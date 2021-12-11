from enum import Enum
from random import randint
from string import ascii_letters
from struct import pack, unpack
import socket
from random import choice

from ..exceptions import *

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

class UDPTracker:
    IDENTIFICATION = 0x41727101980
    BUFFER_SIZE = 2048
    TIMEOUT = 5

    def __init__(self, host, port, info_hash, start_queue, result_queue):
        self.host = host
        self.port = port 
        self.info_hash = info_hash
        self.sock = None
        
        self.start_queue = start_queue
        self.result_queue = result_queue
        self.peers = list()
        self.error = None

    def create_con(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(UDPTracker.TIMEOUT)
        try:
            sock.connect((self.host, self.port))
        except socket.gaierror as e:
            raise UnknownHost("Couldn't resolve host name")
        self.sock = sock
    

    def announce(self):
        peer_id = UDPTracker.gen_pid()
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
        
        try:
            self.create_con()
            cid = self.connect()
            peers = self._announce(cid, self.info_hash, peer_id, downloaded, left, uploaded, event, key, port, ip, num_want)
            self.peers = peers
            self.close_con()
        except Exception as e:
            self.error = str(e)
        
        self.start_queue.get()
        self.result_queue.put(self)
        
    def scrape(self):
        try:
            self.create_con()
            cid = self.connect()
            peers = self._scrape(cid, self.info_hash)
            self.peers = peers
        except Exception as e:
            self.error = str(e)
        
        self.start_queue.get()
        self.result_queue.put(self)
    
    """
    Connect packet:
	32-bit integer	action
	32-bit integer	transaction_id
    64-bit integer	connection_id
    """
    def connect(self):
        TID = self.gen_tid()
        msg = pack('!QII', UDPTracker.IDENTIFICATION, Actions.CONNECT.value, TID)

        try:
            send = self.sock.send(msg)    
        except socket.timeout:
            raise SendTimeout("Sending connect timed out")
        
        try:
            recv = self.sock.recv(UDPTracker.BUFFER_SIZE) 
        except socket.timeout:
            raise ReceiveTimeout("Recieving connect timed out")
        except ConnectionRefusedError:
            raise ConnectionRefused("Connection refused")
        
        if len(recv) < 16:
            print("Error: Announce response smaller than 16 bytes")
            return

        # TODO print error message
        action = unpack('!I', recv[:4])[0]
        if action == Actions.ERROR.value:
            self.error(recv, TID)
            return
        if action != Actions.CONNECT.value:
            print("Error: Action neither connect or error")
            return

        tid = unpack('!I', recv[4:8])[0]
        if tid != TID:
            print("Error: Transaction id aren't equal")
            return
        
        return unpack('!Q', recv[8:16])[0]


    """
    Announce Packet:
    64-bit integer connection_id
    32-bit integer action
    32-bit integer transaction_id
    20-byte string info_hash
    20-byte string peer_id
    64-bit integer downloaded
    64-bit integer left
    64-bit integer uploaded
    32-bit integer event
    32-bit integer IP address
    32-bit integer key
    32-bit integer num_want
    16-bit integer port
    """
    def _announce(self, cid, info_hash, peer_id, dowloaded, left, uploaded, event, key, port, ip=0x0, num_want=-1):
        # create message
        TID = self.gen_tid()
        msg = pack('!QII', cid, Actions.ANNOUNCE.value, TID)
        msg += pack('!20s20sQ', info_hash, peer_id, dowloaded)
        msg += pack('!QQI', left, uploaded, event)
        msg += pack('!IIIH', ip, key, num_want, port)
        
        # send and receive announce packet
        try:
            send = self.sock.send(msg)
        except socket.timeout:
            raise TorrentExceptions("Sending announce timed out")
        
        try:
            recv = self.sock.recv(UDPTracker.BUFFER_SIZE)
        except socket.timeout:
            raise TorrentExceptions("Receiving announce timed out")

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

        # unpack data
        results = []
        count_addr = int((len(recv) - 20) / 6)
        for i in range(count_addr):
            ip = socket.inet_ntoa(recv[20 + i * 6:24 + i * 6])
            tcp_port = unpack('!H', recv[24 + i * 6:26 + i * 6])[0]
            results.append((ip, tcp_port))

        return results


    """
    Scrape packet:
	64-bit integer	connection_id
	32-bit integer	action	
	32-bit integer	transaction_id
	20-byte string	info_hash
    """
    def _scrape(self, cid, info_hashes: list):
        # create message
        TID = self.gen_tid()
        msg = pack('!QII', cid, Actions.SCRAPE.value, TID)
        if type(info_hashes) == list:
            for info_hash in info_hashes:
                msg += pack('!20s', info_hash)
        elif type(info_hashes) == bytes:
            msg += pack('!20s', info_hashes)
            
        # send and receive announce packet
        try:
            send = self.sock.send(msg)
            recv, conn = self.sock.recvfrom(UDPTracker.BUFFER_SIZE)
        except socket.timeout:
            print("Error: Send/Response timed out")
            return None
        
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
    Authenticate packet:
    8-byte zero-padded string	username
	8-byte string	hash

    hash = first 8 bytes of sha1(input + username + sha1(password))
    """
    def authenticate(self, username, password):
        pass

    """
    Error packet:
    32-bit integer	action
	32-bit integer	transaction_id
	string	message
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
    
    
    @staticmethod
    def gen_tid():
        return randint(0, 0xffffffff)
    
    @staticmethod
    def gen_pid():
        return bytes("-qB3090-" + ''.join(choice(ascii_letters) for _ in range(12)), 'utf-8')
    
    def close_con(self):
        self.sock.close()
        self.sock = None