import logging
import socket
import asyncio
from time import time
from enum import Enum
from random import randint
from struct import pack, unpack
from ipaddress import IPv6Address, ip_address

from src.backend.exceptions import *
from src.backend.peer_protocol.PeerIDs import PeerIDs
from src.backend.trackers.HTTPTracker import HTTPEvents

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

# UDP Tracker Extension (BEP 41)
class UDPExtensionTypes(Enum):
    EndOfOptions = 0x0
    NOP = 0x1
    URLData = 0x2

class TrackerStatus(Enum):
    NOCONTACT = 0
    CONNECTING = 1
    FINISHED = 2
    ERROR = 3

class UDPTracker:
    IDENTIFICATION = 0x41727101980
    MAX_TIMEOUT_CYCLES = 8
    CID_EXPIRY_TIME = 60
    BUFFER_SIZE = 2048
    TIMEOUT = 5

    def __init__(self, address, extension, info_hash, peer_id, port, semaphore):
        self.address = address
        self.extension = extension
        self.info_hash = info_hash
        self.peer_id = bytes(peer_id, 'utf-8')
        self.port = port
        self.sock = None
        
        self.semaphore = semaphore
        
        self.peers = list()
        self.interval = 0
        self.leechers = 0
        self.seeders = 0
        
        self.n_cycles = 0
        self.cid_expiry_date = 0
        
        self.status = TrackerStatus.NOCONTACT
        self.announce_task = None
        self.scrape_task = None
        self.error = None

    async def _send(self, msg):
        try:
            loop = asyncio.get_running_loop()
            co = loop.sock_sendall(self.sock, msg)
            await asyncio.wait_for(co, timeout=UDPTracker.TIMEOUT)
        except asyncio.TimeoutError:
            raise SendTimeout("Sending connect timed out")
        except socket.error as e: # alias of OSError
            raise NetworkExceptions(e)
        except Exception as e:
            print('other ', e)
    
    async def _sendrecv(self, msg):
        successful = False
        while self.n_cycles <= UDPTracker.MAX_TIMEOUT_CYCLES and not successful:
            try:
                await self._send(msg)
                loop = asyncio.get_running_loop()
                timeout = 15 * (2 ** self.n_cycles)
                co = loop.sock_recv(self.sock, UDPTracker.BUFFER_SIZE)
                recv = await asyncio.wait_for(co, timeout=timeout)
            except ConnectionRefusedError:
                raise ConnectionRefused("Connection refused")
            except asyncio.TimeoutError:
                print(f"received timeout after {timeout}s")
                self.n_cycles += 1
            except socket.error as e: # alias of OSError
                print('otherwise')
                raise NetworkExceptions(e)
            else:
                successful = True

        # maximal number of retry cycles exceeded
        if self.n_cycles == UDPTracker.MAX_TIMEOUT_CYCLES + 1:
            raise ReceiveTimeout(f"timed out after {UDPTracker.MAX_TIMEOUT_CYCLES} retry cycles")
        
        self.n_cycles = 0 # reset timeout cycles to zero
        return recv

    async def create_con(self):
        loop = asyncio.get_running_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(UDPTracker.TIMEOUT)
        sock.setblocking(False)
        try:
            await loop.sock_connect(sock, (self.address))
            self.sock = sock
        except socket.gaierror as e:
            raise UnknownHost("Couldn't resolve host name")
        
    def close_con(self):
        self.sock.close()
        self.sock = None
       
    def announce_wrap(self, func, name='', callback=None):
        self.announce_task = asyncio.create_task(func)
        self.announce_task.add_done_callback(callback)
        self.announce_task.set_name(name)
    
    def scrape_wrap(self, func, name='', callback=None):
        self.scrape_task = asyncio.create_task(func)
        self.scrape_task.add_done_callback(callback)
        self.scrape_task.set_name(name)
    
    def pause(self):
        if self.announce_task != None:
            self.announce_task.cancel()
        if self.scrape_task != None:
            self.scrape_task.cancel()
    
    async def announce(self, event, uploaded, downloaded, left):
        # translate HTTP Events to UDP Events
        if event == HTTPEvents.STARTED:
            event = UDPEvents.STARTED.value
        elif event == HTTPEvents.STOPPED:
            event = UDPEvents.STOPPED.value
        elif event == HTTPEvents.COMPLETED:
            event = UDPEvents.COMPLETED.value
        else:
            event = UDPEvents.NONE.value

        # if not given
        ip = 0
        key = PeerIDs.generate_ikey()
        num_want = 200
        
        async with self.semaphore:
            peers = None
            try:
                self.status = TrackerStatus.CONNECTING
                await self.create_con()
                peers = await self._announce(self.info_hash, self.peer_id, int(uploaded), int(downloaded), int(left), event, key, self.port, ip, num_want, self.extension)
                self.peers = peers
            except Exception as e:
                self.error = str(e)
                self.status = TrackerStatus.ERROR
            finally:
                if self.sock  is not None:
                    self.close_con()
                if not self.error:
                    self.status = TrackerStatus.FINISHED
                return peers
            
        
    async def scrape(self):
        async with self.semaphore:
            peers = None
            try:
                await self.create_con()
                peers = await self._scrape(self.info_hash)
                self.peers = peers
            except Exception as e:
                #logging.exception('t')
                self.error = str(e)
            finally:
                if self.sock is not None:
                    self.close_con()
                return peers
    
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
    async def connect(self):
        TID = self.gen_tid()
        msg = pack('!QII', UDPTracker.IDENTIFICATION, Actions.CONNECT.value, TID)

        # send and receive connect packet
        recv = await self._sendrecv(msg)
        
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
    async def _announce(self, info_hash, peer_id, uploaded, downloaded, left, event, key, port, ip=0, num_want=-1, extensions=""):
        # update cid if expired / not existing
        if time() > self.cid_expiry_date:
            cid = await self.connect()
        
        # create message
        TID = self.gen_tid()
        
        # don't insert ip, if it is ipv6 address (128bit instead of 32bit)
        if ip != 0 and type(ip_address(ip)) == IPv6Address:
            ip = 0
        
        msg = pack('!QII', cid, Actions.ANNOUNCE.value, TID)
        msg += pack('!20s20sQ', info_hash, peer_id, downloaded)
        msg += pack('!QQI', left, uploaded, event)
        msg += pack('!IIIH', ip, key, num_want, port)
        
        # add extension bytes, even if there is none
        msg += self.encodeExt(extensions)
        
        # send and receive announce packet
        recv = await self._sendrecv(msg)

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
        self.interval = interval
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
    async def _scrape(self, info_hashes: list):
        # update cid if expired / not existing
        if time() > self.cid_expiry_date:
            print('need to connect')
            cid = await self.connect()
        
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
        recv = await self._sendrecv(msg)
        
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