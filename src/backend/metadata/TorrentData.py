from .Bencoder import encode
from hashlib import sha1
from base64 import b32encode
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
        self.httpseeds = list()

        self.pieces = bytes()
        self.pieces_count = 0
        self.piece_length = 0

        self.has_multi_file = False
        self.files = {}
        self.info_hash = ""
        self.info_hash_hex = ""
        self.private = False

    def check_piece_hash(self, index, hash):
        true_hash = self.pieces[index * 20: (index + 1) * 20]
        return true_hash == hash

    @staticmethod
    def gen_info_hash(info):
        encoded = encode(info)
        hash = sha1(encoded).digest()   
        return hash
            
    @staticmethod
    def gen_info_hash_hex(info):
        encoded = encode(info)
        hex_hash = sha1(encoded).hexdigest()
        return hex_hash.upper()

    @property 
    def info_hash_quoted(self):
        return quote_plus(self.info_hash)

    @property
    def info_hash_base32(self):
        base32 = b32encode(self.info_hash).decode('utf-8')
        return base32
    
    @staticmethod
    def gen_peer_id():
        return ''.join(choice(ascii_letters) for _ in range(20))