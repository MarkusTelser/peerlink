from bencode import encode
from hashlib import sha1
from codecs import decode
from urllib.parse import quote_plus 
import libtorrent as lt

class TorrentFile:
    def __init__(self, name, length=0, encoding=None, checksum=None):
        self.name = name
        self.length = length
        self.encoding = encoding
        self.checksum = checksum

class TorrentData:
    def __init__(self):
        self.announce = set()
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

    def getHashInfo(self, quoted=True):
        """
        info = lt.torrent_info(open('../book.torrent','rb').read())
        info_hash = info.info_hash()
        print(info_hash)
        """
        encoded = encode(self.info)
        hex_enc = sha1(encoded).hexdigest()
        ascii_dec = decode(hex_enc, "hex")
        if not quoted:
            return ascii_dec 
        else:
            url_encode = quote_plus(ascii_dec)
            return url_encode
        
    def generate_pieces(self):
        pass
