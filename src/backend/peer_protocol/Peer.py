from distutils import extension
import errno
import socket
import select
from math import ceil
from struct import unpack
from threading import Thread

from src.backend.peer_protocol.BlockManager import BlockManager
from src.backend.peer_protocol.PieceManager import PieceManager

from .PeerMessages import *
from .PeerStreamIterator import PeerStreamIterator
from src.backend.FileHandler import FileHandler
from src.backend.exceptions import *
from .PeerIDs import PeerIDs
from src.backend.peer_protocol.ReservedExtensions import gen_extensions, get_extensions, ReservedExtensions
from src.backend.peer_protocol.ExtensionProtocol import ExtensionProtocol

from src.backend.peer_protocol import PeerMessages
"""
set timeout new every time
use sched library
select should work, especially for client server model (maybe problems with win comptability)
"""
import asyncio

class PPeer(asyncio.Protocol):
    def __init__(self, peer_id, piece_manager: PieceManager, file_handler: FileHandler, extension: ExtensionProtocol):
        super().__init__()
        piece_length, full_size = file_handler.data.piece_length, file_handler.data.files.length
        
        self.transport = None
        self.stream = PeerStreamIterator(extension)
        self.file_handler = file_handler
        self.piece_manager = piece_manager
        self.block_manager = BlockManager(piece_manager, piece_length, full_size)
        self.extension = extension
        
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False
        
        self.first_message = True
        self.peer_id = peer_id
        
    def connection_made(self, transport: asyncio.transports.BaseTransport) -> None:
        self.transport = transport
        
    def data_received(self, data: bytes):
        recv = self.stream.parse(data)
        
        if recv == None:
            return
        elif isinstance(recv, PeerMessageStructures.Choke):
            self.am_choking = True
        elif isinstance(recv, PeerMessageStructures.Unchoke):
            self.am_choking = False
            if self.am_interested:
                requests = self.block_manager.fill_request()
                print('UNCHOKED + INTERSTED', len(requests))
                for request in requests:
                    msg = bld_request(request.piece_id, request.startbit, request.length)
                    self.transport.write(msg)
        elif isinstance(recv, PeerMessageStructures.Interested):
            self.am_interested = True
        elif isinstance(recv, PeerMessageStructures.NotInterested):
            self.am_interested = False
        elif isinstance(recv, PeerMessageStructures.Have):
            pass#self.piece_manager.add_piece(self.peer_id, recv.piece_index)
            #if recv.piece_index not in self.pieces:
            #    self.pieces.append(int(recv.piece_index))
        elif isinstance(recv, PeerMessageStructures.Bitfield):
            if self.first_message: 
                self.piece_manager.add_bitfield(self.peer_id, recv.bitfield)
                print(self.piece_manager.availability)
            else:
                print("bitfield is not first message after handshake")
        elif isinstance(recv, PeerMessageStructures.Request):
            # TODO implement with seeding
            pass
        elif isinstance(recv, PeerMessageStructures.Piece):
            print('RECEIVED BLOCK ', recv.index, 'AT', recv.begin)
            is_last_block = self.block_manager.add_block(recv.index, recv.begin, recv.block)
            if is_last_block:
                data = self.block_manager.get_piece_data(recv.index)
                if self.file_handler.verify_piece(recv.index, data):
                    self.piece_manager.finished_piece(recv.index)
                    self.file_handler.write_piece(recv.index, data)
                else:
                    print('wrong hash' * 100)
            
                print('FULL PIECE', recv.index)
                print(f"{self.piece_manager.downloaded}% {self.piece_manager.health}% {self.piece_manager.availability}")
            
            # requests outstanding piece
            requests = self.block_manager.fill_request()
            for request in requests:
                msg = bld_request(request.piece_id, request.startbit, request.length)
                self.transport.write(msg)
        elif isinstance(recv, PeerMessageStructures.Cancel):
            pass
        # TODO implement with DHT
        elif isinstance(recv, PeerMessageStructures.Port):
            print("dht port received", recv.listen_port)
            asyncio.create_task(DHT.ping(self.transport.get_extra_info('peername')))
        else:
            print(recv)
        
        self.first_message = False
        print('received data', type(recv))
    
    def eof_received(self):
        print('connection closed: eof')
        self.transport.close()
    
    def connection_lost(self, exc):
        print('connection lost')
        
        
class MPeer:
    def __init__(self, address, info_hash, peer_id, piece_manager, file_handler):
        super().__init__()
        self.address = address
        self.info_hash = info_hash
        self.peer_id = bytes(peer_id, 'utf-8')
        
        self.extension = ExtensionProtocol()
        self.piece_manager = piece_manager
        self.file_handler = file_handler
        
        self.start_task = None
        self.transport = None
    
    def start(self):
        self.start_task = asyncio.create_task(self._start())
    
    def pause(self):
        if self.start_task != None:
            self.start_task.cancel()
        if self.transport != None:    
            self.transport.close()
    
    async def _start(self):
        try:
            loop = asyncio.get_running_loop()
            
            # connect to socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(False)
            await loop.sock_connect(sock, self.address)
            
            # send and receive handshake
            HANDSHAKE_TIMEOUT = 10
            supported_ext = gen_extensions(dht=True)
            msg = bld_handshake(self.info_hash, self.peer_id, supported_ext)
            co = loop.sock_sendall(sock, msg)
            await asyncio.wait_for(co, timeout=HANDSHAKE_TIMEOUT)
            co = loop.sock_recv(sock, PeerMessageLengths.HANDSHAKE)
            recv = await asyncio.wait_for(co, timeout=HANDSHAKE_TIMEOUT)
            handshake = PeerMessages.val_handshake(recv, self.info_hash, self.peer_id)
            extensions = get_extensions(handshake.reserved)
            #print(handshake, extensions)
            
            # create transport and start asnychrono communication
            protocol_factory = lambda: PPeer(self.peer_id, self.piece_manager, self.file_handler, self.extension)
            self.transport, protocol = await loop.create_connection(protocol_factory, sock=sock)
            
            # send interested message and start downloading
            protocol.am_interested = True
            self.transport.write(bld_interested())
            
            # send libtorrent extension handshake if supported
            if ReservedExtensions.LibtorrentExtensionProtocol in extensions:
                pass
            
            # send udp port, if supported
            if ReservedExtensions.BitTorrentDHT in extensions:
                print('supports DHT')
                self.transport.write(bld_port())
            
            await asyncio.sleep(3600)
        except Exception as e:
            print(e)
                    

"""
implement peer protocol
"""
class Peer(Thread):
    MAX_INCOMING_CON = 5
    TIMEOUT = 2 * 60

    def __init__(self, address, data, piece_manager: PieceManager, file_handler: FileHandler, peer_id=""):
        super().__init__()
        self.sock = None
        self.address = address #  => (ip, port)
        self.info_hash = data.info_hash
        if type(peer_id) == str:
            self.peer_id = bytes(peer_id, 'utf-8')
        elif type(peer_id) == bytes:
            self.peer_id = peer_id
        
        self.data = data
        self.piece_manager = piece_manager
        self.block_manager = BlockManager(piece_manager, data.piece_length, data.files.length)
        self.file_handler = file_handler
        self.pieces = list()
        

        # TODO implement after right
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False
        
        self.first_message = True
        self.message_list = list()

    def run(self):
        try:
            self.create_con()
            self.extension_protocol = ExtensionProtocol()
            self.psiterator = PeerStreamIterator(self.sock, self.extension_protocol) 
            
            msg = bld_handshake(self.info_hash, self.peer_id)
            self.send_msg(msg, expected_len=68)
            peer_id, reserved = self.recv_handshake(self.info_hash, self.peer_id)
            self.peer_id = peer_id
            print("success handshake", self.address, reserved)
        except Exception as e:
            print(e, self.address)
            return
        
        if ReservedExtensions.LibtorrentExtensionProtocol in get_extensions(reserved):
            print("-"*100)
            print("supports extension")
            msg = self.extension_protocol.bld_handshake('qBitTorrent 1.0')
            self.send_msg(msg)
            print("-"*100)
        
        if ReservedExtensions.BitTorrentDHT in get_extensions(reserved):
            print("supports DHT", self.address)
        
        self.sock.setblocking(0)
        
        rlist = [self.sock]
        wlist = []
        xlist = [self.sock] 
        
        while True:
            timeout = self.block_manager.get_nearest_timeout()
            rrlist, wwlist, xxlist = select.select(rlist, wlist, xlist, timeout)
            
            if not rrlist and not wwlist and not xxlist:
                self.block_manager.block_timeout()
            
            for readable in rrlist:
                self.recv_msg()
                
                # send an interested, if not already
                if not self.am_interested:
                    msg = bld_interested()
                    self.send_msg(msg)
                    self.am_interested = True
                # request data if unchoked, otherwise wait
                elif not self.am_choking:
                    requests = self.block_manager.fill_request()
                    for request in requests:
                        msg = bld_request(request.piece_id, request.startbit, request.length)
                        self.send_msg(msg)
                rrlist.remove(readable)
            for writeable in wwlist:
                wwlist.remove(writeable)
            for exception in xxlist:
                xxlist.remove(exception)
      
    def create_con(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(Peer.TIMEOUT)
        #self.sock.bind(('localhost', 50000))
        #self.sock.listen(Peer.MAX_INCOMING_CON)
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
        except ConnectionResetError:
            raise NetworkExceptions('connection reset by peer')
        
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
        #if peer_id != "" and recv_peer_id != peer_id:
        #    print(recv_peer_id, peer_id)
        #    raise MessageExceptions("Error: Peer didn't return unique peer id")

        return recv_peer_id, reserved
    
    def recv_msg(self):
        recv = self.psiterator.recv()
        
        if recv == None:
            return
        elif isinstance(recv, PeerMessageStructures.Choke):
            print("choked", self.address)
            self.am_choking = True
        elif isinstance(recv, PeerMessageStructures.Unchoke):
            print("unchoked", self.address)
            self.am_choking = False
        elif isinstance(recv, PeerMessageStructures.Interested):
            self.am_interested = True
        elif isinstance(recv, PeerMessageStructures.NotInterested):
            self.am_interested = False
        elif isinstance(recv, PeerMessageStructures.Have):
            self.piece_manager.add_piece(self.peer_id, recv.piece_index)
            if recv.piece_index not in self.pieces:
                self.pieces.append(int(recv.piece_index))
        elif isinstance(recv, PeerMessageStructures.Bitfield):
            if self.first_message:
                print("BITFIELD", recv.bitfield)
                self.piece_manager.add_bitfield(self.peer_id, recv.bitfield)
                self.add_bitfield(recv.bitfield)
            else:
                raise Exception("bitfield is not first message after handshake", self.message_list)
        elif isinstance(recv, PeerMessageStructures.Request):
            # TODO implement with seeding
            pass
        elif isinstance(recv, PeerMessageStructures.Piece):
            full_piece = self.block_manager.add_block(recv.index, recv.begin, recv.block)
            if full_piece:
                data = self.block_manager.get_piece_data(recv.index)
                if self.file_handler.verify_piece(recv.index, data):
                    self.piece_manager.finished_piece(recv.index)
                    self.file_handler.write_piece(recv.index, data)
                else:
                    raise Exception('piece wrong hash', data)
                print("FULLPIECE", recv.index)
                print(f"{self.piece_manager.downloaded}% {self.piece_manager.health}% {self.piece_manager.availability}")
                
        elif isinstance(recv, PeerMessageStructures.Cancel):
            pass
        # TODO implement with DHT
        elif isinstance(recv, PeerMessageStructures.Port):
            print("port", recv.listen_port)
            pass
        else:
            print(recv)
            
        self.first_message = False
        self.message_list.append(recv)
        
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