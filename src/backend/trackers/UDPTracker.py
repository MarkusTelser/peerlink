import socket
from time import time
from enum import Enum
from random import choice
from random import randint
from string import ascii_letters
from struct import pack, unpack
from ipaddress import IPv6Address, ip_address

from src.backend.exceptions import *
from src.backend.peer_protocol.PeerIDs import PeerIDs

class Actions(Enum):
    CONNECT = 0x0
    ANNOUNCE = 0x1
    SCRAPE = 0x2
    ERROR = 0x3

class UDPEvents(Enum):
    NONE = 0x0
    COMPLETED = 0x1
    STARTED = 0x2
    STOPPED = 0x3

class TrackerStatus(Enum):
    NOCONTACT = 0
    CONNECTING = 1
    FINISHED = 2
    ERROR = 3

# UDP Tracker Extension (BEP 41)
class UDPExtensionTypes(Enum):
    EndOfOptions = 0x0
    NOP = 0x1
    URLData = 0x2

class UDPTracker:
    IDENTIFICATION = 0x41727101980
    MAX_TIMEOUT_CYCLES = 8
    CID_EXPIRY_TIME = 60
    BUFFER_SIZE = 2048
    TIMEOUT = 5

    def __init__(self, address, extension, info_hash, semaphore, result_queue):
        self.address = address
        self.extension = extension
        self.info_hash = info_hash
        self.sock = None
        
        self.semaphore = semaphore
        self.result_queue = result_queue
        
        self.peers = list()
        self.leechers = 0
        self.seeders = 0
        
        
        self.n_cycles = 0
        self.cid_expiry_date = 0
        
        self.status = TrackerStatus.NOCONTACT
        self.error = None

    def _send(self, msg):
        try:
            self.sock.sendall(msg)
        except socket.timeout:
            raise SendTimeout("Sending connect timed out")
        except socket.error as e: # alias of OSError
            raise NetworkExceptions(e)
    
    def _sendrecv(self, msg):
        successful = False
        while self.n_cycles <= UDPTracker.MAX_TIMEOUT_CYCLES and not successful:
            try:
                timeout = 15 * (2 ** self.n_cycles)
                self.sock.settimeout(timeout)
                
                self._send(msg)
                recv = self.sock.recv(UDPTracker.BUFFER_SIZE)
            except ConnectionRefusedError:
                raise ConnectionRefused("Connection refused")
            except socket.timeout:
                #print(f"received timeout after {timeout}s")
                self.n_cycles += 1
            except socket.error as e: # alias of OSError
                raise NetworkExceptions(e)
            else:
                successful = True

        # maximal number of retry cycles exceeded
        if self.n_cycles == UDPTracker.MAX_TIMEOUT_CYCLES + 1:
            raise ReceiveTimeout(f"timed out after {UDPTracker.MAX_TIMEOUT_CYCLES} retry cycles")
        
        self.n_cycles = 0 # reset timeout cycles to zero
        return recv

    def create_con(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(UDPTracker.TIMEOUT)
        try:
            sock.connect((self.address))
        except socket.gaierror as e:
            raise UnknownHost("Couldn't resolve host name")
        self.sock = sock
        
    def close_con(self):
        self.sock.close()
        self.sock = None
    
    def announce(self):
        peer_id = bytes(PeerIDs.generate_key(), 'utf-8')
        event = UDPEvents.STARTED.value

        # demo values
        downloaded = 0
        left = 0
        uploaded = 0
        num_want = 500

        # if not given
        ip = 0
        port = 0
        key = 0
        
        with self.semaphore:
            try:
                self.status = TrackerStatus.CONNECTING
                self.create_con()
                peers = self._announce(self.info_hash, peer_id, downloaded, left, uploaded, event, key, port, ip, num_want, self.extension)
                self.peers = peers
            except Exception as e:
                self.error = str(e)
                self.status = TrackerStatus.ERROR
            finally:
                if self.sock is not None:
                    self.close_con()
                self.result_queue.put(self)
                if not self.error:
                    self.status = TrackerStatus.FINISHED
            
        
    def scrape(self):
        with self.semaphore:
            try:
                self.create_con()
                peers = self._scrape(self.info_hash)
                self.peers = peers
            except Exception as e:
                self.error = str(e)
            finally:
                if self.sock is not None:
                    self.close_con()
                self.result_queue.put(self)
    
    """
    Connect request:
	32-bit integer	action // = 0x41727101980
	32-bit integer	transaction_id // = 0 (CONNECT)
    64-bit integer	connection_id
    
    Connect response:
    32-bit integer action // = 0 (CONNECT)
    32-bit integer transaction_id
    64-bit integer connection_id
    """
    def connect(self):
        TID = self.gen_tid()
        msg = pack('!QII', UDPTracker.IDENTIFICATION, Actions.CONNECT.value, TID)

        # send and receive connect packet
        recv = self._sendrecv(msg)
        
        if len(recv) < 16:
            raise WrongFormat("Announce response smaller than 16 bytes")

        action = unpack('!I', recv[:4])[0]
        if action == Actions.ERROR.value:
            self.error(recv, TID)
            return
        
        if action != Actions.CONNECT.value:
            raise WrongFormat("Action neither connect or error")

        tid = unpack('!I', recv[4:8])[0]
        if tid != TID:
            raise WrongFormat("Transaction id aren't equal")
        
        cid = unpack('!Q', recv[8:16])[0]
        
        # set expiry time until which this cid is valid
        self.cid_expiry_date = time() + UDPTracker.CID_EXPIRY_TIME
        
        return cid

    """
    Announce request:
    64-bit integer connection_id
    32-bit integer action // = 1 (ANNOUNCE)
    32-bit integer transaction_id
    20-byte string info_hash
    20-byte string peer_id
    64-bit integer downloaded
    64-bit integer left
    64-bit integer uploaded
    32-bit integer event // 0 = None
    32-bit integer IP address // 0 = DEFAULT
    32-bit integer key
    32-bit integer num_want // -1 = DEFAULT
    16-bit integer port
    
    Announce response:
    32-bit integer action // = 1 (ANNOUNCE)
    32-bit integer transaction_id
    32-bit integer interval
    32-bit integer leechers
    32-bit integer seeders
    32-bit integer IP address
    16-bit integer TCP port
    """
    def _announce(self, info_hash, peer_id, dowloaded, left, uploaded, event, key, port, ip=0, num_want=-1, extensions=""):
        # update cid if expired / not existing
        if time() > self.cid_expiry_date:
            cid = self.connect()
        
        # create message
        TID = self.gen_tid()
        
        # don't insert ip, if it is ipv6 address (128bit instead of 32bit)
        if ip != 0 and type(ip_address(ip)) == IPv6Address:
            ip = 0
        
        msg = pack('!QII', cid, Actions.ANNOUNCE.value, TID)
        msg += pack('!20s20sQ', info_hash, peer_id, dowloaded)
        msg += pack('!QQI', left, uploaded, event)
        msg += pack('!IIIH', ip, key, num_want, port)
        
        # add extension bytes, even if there is none
        msg += self.encodeExt(extensions)
        
        # send and receive announce packet
        recv = self._sendrecv(msg)

        if len(recv) < 20:
            print("Error: Announce response smaller than 20 bytes")
            return None
        
        # TODO print error message
        action = unpack('!I', recv[:4])[0]
        if action == Actions.ERROR.value:
            self.error(recv, TID)
            return None
        if action != Actions.ANNOUNCE.value:
            print(action)
            print("Error: Action is neither announce or error")
            return None
        
        tid = unpack('!I', recv[4:8])[0]
        if tid != TID:
            print("Error: Not the same transaction ID")
            return None

        interval, leechers, seeders = unpack('!III', recv[8:20])
        self.leechers = leechers
        self.seeders = seeders
        
        # unpack data
        results = []
        count_addr = int((len(recv) - 20) / 6)
        for i in range(count_addr):
            ip = socket.inet_ntoa(recv[20 + i * 6:24 + i * 6])
            tcp_port = unpack('!H', recv[24 + i * 6:26 + i * 6])[0]
            results.append((ip, tcp_port))

        return results


    """
    Scrape request:
	64-bit integer	connection_id
	32-bit integer	action // = 2 (SCRAPE)
	32-bit integer	transaction_id
	20-byte string	info_hash
 
    Scrape response:
    32-bit integer action // = 2 (SCRAPE)
    32-bit integer transaction_id
    32-bit integer seeders
    32-bit integer completed
    32-bit integer leechers
    """
    def _scrape(self, info_hashes: list):
        # update cid if expired / not existing
        if time() > self.cid_expiry_date:
            cid = self.connect()
        
        # create message
        TID = self.gen_tid()
        msg = pack('!QII', cid, Actions.SCRAPE.value, TID)
        
        if type(info_hashes) == list:
            for info_hash in info_hashes:
                # up to 74 torrents scraped at once
                msg += pack('!20s', info_hash[:74])
        elif type(info_hashes) == bytes:
            msg += pack('!20s', info_hashes)
            
        # send and receive scrape packet
        recv = self._sendrecv(msg)
        
        if len(recv) < 8:
            print("Error: Scrape response smaller than 8 bytes")
            return None
        
        # TODO print error message
        action = unpack('!I', recv[:4])[0]
        if action == Actions.ERROR.value:
            self.error(recv, TID)
            return None
        if action != Actions.SCRAPE.value:
            print("Error: Action is neither scrape or error")
            return None
        
        tid = unpack("!I", recv[4:8])[0]
        if tid != TID:
            print("Error: Not the same transaction ID")
            return None

        # unpack data
        results = []
        count_addr = int((len(recv) - 8) / 12)
        for i in range(count_addr):
            seeders = unpack('!I', recv[8 + i * 12:12 + i * 12])[0]
            completed = unpack('!I', recv[12 + i * 12:16 + i * 12])[0]
            leecher = unpack('!I', recv[16 + i * 12:20 + i * 12])[0]
            results.append((seeders, completed, leecher))
        
        print(results)
        return results

    """
    Error response:
    32-bit integer action // = 3 (ERROR)
	32-bit integer transaction_id
	string message
    """
    def error(self, data, tid):
        if len(data) < 8:
            print("Error: Error response smaller than 8 bytes")
            return None

        action = unpack("!I", data[:4])[0]
        if action != Actions.ERROR.value:
            print("Error: Action is not error")
            return None
        print("Error: Action is error")

        TID = unpack("!I", data[4:8])[0]
        if TID != tid:
            print("Error: Transaction IDs don't match")
            return None

        if len(data) > 8:
            print("Error message:", data[8:len(data)])
    
    """
    Option Types: 
    EndOfOptions <type=0x0> (is equal to no more bytes)
    NOP <type=0x1> (used for padding, has no effect)
    URLData <type=0x2><len_data><data>
    
    Extension Format:
    1 byte option-type
    1 byte length of data
    n bytes length data field
    """
    def encodeExt(self, url_string: str):
        ret = bytes()
        
        url_len = len(url_string)
        ret += pack("!B", UDPExtensionTypes.URLData.value) # type
        ret += pack("!B", len(url_string)) # length 
        if url_len != 0:
            ret += pack(f"!{url_len}s", bytes(url_string, 'utf-8')) # data
        
        return ret
    
    @staticmethod
    def gen_tid():
        return randint(0, 0xffffffff)