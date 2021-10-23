import socket
from struct import unpack
from peer_protocol.peer_struct import PeerStruct, PeerMessage

class Peer(PeerStruct):
    TIMEOUT = 3
    BUFFER_SIZE = 10240

    def __init__(self, ip, port):
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
        sock.settimeout(Peer.TIMEOUT)
        self.sock = sock
        self.sock.connect((self.ip, self.port))
    
    def close_con(self):
        self.sock.close()
    
    def recv(self):
        try:
            recv = self.sock.recv(Peer.BUFFER_SIZE) 
        except socket.timeout:
            #self.sock.close()
            raise Exception("Error: Listening timed out")
        except Exception as e:
            print(e)
            #self.sock.close()
            return

        if len(recv) < 4:
            raise Exception("Error: Peer message too small",len(recv),recv)
        elif len(recv) == 4:
            return self.val_keep_alive(recv)
        
        id = unpack("!B", recv[4:5])[0]

        if id == PeerMessage.CHOKE.value:
            pass
        elif id == PeerMessage.UNCHOKE.value:
            pass
        elif id == PeerMessage.INTERESTED.value:
            print("remote peer sends interested")
            print(self.val_interested(recv))
        elif id == PeerMessage.NOTINTERESTED.value:
            print("remote peer uninterested")
            print(self.val_not_interested(recv))
        elif id == PeerMessage.HAVE.value:
            pass
        elif id == PeerMessage.BITFIELD.value:
            print("received bitfield")
            print(unpack("!I", recv[0:4]))
            self.val_bitfield(recv)
            return recv
        elif id == PeerMessage.REQUEST.value:
            pass
        elif id == PeerMessage.PIECE.value:
            pass
        elif id == PeerMessage.CANCEL.value:
            pass
        elif id == PeerMessage.PORT.value:
            pass
        else:
            raise Exception("Error: Message id unknown", id, recv)
        return recv