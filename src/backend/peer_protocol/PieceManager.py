from enum import Enum
from math import ceil
from threading import RLock
from random import randint
from dataclasses import dataclass

class DownloadStrategy(Enum):
    SEQUENTIAL = 0
    RANDOM = 1
    RARESTFIRST = 2
    
@dataclass
class Piece:
    index: int
    count_peers: int
    have_peers: list
    status: str = 'PENDING' # PENDING, STARTED, FINISHED
    
"""
holds the pieces from all peers and how rare they are
when you get one it takes the one it would give you
and then checks if it is in your object, peer_list
"""
class PieceManager:
    def __init__(self, pieces_count, download_strategy=DownloadStrategy.RARESTFIRST):
        self.lock = RLock()
        self.pieces_count = pieces_count
        self.download_strategy = download_strategy
        self.pieces = list()
    
    @property
    def downloaded(self):
        with self.lock:
            finished_pieces = [x for x in self.pieces if x.status == 'FINISHED']
            return round(len(finished_pieces) / self.pieces_count * 100, 2)
    
    @property
    def health(self):
        with self.lock:
            have_count = len([x for x in self.pieces if x.count_peers > 0])
            return int(have_count / self.pieces_count * 100)
    
    @property
    def availability(self):
        with self.lock:
            full_availability = min([x.count_peers for x in self.pieces], default=-1)
            count_lowest = len([x for x in self.pieces if x.count_peers == full_availability])
            part_availability = (self.pieces_count - count_lowest) / self.pieces_count 
            return round(full_availability + part_availability, 2)

    def get_piece(self):
        # TODO with peer_id afterwards
        with self.lock:
            leftover_pieces = [x for x in self.pieces if x.status == 'PENDING']
            if len(leftover_pieces) > 0:
                if self.download_strategy == DownloadStrategy.SEQUENTIAL:
                    sorted(leftover_pieces, key=lambda x: x.index)
                    piece = leftover_pieces[0]
                elif self.download_strategy == DownloadStrategy.RANDOM:
                    rand_id = randint(0, len(leftover_pieces) - 1)
                    piece = leftover_pieces[rand_id]        
                elif self.download_strategy == DownloadStrategy.RARESTFIRST:
                    sorted(leftover_pieces, key=lambda x: x.count_peers)
                    piece = leftover_pieces[0]
                piece.status = 'STARTED'
                return piece.index
            
            # enter SUPERSEEDING mode
            inuse_pieces = [x for x in self.pieces if x.status == 'STARTED']
            if len(inuse_pieces) > 0:
                r = randint(0, len(inuse_pieces) - 1)
                return inuse_pieces[r].index
            
            return None    
            
    def add_bitfield(self, peer_id, bitfield):
        with self.lock:
            # check if size is correct, account for extra bits at the end
            if len(bitfield) != ceil(self.pieces_count / 8):
                raise Exception("bitfield wrong size")

            for i, byte in enumerate(bitfield):
                bits = '{0:08b}'.format(byte)
                for j, bit in enumerate(bits):
                    if int(bit):
                        index = i * 8 + j
                        if index >= self.pieces_count:
                            return
                        self.add_piece(peer_id, index)
    
    def add_piece(self, peer_id, index):
        with self.lock:
            if len(self.pieces) != 0:
                for piece in self.pieces:
                    if piece.index == index:
                        piece.count_peers += 1
                        piece.have_peers.append(peer_id)
                        return
            
            # not already in pieces
            p = Piece(index, 1, [peer_id])
            self.pieces.append(p)
    
    def finished_piece(self, index):
        with self.lock:
            used_pieces = [x for x in self.pieces if x.status == 'STARTED']
            for piece in used_pieces:
                if piece.index == index:
                    piece.status = 'FINISHED'
                    return
            
            # raise Exception('piece already downloaded')
    
    def reject_piece(self, index):
        with self.lock:
            used_pieces = [x for x in self.pieces if x.status == 'STARTED']
            for piece in used_pieces:
                if piece.index == index:
                    piece.status = 'PENDING'
                    return

            raise Exception('piece already rejected')
    
    def is_last_piece(self, index):
        with self.lock:
            return index == self.pieces_count - 1 