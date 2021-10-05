from enum import Enum
from random import randint
from struct import pack, unpack
import socket
from os import urandom

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

    def __init__(self, address, port):
        self.ip = address
        self.port = port
        self.sock = None
        
        self.create_con()
        #self.main()

    def main(self):
        self.create_con()
        cid = self.connect()
        self.announce(cid)
        #self.scrape()

    def create_con(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(UDPTracker.TIMEOUT)
        self.sock = sock
    
    def close_con(self):
        self.sock.close()
        self.sock = None

    """
    Connect packet:
	64-bit integer	connection_id
	32-bit integer	action
	32-bit integer	transaction_id
    """
    def connect(self):
        if self.sock == None:
            print("Error: Socket not created")
            return

        TID = self.gen_tid()
        msg = pack('!QII', UDPTracker.IDENTIFICATION, Actions.CONNECT.value, TID)

        try:
            send = self.sock.sendto(msg, (self.ip, self.port))
            recv = self.sock.recv(UDPTracker.BUFFER_SIZE) 
        except socket.timeout:
            print("Error: Send/Response timed out")
            return
                
        if len(recv) < 16:
            print("Error: Announce response smaller than 16 bytes")
            return

        action, tid, cid = unpack('!IIQ', recv)
        # TODO print error message
        if action == Actions.ERROR.value:
            print("Error: Action of announce is error")
            return
        if action != Actions.CONNECT.value:
            print("Error: Action neither connect or error")
            return
        if tid != TID:
            print("Error: Transaction id aren't equal")
            return

        return cid

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
    def announce(self, cid, info_hash, peer_id, dowloaded, left, uploaded, event, key, port, ip=0x0, num_want=-1):
        if self.sock == None:
            print("Error: Socket not created")
            return
        
        # create message
        TID = self.gen_tid()
        msg = pack('!QII', cid, Actions.ANNOUNCE.value, TID)
        msg += pack('!20s20sQ', info_hash, peer_id, dowloaded)
        msg += pack('!QQI', left, uploaded, event)
        msg += pack('!IIIH', ip, key, num_want, port)
        
        # send and receive announce packet
        try:
            print("udp tracker: ", self.ip, self.port)
            send = self.sock.sendto(msg, (self.ip, self.port))
            recv, conn = self.sock.recvfrom(UDPTracker.BUFFER_SIZE)
        except socket.timeout:
            print("Error: Send/Response timed out")
            return None

        if len(recv) < 20:
            print("Error: Announce response smaller than 20 bytes")
            return None

        action, tid, interval, leechers, seeders = unpack('!IIIII', recv[:20])
        print("Interval: ", interval , leechers, seeders)
        
        # TODO print error message
        if action == Actions.ERROR.value:
            print("Error: Action is error")
            return None
        if action != Actions.ANNOUNCE.value:
            print("Error: Action is neither connect or error")
            return None

        if tid != TID:
            print("Error: Not the same transaction ID")
            return None

        # unpack data
        results = []
        count_addr = int((len(recv) - 20) / 6)
        print("this many peers", count_addr, " full size: ", len(recv))
        for i in range(count_addr):
            ip = socket.inet_ntoa(recv[20 + i * 6:24 + i * 6])
            tcp_port = unpack('!H', recv[24 + i * 6:26 + i * 6])[0]
            results.append((ip, tcp_port))
        
        if tid != TID:
            print("Error: Transaction id aren't equal")
            return None
        if action != Actions.ANNOUNCE.value:
            print("Error: Action of announce response is not announce(=1)")
            return None

        print("Interval : ", interval) 
        print(leechers, seeders) 
        print(results)
        return results

    """
    Scrape packet:
	64-bit integer	connection_id
	32-bit integer	action	
	32-bit integer	transaction_id
	20-byte string	info_hash
    """
    def scrape(self, cid):
        pass
    
    """
    Authenticate packet:
    8-byte zero-padded string	username
	8-byte string	hash

    hash = first 8 bytes of sha1(input + username + sha1(password))
    """
    def authenticate(self, username, password):
        pass

    def error():
        pass
    
    @staticmethod
    def gen_tid():
        return randint(0, 0xffffffff)
    
    @staticmethod
    def gen_pid():
        return urandom(20)