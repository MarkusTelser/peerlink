from struct import unpack
from peer_protocol.PeerMessages import *
import sys
import traceback

BUFFER_SIZE = 10000

class PeerStreamIterator(PeerMessages):
    def __init__(self):
        super().__init__()
        self.data = b''
    
    def recv(self, socket):
        while True:
            try:
                recv = socket.recv(BUFFER_SIZE)
                self.data += recv
                parsed = self.parse()
                if parsed != None:
                    return parsed
            except Exception as e:
                print("tr", traceback.print_exc(e))
                print("Error: here", e.message)
                break
    
    def parse(self):
        HEADER_LENGTH = 4

        if len(self.data) > HEADER_LENGTH:
            length = unpack("!I", self.data[:4])[0]
            if length == 0:
                self.data = self.data[HEADER_LENGTH:]
                return PeerMessageStructures.KeepAlive
            
            print(self.data)
            if len(self.data) >= length + HEADER_LENGTH:
                mid = unpack("!B", self.data[4:5])[0]

                if 0 <= mid <= 9:
                    ret = None
                    msg = self.data[:HEADER_LENGTH + length]

                    if mid == 0:
                        ret = PeerMessageStructures.Choke
                    elif mid == 1:
                        ret = PeerMessageStructures.Unchoke
                    elif mid == 2:
                        ret = PeerMessageStructures.Interested
                    elif mid == 3:
                        ret = PeerMessageStructures.NotInterested
                    elif mid == 4:
                        ret = PeerMessages.val_have(msg)
                    elif mid == 5:
                        ret = PeerMessages.val_bitfield(msg)
                    elif mid == 6:
                        ret = PeerMessages.val_request(msg)
                    elif mid == 7:
                        len(msg)
                        ret = PeerMessages.val_piece(msg)
                    elif mid == 8:
                        ret = PeerMessages.val_cancel(msg)
                    elif mid == 9:
                        ret = PeerMessages.val_port(msg)
                    
                    # clean up data and return parsed data
                    self.data = self.data[HEADER_LENGTH + length:]
                    print(self.data)
                    return ret
                else:
                    raise Exception("Error: Unknown message id", mid)
            else:
                print("Info: don't have all parts of message")
        else:
            print("Info: message too small")
        return None
