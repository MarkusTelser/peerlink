from bencode import bencode
from hashlib import sha1
from urllib.parse import quote_plus 
from random import choice
from string import ascii_letters

class TorrentFile:
    def __init__(self, name, length=0, encoding=None, checksum=None):
        self.name = name
        self.length = length
        self.encoding = encoding
        self.checksum = checksum

class TorrentData:
    def __init__(self):
        self.announces = list()
        self.created_by = ""
        self.creation_date = ""
        self.comment = ""
        self.encoding = ""
        self.nodes = set()

        self.pieces = bytes()
        self.pieces_count = 0
        self.piece_length = 0

        self.has_multi_file = False
        self.files = {}
        self.info = None
        self.private = False

    def check_piece_hash(self, index, hash):
        true_hash = self.pieces[index * 20: (index + 1) * 20]
        return true_hash == hash

    @property
    def info_hash(self):
        encoded = bencode(self.info)
        hash = sha1(encoded).digest()   
        return hash
            
    @property
    def info_hash_hex(self):
        encoded = bencode(self.info)
        hex_hash = sha1(encoded).hexdigest()
        return hex_hash

    @property 
    def info_hash_quoted(self):
        return quote_plus(self.info_hash)
    
    @staticmethod
    def gen_peer_id():
        return ''.join(choice(ascii_letters) for _ in range(20))