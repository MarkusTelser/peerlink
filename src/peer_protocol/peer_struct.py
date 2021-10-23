from enum import Enum
from struct import pack, unpack
import socket

class PeerMessageIDs(Enum):
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
class PeerMsgLengths(Enum):
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


"""
this class contains a validate (def val)
and build (def bld) for each peer message type
so communication in each direction is easily possible
in an upper class socket a receive is 
implemented, because we don't always know what we receive
"""
class PeerStruct:  
    def send_msg(self, msg):
        try:
            send = self.sock.send(msg)
        except socket.timeout:
            raise Exception("Error: Sending timed out")
        except Exception as e:
            print(e)
            return False
        return send

    """
    handshake: <pstrlen><pstr><reserved><info_hash><peer_id>
    """
    def send_handshake(self, info_hash, peer_id):
        pstrlen = 19
        pstr = b'BitTorrent protocol'
        
        msg = pack('!B', pstrlen)
        msg += pack('!19s', pstr)
        msg += pack('!8x')
        msg += pack('!20s', info_hash)
        msg += pack('!20s', peer_id)

        len = self.send_msg(msg)
        if len != PeerMessageLengths.HANDSHAKE.value:
            raise Exception("Error: Handshake not sent fully", len)
        
    def recv_handshake(self, info_hash, peer_id):
        try:
            recv = self.sock.recv(PeerMessageLengths.HANDSHAKE.value)
        except socket.timeout:
            raise Exception("Error: Response timed out")
        except Exception as e:
            print(e)
            return False
        
        if len(recv) != PeerMessageLengths.HANDSHAKE.value:
            raise Exception("Error: Handshake message has wrong size", len(recv), recv)
        
        recv_info_hash = unpack("!20s", recv[28:48])[0]
        if recv_info_hash != info_hash:
            raise Exception("Error: Received info hash does not match")

        recv_peer_id = unpack("!20s", recv[48:68])[0]
        if recv_peer_id == peer_id:
            raise Exception("Erro: Peer didn't return unique peer id")

        return recv_peer_id

    """
    keep-alive: <len=0000>
    """
    def send_keep_alive(self):
        length = 0
        msg = pack("!I", length)
        self.send_msg(msg)

    """
    choke: <len=0001><id=0>
    """
    def send_choke(self):
        length = 1
        id = PeerMessageIDs.CHOKE.value
        msg = pack("!IB", length, id)

        self.send_msg(msg)
    

    """
    unchoke: <len=0001><id=1>
    """
    def send_unchoke(self):
        length = 1
        id = PeerMessageIDs.UNCHOKE.value
        msg = pack("!IB", length, id)

        self.send_msg(msg)

    """
    interested: <len=0001><id=2>
    """
    def send_interested(self):
        length = 1
        id = PeerMessageIDs.INTERESTED.value
        msg = pack("!IB", length, id)

        len = self.send_msg(msg)
        if len != PeerMessageLengths.INTERESTED.value:
            raise Exception("Error: Interested not fully send", len)


    """
    not interested: <len=0001><id=3>
    """
    def send_not_interested(self):
        length = 1
        id = PeerMessageIDs.NOTINTERESTED.value
        msg = pack("!IB", length, id)

        self.send_msg(msg)
    

    """
    have: <len=0005><id=4><piece index>
    """
    def send_have(self, piece_index):
        length = 5
        id = PeerMessageIDs.HAVE.value

        msg = pack("!IB", length, id)
        msg += pack("!20s", piece_index)

        self.send_msg(msg)
    
    def val_have(self, recv):
        if len(recv) != PeerMessageLengths.HAVE.value:
            print("Error: Have message has wrong size")
            return None
        
        length = unpack("!I", recv[:4])[0]
        if length != 5:
            print("Error: Have length field not 1")
            return None
        
        piece_index = unpack("!20s", recv[5:25])[0]

        return piece_index
    
    """
    bitfield: <len=0001+X><id=5><bitfield>
    """
    def send_bitfield(self, bitfield):
        length = 1 + len(bitfield)
        id = PeerMessageIDs.BITFIELD.value

        msg = pack("!IB", length, id)
        msg += pack(f"{len(bitfield)}s", bitfield)

        self.send_msg(msg)

    def val_bitfield(self, recv):
        """
        if len(recv) <= 5:
            raise Exception("Error: bitfield message too small", recv)
        """
        """
        # doesnt't make any sense, the returend number is always 77
        length = int((unpack("!I", recv[:4])[0] -1)  / 4)
        print(length)
        if length != len(recv) - 4:
            print("Error: bitfield length field wrong")
            return None
        """
        length = int(unpack("!I", recv[:4])[0]) - 1
        if length > len(recv) - 5:
            print("missing bitfield")

        bitfield = recv[5:]
        return bitfield

        # TODO iterate over bitfield to find available pieces
        #print(bitfield)
        #for count, bit in enumerate(bitfield):
        #    print(count, bit)
    
    """
    request: <len=0013><id=6><index><begin><length>
    """
    def send_request(self, index, begin, length):
        len = 13
        id = PeerMessageIDs.REQUEST.value

        msg = pack("!IB", len, id)
        msg += pack("!III", index, begin, length)

        self.send_msg(msg)

    def val_request(self, recv):
        if len(recv) != PeerMessageLengths.REQUEST.value:
            print("Error: Request message has wrong size")
            return None
        
        length = unpack("!I", recv[:4])[0]
        if length != PeerMessageLengths.REQUEST.value:
            print("Error: Request length not 17")
            return None
        
        index, begin, length = unpack("!III", recv[5:17])

        return index, begin, length


    """
    piece: <len=0009+X><id=7><index><begin><block>
    """
    def send_piece(self, index, begin, block):
        length = 9 + len(block)
        id = PeerMessageIDs.PIECE.value

        msg = pack("!IB", length, id)
        msg += pack(f"!II{len(block)}s", index, begin, block)

        self.send_msg(msg)
    
    def val_piece(self, recv):
        if len(recv) <= 13:
            print("Error: Piece message has wrong size")
            return None
        
        length = unpack("!I", recv[:4])[0]
        if length != len(recv) -4:
            print("Error: Piece length wrong size")
            return None
        
        index, begin, block = unpack(f"!II{len(recv) - 9}s", recv[5:])

        return index, begin, block

    """
    cancel: <len=0013><id=8><index><begin><length>
    """
    def send_cancel(self, index, begin, length):
        len = 13
        id = PeerMessageIDs.CANCEL.value

        msg = pack("!IB", len, id)
        msg += pack("!III", index, begin, length)

        self.send_msg(msg)

    def val_cancel(self, recv):
        if len(recv) != PeerMessageLengths.CANCEL.value:
            print("Error: Cancel message has wrong size")
            return None
        
        length = unpack("!I", recv[:4])[0]
        if length != 13:
            print("Error: Cancel length field not 13")
            return None
        
        index, begin, length = unpack("!III", recv[5:17])

        return index, begin, length

    # if DHT tracker is supported
    """
    port: <len=0003><id=9><listen-port>
    """
    def send_port(self, listen_port):
        length = 3
        id = PeerMessageIDs.PORT.value

        msg = pack("!IB", length, id)
        msg += pack("!I", listen_port)

        self.send_msg(msg)


    def val_port(self, recv):
        if len(recv) != PeerMessageLengths.PORT.value:
            print("Error: Port message has wrong size")
            return None
        
        length = unpack("!I", recv[:4])[0]
        if length != 3:
            print("Error: Port length field not 3")
            return None
        
        listen_port = unpack("!I", recv[5:9])[0]

        return listen_port