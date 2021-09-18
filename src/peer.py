import socket
from struct import pack, unpack

class Peer:
    TIMEOUT = 10
    BUFFER_SIZE = 1024

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    
    def handshake(self, info_hash, peer_id):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(Peer.TIMEOUT)
        
        pstrlen = 19
        pstr = "BitTorrent protocol"
        reserved = 0
        msg = ""
        msg += pack('!I', pstrlen)
        msg += pack(f'!{pstrlen}s', pstr)
        msg += pack('!Q', reserved)
        msg += pack('!20s', info_hash)
        msg += pack('!20s', peer_id)
        
        try:
            send = sock.sendto(msg, (self.ip, self.port))
            recv = sock.recv(Peer.BUFFER_SIZE) 
        except socket.timeout:
            print("Error: Send/Response timed out")
            return

        print()
        
