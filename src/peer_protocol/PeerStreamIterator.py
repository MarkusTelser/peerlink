from struct import unpack
from peer_protocol.Peer import Peer
from peer_protocol.PeerMessages import *

class PeerStreamIterator(PeerMessages):
    def __init__(self):
        self.data = b''

    def main():
        pass

    def parse(self):
        HEADER_LENGTH = 4
        if len(self.data) > HEADER_LENGTH:
            length = unpack("!I", self.data[:4])[0]
            if length == 0:
                self.data = self.data[HEADER_LENGTH:]
                return PeerMessageStructures.KeepAlive
            
            if len(self.data) >= length + HEADER_LENGTH:
                id == unpack("!B", self.data[4:5])[0]

                if 0 <= id <= 9:
                    ret = None

                    if id == 0:
                        ret = PeerMessageStructures.Choke
                    elif id == 1:
                        ret =  PeerMessageStructures.Unchoke
                    elif id == 2:
                        ret = PeerMessageStructures.Interested
                    elif id == 3:
                        ret =  PeerMessageStructures.NotInterested
                    elif id == 4:
                        ret =  PeerMessages.val_have()
                    elif id == 5:
                        ret =  PeerMessages.val_bitfield()
                    elif id == 6:
                        ret =  PeerMessages.val_request()
                    elif id == 7:
                        ret =  PeerMessages.val_piece()
                    elif id == 8:
                        ret =  PeerMessages.val_cancel()
                    elif id == 9:
                        ret =  PeerMessages.val_port()
                    
                    # clean up data and return parsed data 
                    self.data = self.data[HEADER_LENGTH + length:]
                    return ret
                else:
                    raise Exception("Error: Unknown message id", id)
            else:
                print("Info: don't have all parts of message")
        else:
            print("Info: message too small")
        return None
