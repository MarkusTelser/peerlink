from collections import OrderedDict
from re import I
from ..exceptions import WrongFormat, WrongType
    
"""
dictionary "d...e"
lists "l...e"
integers "i...e"
byte strings "len:..."
"""

def _decode(bstring: bytes, i: int, raw: bool = False):
    typ = bstring[i:i+1]
    
    # dictionary
    if typ == b'd':
        i += 1
        
        d = OrderedDict()
        not_end = True
        while not_end:
            key, i = _decode(bstring, i)
            if key == b'e':
                not_end = False
            elif type(key) != bytes and type(key) != str:
                raise WrongType('dict key wrong type', key)
            else:
                value, i = _decode(bstring, i)
                d[key] = value
        return d, i
    # list
    elif typ == b'l':
        i += 1
        
        l = list()
        not_end = True
        while not_end:
            item, i = _decode(bstring, i)
            if item == b'e':
                not_end = False
            else:
                l.append(item)
        return l, i
    # integer
    elif typ == b'i':
        i += 1

        end = bstring[i:].find(b'e')
        # raise error if integer seems to have no end
        if end == -1:
            raise WrongFormat("integer doesn't end with e")
        # raise error if there is a leading zero in integer with a bigger size than one
        if end > 2 and bstring[i] == b'0':
            raise WrongFormat('leading zero in integer')
        # raise error if there is a negative zero like i-0e
        if end == 3 and bstring[i:i+1] == b'-0':
            raise WrongFormat('negative zero is not allowed')
        integer = int(bstring[i:i+end])
        
        i += 1 + len(str(integer))

        return integer, i
    # string
    elif typ.isdigit():
        end = bstring[i:].find(b':')
        # raise error if no colon is found in string
        if end == -1:
            raise WrongFormat("string doesn't have colon to end length")
        length = int(bstring[i:i+end])
        try:
            string = bstring[i+end+1:i+end+length+1]
        except IndexError:
            raise WrongFormat('data finishes before string ends')
        i += length + len(str(length)) + 1
        try:
            if raw:
                return string, i
            else:
                return string.decode('utf-8'), i
        except UnicodeDecodeError:
            if raw:
                raise WrongType('string is not utf-8 decodeable in raw mode')
            return string, i
    # end delimiter
    elif typ == b'e':
        i += 1
        return b'e', i
    else:
        raise WrongType('not supported type: ', typ)


# clean function call
def bdecode(byte_string: bytes, spare_bytes=False):
    dec, i = _decode(byte_string, 0)
    if not spare_bytes:
        return dec
    return dec, byte_string[i:]


def bencode(data):
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
            ret += bencode(item)
        ret += b'e'
        return ret
    elif typ == dict or typ == OrderedDict:
        data = dict(sorted(data.items()))
        ret = b'd'
        if typ == OrderedDict:
            for key, value in data.items():
                if type(key) != str:
                    raise WrongType('key is not string')
                ret += bencode(key)
                ret += bencode(value)
        elif typ == dict:
            # sort dict if not already sorted
            data = OrderedDict(data)
            for key in data:
                if type(key) != str:
                    raise WrongType('key is not string')
                ret += bencode(key)
                ret += bencode(data[key])
        ret += b'e'
        return ret
    else:
        raise WrongType('not supported type: ', typ)