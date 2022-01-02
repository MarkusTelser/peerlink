from enum import Enum
from math import ceil
from threading import RLock

class DownloadStrategy(Enum):
    SEQUENTIAL = 0
    RANDOM = 1
    RARESTFIRST = 2

class SequentialPieceManager:
    pass

class RandomPieceManager:
    pass

class RarestFirstPieceManager:
    pass

"""
holds the pieces from all peers and how rare they are
when you get one it takes the one it would give you
and then checks if it is in your object, peer_list
"""
class PieceManager:
    def __init__(self, pieces_count):
        self.lock = RLock()
        self.pieces_count = pieces_count
        self.pieces = list() # contains => [piece_id, how_many_peers_have_piece]
        self.used_pieces = list()
    
    def get_piece(self):
        piece = self.pieces[0]
        self.used_pieces.append(piece)
        del self.pieces[0]
        return piece
    
    def add_piece(self, id):
        if len(self.pieces) != 0:
            for piece in self.pieces:
                if piece[0] == id:
                    # increase piece count and add peer list
                    self.lock.acquire()
                    piece[1] += 1
                    self.lock.release()
                    return
        
        # not already in pieces
        self.lock.acquire()
        piece = [id, 1]
        self.pieces.append(piece)
        self.lock.release()

    def add_bitfield(self, bitfield):
        # check if size is correct, account for extra bits at the end
        if len(bitfield) != ceil(self.pieces_count / 8):
            print("bitfield wrong size")
            return 

        for i, byte in enumerate(bitfield):
            bits = '{0:08b}'.format(byte)
            for j, bit in enumerate(bits):
                if int(bit):
                    id = i * 8 + j
                    if id >= self.pieces_count:
                        return
                    self.add_piece(id)

    def sort_rarest(self):
        self.pieces.sort(key=lambda x: x[1])
