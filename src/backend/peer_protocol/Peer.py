import socket
import sys
import errno
from struct import unpack
from threading import Thread
from math import ceil
from .PeerMessages import PeerMessageLengths, PeerMessageStructures
from .PeerStreamIterator import PeerStreamIterator
from ..exceptions import *
from .PeerIDs import PeerIDs

"""
implement peer protocol
"""
class Peer(Thread):
    TIMEOUT = 10

    def __init__(self, address, peer_id, data, piece_manager, file_handler):
        super().__init__()
        self.sock = None
        self.address = address #  => (ip, port)
        self.info_hash = data.info_hash
        self.peer_id = bytes(peer_id, 'utf-8')
        
        self.data = data
        self.piece_manager = piece_manager
        self.file_handler = file_handler
        self.pieces = list()

        # TODO implement after right
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False

    def run(self):
        try:
            self.create_con()   
            self.psiterator = PeerStreamIterator(self.sock) 
        
            # send and receive handshake
            msg = self.psiterator.bld_handshake(self.info_hash, self.peer_id)
            self.send_msg(msg, expected_len=68)
            peer_id, reserved = self.recv_handshake(self.info_hash, self.peer_id)
            print(peer_id, PeerIDs.get_client(peer_id))
        except Exception as e:
            return
        #print("success", self.address, reserved)

        try:
            self.recv_msg()
        except Exception as e:
            print(e)
        
        msg = self.psiterator.bld_interested()
        self.send_msg(msg)  

        while self.am_choking:
            r = self.recv_msg()
            if r == None:
                return
            #print(type(r), r, self.am_choking)

        print("success", self.address)


        BLOCK_SIZE = 2 ** 16
        piece_size = self.data.piece_length
        i = 0
        size = BLOCK_SIZE

        while piece_size > 0:
            if piece_size < BLOCK_SIZE:
                size = piece_size

            msg = self.psiterator.bld_request(0, i * BLOCK_SIZE, size)
            self.send_msg(msg)

            r = self.recv_msg()

            piece_size -= size 
            i += 1
            print("-- block",i , self.address)
        
        sys.exit()
        #listen_thread = Thread(target=self.recv_msg)
        #send_thread = Thread(target=self.send)

        # TODO thread listen on socket
        # TODO thread gets requests from piece manager
      
    def create_con(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.TIMEOUT)
        self.sock = sock
        try:
            self.sock.connect(self.address)
        except ConnectionRefusedError as e:
            raise NetworkExceptions('Connection refused')
        except socket.timeout:
            raise ConnectTimeout("timed out waiting")
        except socket.error as e:
            if e.errno == errno.ENETUNREACH:
                raise NetworkExceptions('Network is unreachable')
            elif e.errno == errno.EHOSTUNREACH:
                raise NetworkExceptions('No route to host')
            raise e

    def send_msg(self, msg, expected_len=-1):
        try:
            send_len = self.sock.send(msg)
        except socket.timeout:
            raise SendTimeout('Sending msg timed out')
        
        if expected_len != -1 and expected_len != send_len:
            raise Exception("Error: Didn't send everything")

    def recv_handshake(self, info_hash, peer_id):
        try:
            recv = self.sock.recv(PeerMessageLengths.HANDSHAKE)
        except socket.timeout:
            raise ReceiveTimeout("Error: Response timed out")
        
        if len(recv) == 0 and recv == b'':
            raise ConnectionClosed("Peer closed connection")

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
        if recv_peer_id == peer_id:
            raise MessageExceptions("Error: Peer didn't return unique peer id")

        return recv_peer_id, reserved
    
    def recv_msg(self):
        recv = self.psiterator.recv()

        if isinstance(recv, PeerMessageStructures.Choke):
            self.am_choking = True
        elif isinstance(recv, PeerMessageStructures.Unchoke):
            self.am_choking = False
        elif isinstance(recv, PeerMessageStructures.Interested):
            self.am_interested = True
        elif isinstance(recv, PeerMessageStructures.NotInterested):
            self.am_interested = False
        elif isinstance(recv, PeerMessageStructures.Have):
            self.piece_manager.add_piece(recv.piece_index)
            if recv.piece_index not in self.pieces:
                self.pieces.append(int(recv.piece_index))
        elif isinstance(recv, PeerMessageStructures.Bitfield):
            self.piece_manager.add_bitfield(recv.bitfield)
            self.add_bitfield(recv.bitfield)
        elif isinstance(recv, PeerMessageStructures.Request):
            # TODO implement with seeding
            pass
        elif isinstance(recv, PeerMessageStructures.Piece):
            print(recv.index, recv.begin, len(recv.block), recv.block)
            self.file_handler.write_block(recv.index, recv.begin, recv.block)
        elif isinstance(recv, PeerMessageStructures.Cancel):
            # TODO implement with EndGame Strategy
            pass
        elif isinstance(recv, PeerMessageStructures.Port):
            print("port", recv.listen_port)
            # TODO implement with DHT
            pass
        else:
            pass
        return recv
        
    def add_bitfield(self, bitfield):
        # check if size is correct, account for extra bits at the end
        if len(bitfield) != ceil(self.piece_manager.pieces_count / 8):
            print("bitfield wrong size")
            return 

        for i, byte in enumerate(bitfield):
            bits = '{0:08b}'.format(byte)
            for j, bit in enumerate(bits):
                if int(bit):
                    id = i * 8 + j
                    if id >= self.piece_manager.pieces_count:
                        return
                    if id not in self.pieces:
                        self.pieces.append(id)

    def close_con(self):
        self.sock.close()