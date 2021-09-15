from enum import Enum
from random import randint
from struct import pack, unpack
from socket import socket, gethostbyname, AF_INET, SOCK_DGRAM

class Actions(Enum):
    CONNECT = 0
    ANNOUNCE = 1
    SCRAPE = 2
    ERROR = 3

class Events(Enum):
    NONE = 0
    COMPLETED = 1
    STARTED = 2
    STOPPED = 3

class UDPTracker:
    IDENTIFICATION = 0x41727101980
    BUFFER_SIZE = 4096
    TIMEOUT = 10
    
    def __init__(self, address, port):
        self.ip = gethostbyname(address)
        self.port = port
        self.sock = None

        self.main()

    def main(self):
        self.create_con()
        cid = self.connect()
        self.announce(cid)
        #self.scrape()

    def create_con(self):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.settimeout(UDPTracker.TIMEOUT)
        self.sock = sock
    
    @staticmethod
    def create_tid():
        return randint(0, 0xffffffff)

    def connect():
        if self.sock == None:
            print("Error: Socket not created")
            return

        msg = pack('!QII', UDPTracker.IDENTIFICATION, Actions.CONNECT.value, create_tid())
        send = self.sock.sendto(msg, (self.ip, self.port))
        print(len(send))

        recv = self.sock.recv(UDPTracker.BUFFER_SIZE) 
        if len(recv) < 16:
            print("Error: Announce response smaller than 16 bytes")
            return

        action, tid, cid = unpack('!IIQ', recv)
        if action != Actions.CONNECT.value:
            print("Error: Action of announce response is not action(=0)")
            return
        if tid != TID:
            print("Error: Transaction id aren't equal")
            return
    
        print(len(recv))
        print(tid,hex(tid), TID)
        print(action, tid, cid)
        print(recv)
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
    def announce(cid, info_hash, peer_id, dowloaded, left, uploaded, event, key, port, ip=0, num_want=-1):
        if self.sock == None:
            print("Error: Socket not created")
            return
        
        # create message
        msg = pack('!QII', cid, Actions.ANNOUNCE.value, create_tid())
        msg += pack('!20s20sQ', info_hash, peer_id, dowloaded)
        msg += pack('!QQI', left, uploaded, event)
        msg += pack('!IIIQ', ip, key, num_want, port)
        
        # send and receive announce packet
        send = self.sock.sendto(msg, (self.ip, self.port))
        recv = self.sock.recv(UDPTracker.BUFFER_SIZE)
        
        if len(recv) < 20:
            print("Error: Announce response smaller than 20 bytes")
            return

        action, tid, interval, leechers, seeders, ip, tcp_port = unpack('!IIIIIIQ', recv)

        if tid != TID:
            print("Error: Transaction id aren't equal")
            return
        if action != Actions.ANNOUNCE.value:
            print("Error: Action of announce response is not announce(=1)")
            return

        print(interval, leechers, seeders, ip, tcp_port)

    def scrape():
        pass
    
    def authenticate():
        pass

    def error():
        pass

if __name__ == "__main__":
    adr = "tracker.torrent.eu.org"
    port = 451
    UDPTracker(adr, port)
