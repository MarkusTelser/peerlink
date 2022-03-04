from collections import OrderedDict
from ..exceptions import WrongFormat, WrongType

class Bencoder:
    def __init__(self) -> None:
        self.i = 0

    # clean function call
    def decode(self, byte_string: bytes, spare_bytes):
        self.i = 0
        dec = self._decode(byte_string)
        if not spare_bytes:
            return dec
        return dec, byte_string[self.i:]
    
    """
    dictionary "d...e"
    lists "l...e"
    integers "i...e"
    byte strings "len:..."
    """
    def _decode(self, bstring: bytes, raw: bool = False):
        typ = bstring[self.i:self.i+1]
        
        # dictionary
        if typ == b'd':
            self.i += 1
            
            d = OrderedDict()
            not_end = True
            while not_end:
                key = self._decode(bstring)
                if key == b'e':
                    not_end = False
                elif type(key) != bytes and type(key) != str:
                    raise WrongType('dict key wrong type', key)
                else:
                    value = self._decode(bstring)
                    d[key] = value
            return d
        # list
        elif typ == b'l':
            self.i += 1
            
            l = list()
            not_end = True
            while not_end:
                item = self._decode(bstring)
                if item == b'e':
                    not_end = False
                else:
                    l.append(item)
            return l

        # integer
        elif typ == b'i':
            self.i += 1

            end = bstring[self.i:].find(b'e')
            # raise error if integer seems to have no end
            if end == -1:
                raise WrongFormat("integer doesn't end with e")
            # raise error if there is a leading zero in integer with a bigger size than one
            if end > 2 and bstring[self.i] == b'0':
                raise WrongFormat('leading zero in integer')
            # raise error if there is a negative zero like i-0e
            if end == 3 and bstring[self.i:self.i+1] == b'-0':
                raise WrongFormat('negative zero is not allowed')
            integer = int(bstring[self.i:self.i+end])
            
            self.i += 1 + len(str(integer))

            return integer
        # string
        elif typ.isdigit():
            end = bstring[self.i:].find(b':')
            # raise error if no colon is found in string
            if end == -1:
                raise WrongFormat("string doesn't have colon to end length")
            length = int(bstring[self.i:self.i+end])
            try:
                string = bstring[self.i+end+1:self.i+end+length+1]
            except IndexError:
                raise WrongFormat('data finishes before string ends')
            self.i += length + len(str(length)) + 1
            try:
                if raw:
                    return string
                else:
                    return string.decode('utf-8')
            except UnicodeDecodeError:
                if raw:
                    raise WrongType('string is not utf-8 decodeable in raw mode')
                return string
        # end delimiter
        elif typ == b'e':
            self.i += 1
            return b'e'
        else:
            raise WrongType('not supported type: ', typ)
    
    def encode(self, data):
        typ = type(data)

        if typ == str or typ == bytes:
            
            if typ == str:
                try:
                    byte_string = bytes(data, 'utf-8')
                except UnicodeEncodeError:
                    raise WrongFormat("String isn't utf-8 formatted")
                try:
                    l = bytes(str(len(byte_string)), 'utf-8')
                except UnicodeEncodeError:
                    raise WrongFormat("String length isn't utf-8 formatted")
                ret = l + b':'
                ret += byte_string
            elif typ == bytes:
                try:
                    l = bytes(str(len(data)), 'utf-8')
                except UnicodeEncodeError:
                    raise WrongFormat("String length isn't utf-8 formatted")
                ret = l + b':'
                ret += data
            return ret
        elif typ == int:
            try:
                byte_string = bytes(str(data), 'utf-8')
            except UnicodeEncodeError:
                raise WrongFormat('int not utf-8 encodable')
            ret = b'i' + byte_string + b'e'
            return ret
        elif typ == tuple or typ == list:
            ret = b'l'
            for item in data:
                ret += self.encode(item)
            ret += b'e'
            return ret
        elif typ == dict or typ == OrderedDict:
            ret = b'd'
            if typ == OrderedDict:
                for key, value in data.items():
                    if type(key) != str:
                        raise WrongType('key is not string')
                    ret += self.encode(key)
                    ret += self.encode(value)
            elif typ == dict:
                # sort dict if not already sorted
                data = OrderedDict(data)
                for key in data:
                    if type(key) != str:
                        raise WrongType('key is not string')
                    ret += self.encode(key)
                    ret += self.encode(data[key])
            ret += b'e'
            return ret
        else:
            raise WrongType('not supported type: ', typ)


b = Bencoder()

def bdecode(byte_string: bytes, spare_bytes=False):
    return b.decode(byte_string, spare_bytes)

def bencode(data):
    return b.encode(data)