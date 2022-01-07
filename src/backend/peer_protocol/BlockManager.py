from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from math import ceil

@dataclass
class Request:
    piece_id: int
    block_id: int
    startbit: int
    length: int
    timeout: datetime = 0

@dataclass
class Piece:
    piece_id: int
    missing_pieces: list
    started: datetime
    piece_data: dict = field(default_factory=dict)

class BlockManager:
    BLOCK_TIMEOUT = 10
    BLOCK_SIZE = 2 ** 14
    MAX_REQUESTS = 5
    
    def __init__(self, piece_manager, piece_size, full_size):
        self.piece_manager = piece_manager
        self.piece_size = piece_size
        self.full_size = full_size
        
        self.pieces = list()
        self.requests = list()
        self.outstanding = list()
        
    def fill_request(self):
        if len(self.requests) < self.MAX_REQUESTS:
            missing = self.MAX_REQUESTS - len(self.requests)
            while len(self.outstanding) < missing:
                self._get_blocks()
            
            requests = self.outstanding[:missing]
            for request in requests:
                request.timeout = datetime.now() + timedelta(seconds=self.BLOCK_TIMEOUT)
            self.requests.extend(requests)
            self.outstanding = self.outstanding[missing:]
            return requests
        return []
    
    # return if full piece is downloaded
    def add_block(self, piece_id, startbit, data):
        finished_piece = True
        for request in self.requests:
            if request.piece_id == piece_id and request.startbit == startbit:
                self.requests.remove(request)
                if request.piece_id in [x.piece_id for x in self.requests]:
                    finished_piece = False
                elif request.piece_id in [x.piece_id for x in self.outstanding]:
                    finished_piece = False
        
        # remove block from missing pieces of self.pieces and add block data
        for piece in self.pieces:
            if piece.piece_id == piece_id:
                block_id = int(startbit / self.BLOCK_SIZE)
                if block_id in piece.missing_pieces:
                    piece.missing_pieces.remove(block_id)
                    piece.piece_data[block_id] = data
        return finished_piece
    
    def get_piece_data(self, index):
        data = None
        for piece in self.pieces:
            if piece.piece_id == index:
                if len(piece.missing_pieces) == 0:
                    sort_list = sorted(piece.piece_data.items())
                    data = b''.join([x[1] for x in sort_list])
        return data    
    
    def get_nearest_timeout(self):
        if self.requests:
            nearest_block = min(self.requests, key=lambda x: abs(x.timeout - datetime.now()))
            return (nearest_block.timeout - datetime.now()).total_seconds()
        return None
    
    def block_timeout(self):
        soonest = self.get_nearest_timeout()
        if soonest in self.requests:
            self.requests.remove(soonest)
    
    def _get_blocks(self):
        # get piece from piece manager, calculate size
        piece = self.piece_manager.get_piece()
        piece_size = self.piece_size
        if self.piece_manager.is_last_piece(piece):
            piece_size = min(piece_size, self.full_size % piece_size) 
        
        # add to list of pieces
        missing_blocks = [x for x in range(ceil(piece_size / self.BLOCK_SIZE))]
        p = Piece(piece, missing_blocks, datetime.now())
        self.pieces.append(p)
        
        remaining_size = piece_size
        block_id = 0
        while remaining_size > 0:
            block_size = min(BlockManager.BLOCK_SIZE, remaining_size)
            r = Request(piece, block_id, block_id * BlockManager.BLOCK_SIZE, block_size)
            self.outstanding.append(r)
            remaining_size -= BlockManager.BLOCK_SIZE
            block_id += 1
        

if __name__ == "__main__":
    from src.backend.peer_protocol.PieceManager import PieceManager
    p = PieceManager(10)
    p.add_piece(0)
    b = BlockManager(p, 11, 30)
    b.fill_request()
    print(len(b.requests), b.requests)
    print(len(b.outstanding), b.outstanding)
    print(b.get_nearest_timeout())
    
    b.block_timeout()
    b.fill_request()
    print(len(b.requests), b.requests)
    print(len(b.outstanding), b.outstanding)
    print(b.get_nearest_timeout())