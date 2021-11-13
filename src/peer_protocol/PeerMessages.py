from os import stat
from struct import pack, unpack
from collections import namedtuple
import socket

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
    PORT = 0x9

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
class PeerMessages:
    """
    handshake: <pstrlen><pstr><reserved><info_hash><peer_id>
    """
    def bld_handshake(self, info_hash, peer_id):
        pstrlen = 19
        pstr = b'BitTorrent protocol'
        
        msg = pack('!B', pstrlen)
        msg += pack('!19s', pstr)
        msg += pack('!8x')
        msg += pack('!20s', info_hash)
        msg += pack('!20s', peer_id)

        return msg

    """
    keep-alive: <len=0000>
    """
    def bld_keep_alive(self):
        length = 0
        msg = pack("!I", length)
        return msg

    """
    choke: <len=0001><id=0>
    """
    def bld_choke(self):
        length = 1
        id = PeerMessageIDs.CHOKE
        msg = pack("!IB", length, id)
        return msg

    """
    unchoke: <len=0001><id=1>
    """
    def bld_unchoke(self):
        length = 1
        id = PeerMessageIDs.UNCHOKE
        msg = pack("!IB", length, id)
        return msg

    """
    interested: <len=0001><id=2>
    """
    def bld_interested(self):
        length = 1
        id = PeerMessageIDs.INTERESTED
        msg = pack("!IB", length, id)
        return msg

    """
    not interested: <len=0001><id=3>
    """
    def bld_not_interested(self):
        length = 1
        id = PeerMessageIDs.NOTINTERESTED
        msg = pack("!IB", length, id)
        return msg

    """
    have: <len=0005><id=4><piece index>
    """
    def bld_have(self, piece_index):
        length = 5
        id = PeerMessageIDs.HAVE

        msg = pack("!IB", length, id)
        msg += pack("!20s", piece_index)
        return msg
    
    def val_have(self, recv):
        piece_index = unpack("!20s", recv[5:25])[0]
        ret = PeerMessageStructures.Have(piece_index)
        return ret
    
    """
    bitfield: <len=0001+X><id=5><bitfield>
    """
    def bld_bitfield(self, bitfield):
        length = 1 + len(bitfield)
        id = PeerMessageIDs.BITFIELD

        msg = pack("!IB", length, id)
        msg += pack(f"{len(bitfield)}s", bitfield)
        return msg

    @staticmethod
    def val_bitfield(recv):
        bitfield = recv[5:]
        ret = PeerMessageStructures.Bitfield(bitfield)
        return ret
    
    """
    request: <len=0013><id=6><index><begin><length>
    """
    def bld_request(self, index, begin, length):
        len = 13
        id = PeerMessageIDs.REQUEST

        msg = pack("!IB", len, id)
        msg += pack("!III", index, begin, length)
        return msg

    def val_request(self, recv):
        index, begin, length = unpack("!III", recv[5:17])
        ret = PeerMessageStructures.Request(index, begin, length)
        return ret


    """
    piece: <len=0009+X><id=7><index><begin><block>
    """
    def bld_piece(self, index, begin, block):
        length = 9 + len(block)
        id = PeerMessageIDs.PIECE

        msg = pack("!IB", length, id)
        msg += pack(f"!II{len(block)}s", index, begin, block)
        return msg
    
    def val_piece(self, recv):
        index, begin, block = unpack(f"!II{len(recv) - 13}s", recv[5:])
        ret = PeerMessageStructures.Piece(index, begin, block)
        return ret

    """
    cancel: <len=0013><id=8><index><begin><length>
    """
    def bld_cancel(self, index, begin, length):
        len = 13
        id = PeerMessageIDs.CANCEL

        msg = pack("!IB", len, id)
        msg += pack("!III", index, begin, length)
        return msg

    def val_cancel(self, recv):
        index, begin, length = unpack("!III", recv[5:17])
        ret = PeerMessageStructures.Cancel(index, begin, length)
        return ret

    # if DHT tracker is supported
    """
    port: <len=0003><id=9><listen-port>
    """
    def bld_port(self, listen_port):
        length = 3
        id = PeerMessageIDs.PORT

        msg = pack("!IB", length, id)
        msg += pack("!I", listen_port)
        return msg

    def val_port(self, recv):    
        listen_port = unpack("!I", recv[5:9])[0]
        ret = PeerMessageStructures.Port(listen_port)
        return ret