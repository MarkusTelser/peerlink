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
        encoded = bencode(self.info)
        hash = sha1(encoded).digest()
        return hash
            
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
            return announce.split("/")[2].split(":")[0]
    
    @staticmethod
    def getPortFromAnnounce(announce):
        link = announce.split("/")[2]
        if ":" in link:
            return int(link.split(":")[1])
        else:
            pass
        # TODO return ports range to try out
    
    @staticmethod
    def gen_peer_id():
        return ''.join(choice(ascii_letters) for _ in range(20))