import libtorrent as lt
from requests.utils import quote 
import bencode

info = lt.torrent_info(open('../test.torrent','rb').read())
info_hash = info.info_hash()
hexadecimal = str(info_hash)
integer = int(hexadecimal, 16)
print(info.is_valid())
print(info_hash)
print(hexadecimal.encode())
print(hexadecimal)
print(quote(hexadecimal))
print(integer)
print(quote(str(integer)))
print(bencode.encode(hexadecimal))
