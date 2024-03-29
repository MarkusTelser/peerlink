from enum import Enum
from math import ceil
from threading import RLock
from random import randint
from dataclasses import dataclass
import time

class DownloadStrategy(Enum):
    RARESTFIRST = 0
    SEQUENTIAL = 1
    RANDOM = 2
    
    
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
    def __init__(self, piece_count, piece_size, cb, download_strategy=DownloadStrategy.RARESTFIRST):
        self.piece_count = piece_count
        self.piece_size = piece_size
        self._done_callback = cb
        self.download_strategy = download_strategy
        self.pieces = list()
    
    @property
    def finished_pieces(self):
        return len([x for x in self.pieces if x.status == 'FINISHED'])

    @property
    def downloaded_percent(self):
        return round(self.finished_pieces / self.piece_count * 100, 2)
    
    @property
    def downloaded_bytes(self):
        return self.finished_pieces * self.piece_size

    @property
    def left_bytes(self): 
        return (self.piece_count - self.finished_pieces) * self.piece_size
    
    @property
    def health(self):
        have_count = len([x for x in self.pieces if x.count_peers > 0])
        return int(have_count / self.piece_count * 100)
    
    @property
    def availability(self):
        full_availability = min([x.count_peers for x in self.pieces], default=-1)
        count_lowest = len([x for x in self.pieces if x.count_peers == full_availability])
        part_availability = (self.piece_count - count_lowest) / self.piece_count 
        return round(full_availability + part_availability, 2)
    
    @property
    def uploaded_bytes(self):
        return 0
    
    def get_piece(self):
        # TODO with peer_id afterwards
        
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
        else:
            # enter SUPERSEEDING mode
            inuse_pieces = [x for x in self.pieces if x.status == 'STARTED']
            if len(inuse_pieces) > 0:
                r = randint(0, len(inuse_pieces) - 1)
                return inuse_pieces[r].index
            return None    
    
    def get_entirety(self, peer_id):
        count = 0
        for piece in self.pieces:
            if peer_id in piece.have_peers:
                count += 1
        return round(count / self.piece_count * 100, 2)

    def add_bitfield(self, peer_id, bitfield):
        # check if size is correct, account for extra bits at the end
        print(len(bitfield), ceil(self.piece_count / 8))
        if len(bitfield) != ceil(self.piece_count / 8):
            raise Exception("bitfield wrong size")
        
        print('before adding  bitfield')
        t = time.time()
        for i, byte in enumerate(bitfield):
            bits = '{0:08b}'.format(byte)
            for j, bit in enumerate(bits):
                if int(bit):
                    index = i * 8 + j
                    if index >= self.piece_count:
                        return
                    self.add_piece(peer_id, index)
        print('after adding  bitfield', time.time() - t, peer_id)

    def add_piece(self, peer_id, index):
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
        used_pieces = [x for x in self.pieces if x.status == 'STARTED']
        for piece in used_pieces:
            if piece.index == index:
                piece.status = 'FINISHED'
                if self.left_bytes == 0:
                    print('FINISHEEEEEEd')
                    self._done_callback()
                return
        
        # raise Exception('piece already downloaded')
    
    def reject_piece(self, index):
        used_pieces = [x for x in self.pieces if x.status == 'STARTED']
        for piece in used_pieces:
            if piece.index == index:
                piece.status = 'PENDING'
                return

        raise Exception('piece already rejected')
    
    def set_strategy(self, strategy: DownloadStrategy | int):
        if type(strategy) == DownloadStrategy:
            self.download_strategy = strategy
        elif 0 <= strategy < 3:
            print('---' * 100)
            
            self.download_strategy = DownloadStrategy(strategy)
            print(strategy, self.download_strategy)
        else:
            # TODO LOG warnings invalid strategy
            pass

    def is_last_piece(self, index):
        return index == self.piece_count - 1