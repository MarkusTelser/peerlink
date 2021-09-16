from bencode import encode
from hashlib import sha1
from codecs import decode
from urllib.parse import quote_plus 

def getHashInfo(info):
    encoded = encode(info)
    hex_enc = sha1(encoded).hexdigest()
    ascii_dec = decode(hex_enc, "hex")
    url_encode = quote_plus(ascii_dec)
    return url_encode