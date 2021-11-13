import socket
from struct import unpack
from peer_protocol.PeerMessages import PeerMessageLengths, PeerMessageStructures
from peer_protocol.PeerStreamIterator import PeerStreamIterator
from threading import Thread

"""
implement peer protocol
"""
class Peer(PeerStreamIterator):
    TIMEOUT = 10

    def __init__(self, address, info_hash, peer_id):
        super().__init__()
        self.sock = None
        self.address = address #  => (ip, port)
        self.info_hash = info_hash
        self.peer_id = peer_id

        # TODO implement after right
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False

    def main(self):
        self.create_con()
        
        # send and receive handshake
        msg = self.bld_handshake(self.info_hash, self.peer_id)
        self.send_msg(msg, expected_len=68)
        self.recv_handshake(self.info_hash, self.peer_id)

        listen_thread = Thread(target=self.recv_msg)
        send_thread = Thread(target=self.send)

        # TODO thread listen on socket
        # TODO thread gets requests from piece manager
      
    def create_con(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.TIMEOUT)
        self.sock = sock
        self.sock.connect(self.address)
    
    def send(self):
        pass

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
        recv = self.recv(self.sock)

        if isinstance(recv, PeerMessageStructures.Choke):
            self.am_choking = True
        elif isinstance(recv, PeerMessageStructures.Unchoke):
            self.am_choking = False
        elif isinstance(recv, PeerMessageStructures.Interested):
            self.am_interested = True
        elif isinstance(recv, PeerMessageStructures.NotInterested):
            self.am_interested = False
        
        if isinstance(recv, PeerMessageStructures.Have):
            pass
        elif isinstance(recv, PeerMessageStructures.Bitfield):
            pass
        elif isinstance(recv, PeerMessageStructures.Request):
            # TODO implement with seeding
            pass
        elif isinstance(recv, PeerMessageStructures.Piece):
            pass
        elif isinstance(recv, PeerMessageStructures.Cancel):
            # TODO implement with EndGame Strategy
            pass
        elif isinstance(recv, PeerMessageStructures.Port):
            # TODO implement with DHT
            pass
        

    def close_con(self):
        self.sock.close()