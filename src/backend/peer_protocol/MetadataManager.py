
from asyncio import Event
from random import randrange
from hashlib import sha1
from math import ceil

from src.backend.metadata.Bencoder import bdecode

class MetadataManager:
    BLOCK_SIZE = 16384
    PARALLEL_PIECES = 3
    
    def __init__(self, info_hash: str, cb):
        self.info_hash = info_hash
        self.full_size = 0
        self.cb = cb
        self._data = dict()
        self.finished = Event()
        self.oustanding_pieces = list()
        self.requested_pieces = list()
        self.downloaded_pieces = list()
    
    def set_full_size(self, size):
        if self.full_size:
            return
       
        # initialize all pieces possible
        self.full_size = size
        pieces_count = ceil(self.full_size / self.BLOCK_SIZE) 
        self.oustanding_pieces = [x for x in range(pieces_count)]
    
    def request_blocks(self):
        blocks = list()
        if len(self.oustanding_pieces) > 0:
            for _ in range(self.PARALLEL_PIECES):
                if len(self.oustanding_pieces) == 0:
                    break
                item = self.oustanding_pieces.pop()
                blocks.append(item)
                self.requested_pieces.append(item)
        elif len(self.requested_pieces) > 0:
            count = self.PARALLEL_PIECES if len(self.requested_pieces) > self.PARALLEL_PIECES else len(self.requested_pieces)
            for _ in range(count):
                while True:
                    item = self.requested_pieces[randrange(0, len(self.requested_pieces))]
                    if item not in blocks:
                        blocks.append(item)
                        break
        
        return blocks
    
    def finished_block(self, index, data):
        if index in self.requested_pieces:
            self.requested_pieces.remove(index)
            self.downloaded_pieces.append(index)
            self._data[index] = data
        
        if len(self.requested_pieces) == 0 and len(self.oustanding_pieces) == 0 and not self.finished.is_set():
            correct = self._check_hash()
            if correct:
                self.finished.set()
                self.cb()
            return correct
        return False
            
    def _check_hash(self):
        bdata = b'' 
        for i in range(ceil(self.full_size / self.BLOCK_SIZE)):
            bdata += self._data[i]
        
        # hash with sha1 and compare
        hash = sha1(bdata).digest()
        return hash == self.info_hash