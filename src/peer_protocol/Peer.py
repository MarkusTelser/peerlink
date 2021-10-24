import socket
from struct import unpack
from peer_protocol.PeerMessages import PeerMessageLengths
from peer_protocol.PeerStreamIterator import PeerStreamIterator

"""
implement peer protocol
"""
class Peer(PeerStreamIterator):
    def __init__(self, ip, port):
        super().__init__()
        self.sock = None
        self.ip = ip
        self.port = port

        # TODO implement after right
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False

        self.create_con()
      
    def create_con(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = sock
        self.sock.connect((self.ip, self.port))

    def send_msg(self, msg, expected_len=-1):
        try:
            send_len = self.sock.send(msg)
        except Exception as e:
            raise Exception("Error: ", e)
        
        if expected_len != -1 and expected_len != send_len:
            raise Exception("Error: Didn't send everything")

    def recv_handshake(self, info_hash, peer_id):
        try:
            recv = self.sock.recv(PeerMessageLengths.HANDSHAKE)
        except socket.timeout:
            raise Exception("Error: Response timed out")
        except Exception as e:
            print(e)
            return False
        
        if len(recv) != PeerMessageLengths.HANDSHAKE:
            raise Exception("Error: Handshake message has wrong size", len(recv), recv)
        
        recv_info_hash = unpack("!20s", recv[28:48])[0]
        if recv_info_hash != info_hash:
            raise Exception("Error: Received info hash does not match")

        recv_peer_id = unpack("!20s", recv[48:68])[0]
        if recv_peer_id == peer_id:
            raise Exception("Error: Peer didn't return unique peer id")

        return recv_peer_id
    
    def recv_msg(self):
        return self.recv(self.sock)

    def close_con(self):
        self.sock.close()