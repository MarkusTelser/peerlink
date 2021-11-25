from collections import OrderedDict

"""
dictionary "d...e"
lists "l...e"
integers "i...e"
byte strings "len:..."
"""
class Bencoder:
    def __init__(self) -> None:
        self.i = 0

    # clean function call
    def decode(self, data: bytes):
        self.i = 0
        return self._decode(data)
        
    def _decode(self, data):
        typ = data[self.i:self.i+1]
        
        # dictionary
        if typ == b'd':
            self.i += 1
            
            d = OrderedDict()
            not_end = True
            while not_end:
                key = self._decode(data)
                if key == b'e':
                    not_end = False
                elif type(key) != bytes and type(key) != str:
                    raise Exception('Dictionary key wrong type', key)
                else:
                    value = self._decode(data)
                    d[key] = value
            return d
        # list
        elif typ == b'l':
            self.i += 1
            
            l = list()
            not_end = True
            while not_end:
                item = self._decode(data)
                if item == b'e':
                    not_end = False
                else:
                    l.append(item)
            return l

        # integer
        elif typ == b'i':
            self.i += 1

            end = data[self.i:].find(b'e')
            integer = int(data[self.i:self.i+end])
            
            self.i += 1 + len(str(integer))

            return integer
        # string
        elif typ.isdigit():
            end = data[self.i:].find(b':')
            length = int(data[self.i:self.i+end])
            string = data[self.i+end+1:self.i+end+length+1]
            self.i += length + len(str(length)) + 1
            try:
                return string.decode('utf-8')
            except UnicodeDecodeError:
                return string
        elif typ == b'e':
            self.i += 1
            return b'e'
        else:
            raise Exception('wrong type', typ)


import bencode
import hashlib

with open(f"../../../data/all/testtest.torrent", "rb") as f:
        data = f.read()

b = Bencoder()
result = b.decode(data)

# my result
encr = bencode.bencode(result['info'])
print(hashlib.sha1(encr).digest())

# true result (should be the same)
result = bencode.decode(data)
encr = bencode.bencode(result['info'])
print(hashlib.sha1(encr).digest())