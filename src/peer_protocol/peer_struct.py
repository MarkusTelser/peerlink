from enum import Enum
from struct import pack, unpack
import socket

class PeerMessage(Enum):
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

class PeerMsgLengths(Enum):
    HANDSHAKE = 68
    KEEP_ALIVE = 4
    CHOKE = 5
    UNCHOKE = 5

"""
this class contains a validate (def val)
and build (def bld) for each peer message type
so communication in each direction is easily possible
in an upper class socket a receive is 
implemented, because we don't always know what we receive
"""

"""
validate everything except id
and length in keep alive
"""
class PeerStruct:  
    def send_msg(self, msg):
        try:
            print("writing on socket")
            send = self.sock.send(msg)
        except socket.timeout:
            #print("Error: Send/Response timed out")
            return False
        except Exception as e:
            print(e)
            return False

    def send_handshake(self, info_hash, peer_id):
        pstrlen = 19
        pstr = b'BitTorrent protocol'
        reserved = 0x0
        
        msg = pack('!B', pstrlen)
        msg += pack('!19s', pstr)
        msg += pack('!Q', reserved)
        msg += pack('!20s', info_hash)
        msg += pack('!20s', peer_id)

        self.send_msg(msg)
        
    def val_handshake(self, recv, info_hash, peer_id):
        if len(recv) != PeerMsgLengths.HANDSHAKE:
            print("Error: Handshake message has wrong size")
            return None
        
        recv_info_hash = unpack("!20s", recv[28:48])[0]
        if recv_info_hash != info_hash:
            print("Error: Received info hash does not match")
            return None

        recv_peer_id = unpack("!20s", recv[48:68])[0]
        if recv_peer_id == peer_id:
            print("Erro: Peer didn't return unique peer id")
            return None

        return recv_peer_id

    def send_keep_alive(self):
        length = 0
        msg = pack("!I", length)
        self.send_msg(msg)
    
    def val_keep_alive(self, recv):
        if len(recv) != PeerMsgLengths.KEEP_ALIVE:
            print("Error: Keep alive message has wrong size")
            return False
        
        length = unpack("!I", recv)
        if length != 0:
            print("Error: Keep alive length field not 0")
            return False
        
        return True

    def send_choke(self):
        length = 1
        id = 0
        msg = pack("!IB", length, id)

        self.send_msg(msg)
    
    def val_choke(self, recv):
        if len(recv) != PeerMsgLengths.CHOKE:
            print("Error: Choke message has wrong size")
            return False
        
        length = unpack("!I", recv[:4])
        if length != 1:
            print("Error: Choke length field not 1")
            return False
        
        return True

    def send_unchoke(self):
        length = 1
        id = 1
        msg = pack("!IB", length, id)

        self.send_msg(msg)

    def val_unchoke(self, recv):
        if len(recv) != PeerMsgLengths.UNCHOKE:
            print("Error: Unchoke message has wrong size")
            return False
        
        length = unpack("!I", recv[:4])
        if length != 1:
            print("Error: Unchoke length field not 1")
            return False
        
        return True

    def send_interested():
        pass

    def val_interested():
        pass

    def send_not_interested():
        pass
    
    def val_not_interested():
        pass

    def send_have():
        pass
    
    def val_have():
        pass

    def send_request():
        pass

    def val_request():
        pass

    def send_piece():
        pass
    
    def val_piece():
        pass

    def send_cancel():
        pass

    def val_cancel():
        pass

    def send_bitfield():
        pass

    def val_bitfield(self, data):
        if data == None:
            print("Error: data is empty")
            return None
        
        if len(data) < 5:
            print("Error: bitfield message too small")
            return None

        length = unpack("!IB", data[:4])[0]

        if length <= 1:
            print("Error: bitfield length field too small")
            return None

        bitfield = data[5:4+length]

        # iterate over bitfield to find available pieces
        print(bitfield)
        for count, bit in enumerate(bitfield):
            pass

    # if DHT tracker is supported
    def send_port():
        pass

    def val_port():
        pass


        
