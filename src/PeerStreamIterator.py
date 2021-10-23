from struct import unpack
from typing import NamedTuple
from collections import namedtuple

class PeerMessages:
    KeepAlive = namedtuple('KeepAlive', '')
    Choke = namedtuple('Choke', '')
    Unchoke = namedtuple('Unchoke', '')
    Interested = namedtuple('Interested', '')
    NotInterested = namedtuple('NotInterested', '')
    Have = namedtuple('Have', 'piece_index')
    Bitfield = namedtuple('Bitfield', 'bitfield')
    Request = namedtuple('Request', 'index begin length')
    Piece = namedtuple('Piece', 'index begin block')
    Cancel = namedtuple('Cancel', 'index begin length')
    Port = namedtuple('Port', 'listen_port')


class PeerStreamIterator:
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
                return PeerMessages.KeepAlive
            
            if len(self.data) >= length + HEADER_LENGTH:
                id == unpack("!B", self.data[4:5])[0]

                if 0 <= id <= 9:
                    data = ""

                    if id == 0:
                        return PeerMessages.Choke
                    elif id == 1:
                        return PeerMessages.Unchoke
                    elif id == 2:
                        return PeerMessages.Interested
                    elif id == 3:
                        return PeerMessages.NotInterested
                    elif id == 4:
                        pass
                    elif id == 5:
                        pass
                    elif id == 6:
                        pass
                    elif id == 7:
                        pass
                    elif id == 8:
                        pass
                    elif id == 9:
                        pass
                    
                    # clean up data and return parsed data 
                    self.data = self.data[HEADER_LENGTH + length:]
                    return data
                else:
                    raise Exception("Error: Unknown message id", id)
            else:
                print("Info: don't have all parts of message")
        else:
            print("Info: message too small")
        return None
