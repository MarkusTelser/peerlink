from bencode import encode
from hashlib import sha1
from codecs import decode
from urllib.parse import quote_plus 
from random import choice
from string import ascii_letters
import libtorrent as lt

class TorrentFile:
    def __init__(self, name, length=0, encoding=None, checksum=None):
        self.name = name
        self.length = length
        self.encoding = encoding
        self.checksum = checksum

class TorrentData:
    def __init__(self):
        self.announces = set()
        self.created_by = ""
        self.creation_date = ""
        self.comment = ""
        self.encoding = ""
        self.nodes = set()

        self.pieces = bytes()
        self.piece_length = 0

        self.has_multi_file = False
        self.files = {}
        self.info = None
        self.private = False

    @property
    def info_hash(self):
        """
        info = lt.torrent_info(open('../book.torrent','rb').read())
        info_hash = info.info_hash()
        print(info_hash)
        """
        encoded = encode(self.info)
        hex_enc = sha1(encoded).hexdigest()
        ascii_dec = decode(hex_enc, "hex")
        return ascii_dec 
            
    @property 
    def info_hash_quoted(self):
        return quote_plus(self.info_hash)

    def generate_pieces(self):
        pass

    @staticmethod
    def getAnnounceConnection(announce):
        return announce.split("://")[0]

    @staticmethod
    def getLinkFromAnnounce(announce):
        ann = TorrentData.getAnnounceConnection(announce)
        if ann == "http":
            return "http://" + announce.split("/")[2]
        elif ann == "https":
            return "https://" + announce.split("/")[2]
        elif ann == "udp":
            return announce.split("/")[2]
    
    @staticmethod
    def gen_peer_id():
        return ''.join(choice(ascii_letters) for _ in range(20))