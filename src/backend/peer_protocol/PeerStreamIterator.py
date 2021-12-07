from struct import unpack
from .PeerMessages import *
from ..exceptions import *
import traceback

BUFFER_SIZE = 10000

class PeerStreamIterator(PeerMessages):
    def __init__(self, socket):
        super().__init__()
        self.socket = socket
        self.data = b''
    
    def recv(self):
        while True:
            try:
                recv = self.socket.recv(BUFFER_SIZE)
                self.data += recv
                parsed = self.parse()
                if parsed != None:
                    return parsed
            except Exception as e:
                print(e)
                return None
    
    def parse(self):
        HEADER_LENGTH = 4

        if len(self.data) > HEADER_LENGTH:
            length = unpack("!I", self.data[:4])[0]
            if length == 0:
                self.data = self.data[HEADER_LENGTH:]
                return None
            
            if len(self.data) >= length + HEADER_LENGTH:
                mid = unpack("!B", self.data[4:5])[0]

                if 0 <= mid <= 9:
                    ret = None
                    msg = self.data[:HEADER_LENGTH + length]

                    if mid == 0:
                        ret = PeerMessageStructures.Choke()
                    elif mid == 1:
                        ret = PeerMessageStructures.Unchoke()
                    elif mid == 2:
                        ret = PeerMessageStructures.Interested()
                    elif mid == 3:
                        ret = PeerMessageStructures.NotInterested()
                    elif mid == 4:
                        ret = self.val_have(msg)
                    elif mid == 5:
                        ret = self.val_bitfield(msg)
                    elif mid == 6:
                        ret = self.val_request(msg)
                    elif mid == 7:
                        ret = self.val_piece(msg)
                    elif mid == 8:
                        ret = self.val_cancel(msg)
                    elif mid == 9:
                        ret = self.val_port(msg)
                    
                    # clean up data and return parsed data
                    self.data = self.data[HEADER_LENGTH + length:]
                    return ret
                else:
                    raise MessageExceptions("Unknown message id", mid)
            else:
                pass
                #print("Info: don't have all parts of message")
        else:
            pass
            #print("Info: message too small")
        return None
