from socket import socket, AF_INET, SOCK_STREAM
from struct import pack, unpack
from peer_struct import PeerStruct, PeerMessage

class Peer(PeerStruct):
    TIMEOUT = 3
    BUFFER_SIZE = 1024

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
            
    def recv(self):
        try:
            print("listen on socket")
            recv = self.sock.recv(Peer.BUFFER_SIZE) 
            print(recv)
        except socket.timeout:
            #print("Error: Send/Response timed out")
            self.sock.close()
            return
        except Exception as e:
            print(e)
            self.sock.close()
            return

        if len(recv) < 4:
            print("Error: Peer message too small")
            return False
        elif len(recv) == 4:
            return self.val_keep_alive(recv)
        
        id = unpack("!B", recv[4:5])[0]

        if id == PeerMessage.CHOKE:
            pass
        elif id == PeerMessage.UNCHOKE:
            pass
        elif id == PeerMessage.INTERESTED:
            pass
        elif id == PeerMessage.NOTINTERESTED:
            pass
        elif id == PeerMessage.HAVE:
            pass
        elif id == PeerMessage.BITFIELD:
            return self.(recv)
        elif id == PeerMessage.REQUEST:
            pass
        elif id == PeerMessage.PIECE:
            pass
        elif id == PeerMessage.CANCEL:
            pass
        elif id == PeerMessage.PORT:
            pass
        else:
            print("Error: Message id unknown")
            return None

    def create_con(self):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(Peer.TIMEOUT)
        self.sock = sock

        print(self.ip, self.port)
        self.sock.connect((self.ip, self.port))
    
    def close_con(self):
        self.sock.close()