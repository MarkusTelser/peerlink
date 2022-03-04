import socket
from os import stat
from struct import pack, unpack
from collections import namedtuple
from src.backend.dht.DHT import DHT
from src.backend.exceptions import MessageExceptions, NetworkExceptions

from src.backend.metadata.Bencoder import bencode

class PeerMessageIDs:
    CHOKE = 0x0
    UNCHOKE = 0x1
    INTERESTED = 0x2
    NOTINTERESTED = 0x3
    HAVE = 0x4
    BITFIELD = 0x5
    REQUEST = 0x6
    PIECE = 0x7
    CANCEL = 0x8
    
    # DHT extension
    PORT = 0x9
    
    # Fast extension
    SUGGEST = 0x0D
    HAVEALL = 0x0E
    HAVENONE = 0x0F
    REJECTREQUEST = 0x10
    ALLOWEDFAST = 0x11
    
    # Hash Transfer Protcol
    HASHREQUEST = 0x15
    HASHES = 0x16
    HASHREJECT = 0x17
    
    # client specific
    LTEPHANDSHAKE = 0x14

 # BITFIELD, PIECE have variable len
class PeerMessageLengths:
    HANDSHAKE = 68
    KEEP_ALIVE = 4
    CHOKE = 5
    UNCHOKE = 5
    INTERESTED = 5
    NOTINTERESTED = 5
    HAVE = 25
    PORT = 9
    REQUEST = 17
    CANCEL = 17

class PeerMessageStructures:
    Handshake = namedtuple('Handshake', 'peer_id reserved')
    KeepAlive = namedtuple('KeepAlive', '')
    Choke = namedtuple('Choke', '')
    Unchoke = namedtuple('Unchoke', '')
    Interested = namedtuple('Interested', '')
    NotInterested = namedtuple('NotInterested', '')
    Have = namedtuple('Have', 'piece_index')
    Bitfield = namedtuple('Bitfield', 'bitfield')
    Request = namedtuple('Request', 'index begin length')
    Piece = namedtuple('Piece', 'index begin block')
    Cancel = namedtuple('Cancel', 'index begin length')
    Port = namedtuple('Port', 'listen_port')
    
"""
this class contains a validate (def val)
and build (def bld) for each peer message type
so communication in each direction is easily possible
in an upper class socket a receive is 
implemented, because we don't always know what we receive
"""

"""
handshake: <pstrlen><pstr><reserved><info_hash><peer_id>
"""
def bld_handshake(info_hash, peer_id, reserved):
    pstrlen = 19
    pstr = b'BitTorrent protocol'
    
    msg = pack('!B', pstrlen)
    msg += pack('!19s', pstr)
    msg += pack('!8s', reserved)
    msg += pack('!20s', info_hash)
    msg += pack('!20s', peer_id)

    return msg

def val_handshake(recv, info_hash, peer_id):
    if recv == b'':
        raise NetworkExceptions('Connection was closed by other peer')
    
    if len(recv) != PeerMessageLengths.HANDSHAKE:
        raise MessageExceptions("Error: Handshake message has wrong size", len(recv), recv)
    
    pstrlen, pstr = unpack("!B19s", recv[:20])
    if pstrlen != 19 or pstr != b'BitTorrent protocol':
        raise MessageExceptions("Error: Only BitTorrent protocol supported", pstrlen, pstr)

    reserved = unpack("!8s", recv[20:28])[0]

    recv_info_hash = unpack("!20s", recv[28:48])[0]
    if recv_info_hash != info_hash:
        raise MessageExceptions("Error: Received info hash does not match")

    recv_peer_id = unpack("!20s", recv[48:68])[0]
    if peer_id == "" or recv_peer_id == peer_id:
        print('not unique', recv_peer_id, peer_id)
        raise MessageExceptions("Error: Peer didn't return unique peer id")
    
    ret = PeerMessageStructures.Handshake(recv_peer_id, reserved)
    return ret

"""
keep-alive: <len=0000>
"""
def bld_keep_alive():
    length = 0
    msg = pack("!I", length)
    return msg

"""
choke: <len=0001><id=0>
"""
def bld_choke():
    length = 1
    id = PeerMessageIDs.CHOKE
    msg = pack("!IB", length, id)
    return msg

"""
unchoke: <len=0001><id=1>
"""
def bld_unchoke():
    length = 1
    id = PeerMessageIDs.UNCHOKE
    msg = pack("!IB", length, id)
    return msg

"""
interested: <len=0001><id=2>
"""
def bld_interested():
    length = 1
    id = PeerMessageIDs.INTERESTED
    msg = pack("!IB", length, id)
    return msg

"""
not interested: <len=0001><id=3>
"""
def bld_not_interested():
    length = 1
    id = PeerMessageIDs.NOTINTERESTED
    msg = pack("!IB", length, id)
    return msg

"""
have: <len=0005><id=4><piece index>
"""
def bld_have(piece_index):
    length = 5
    id = PeerMessageIDs.HAVE

    msg = pack("!IB", length, id)
    msg += pack("!20s", piece_index)
    return msg

def val_have(recv):
    piece_index = unpack("!I", recv[5:9])[0]
    ret = PeerMessageStructures.Have(piece_index)
    return ret

"""
bitfield: <len=0001+X><id=5><bitfield>
"""
def bld_bitfield(bitfield):
    length = 1 + len(bitfield)
    id = PeerMessageIDs.BITFIELD

    msg = pack("!IB", length, id)
    msg += pack(f"{len(bitfield)}s", bitfield)
    return msg

def val_bitfield(recv):
    bitfield = recv[5:]
    ret = PeerMessageStructures.Bitfield(bitfield)
    return ret

"""
request: <len=0013><id=6><index><begin><length>
"""
def bld_request(index, begin, length):
    len = 13
    id = PeerMessageIDs.REQUEST

    msg = pack("!IB", len, id)
    msg += pack("!III", index, begin, length)
    return msg

def val_request(recv):
    index, begin, length = unpack("!III", recv[5:17])
    ret = PeerMessageStructures.Request(index, begin, length)
    return ret


"""
piece: <len=0009+X><id=7><index><begin><block>
"""
def bld_piece(index, begin, block):
    length = 9 + len(block)
    id = PeerMessageIDs.PIECE

    msg = pack("!IB", length, id)
    msg += pack(f"!II{len(block)}s", index, begin, block)
    return msg

def val_piece(recv):
    index, begin, block = unpack(f"!II{len(recv) - 13}s", recv[5:])
    ret = PeerMessageStructures.Piece(index, begin, block)
    return ret

"""
cancel: <len=0013><id=8><index><begin><length>
"""
def bld_cancel(index, begin, length):
    len = 13
    id = PeerMessageIDs.CANCEL

    msg = pack("!IB", len, id)
    msg += pack("!III", index, begin, length)
    return msg

def val_cancel(recv):
    index, begin, length = unpack("!III", recv[5:17])
    ret = PeerMessageStructures.Cancel(index, begin, length)
    return ret

# if DHT tracker is supported
"""
port: <len=0003><id=9><listen-port>
"""
def bld_port():
    length, id, listen_port = 3, PeerMessageIDs.PORT, DHT.PORT

    msg = pack("!IB", length, id)
    msg += pack("!H", listen_port)
    print('sending port', msg)
    return msg

def val_port(recv):    
    listen_port = unpack("!H", recv[5:9])[0]
    ret = PeerMessageStructures.Port(listen_port)
    print('received port', recv)
    return ret
        