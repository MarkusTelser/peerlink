from distutils import extension
import errno
import socket
import select
import concurrent
from math import ceil
from struct import unpack
from threading import Thread
import logging

from src.backend.peer_protocol.BlockManager import BlockManager
from src.backend.peer_protocol.Metadata import MetadataData, MetadataReject, bld_metadata_request
from src.backend.peer_protocol.MetadataManager import MetadataManager
from src.backend.peer_protocol.PieceManager import PieceManager

from .PeerMessages import *
from .PeerStreamIterator import PeerStreamIterator
from src.backend.FileHandler import FileHandler
from src.backend.exceptions import *
from .PeerIDs import PeerIDs
from src.backend.peer_protocol.ReservedExtensions import gen_extensions, get_extensions, ReservedExtensions
from src.backend.peer_protocol.ExtensionProtocol import ExtensionHandshakeMessage, ExtensionProtocol
from src.backend.peer_protocol import PeerMessages
from enum import Enum
import smokesignal


"""
set timeout new every time
use sched library
select should work, especially for client server model (maybe problems with win comptability)
"""
import asyncio

class PeerSources(Enum):
    METADATA = 0
    TRACKER = 1
    DHT = 2
    PEX = 3
    LPD = 4

class PPeer(asyncio.Protocol):
    def __init__(self, peer_id, extension: ExtensionProtocol):
        super().__init__()
        self.transport = None
        self.file_handler = None
        self.block_manager = None
        self.piece_manager = None
        self.metadata_manager = None
        self.extension = extension
        self.stream = PeerStreamIterator(extension)
        self._bitfield = b''
        
        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False
        
        self.first_message = True
        self.peer_id = peer_id
        
        self.resume_download = asyncio.Event()
        self.succ_ext_handshake = asyncio.Event()


        smokesignal.on('finished_full_piece', self._send_have)
        smokesignal.on('reject_piece', self._send_reject)
        
    def connection_made(self, transport: asyncio.transports.BaseTransport) -> None:
        self.transport = transport
    
    def set_torrent(self, piece_manager: PieceManager, file_handler: FileHandler):
        self.file_handler = file_handler
        self.piece_manager = piece_manager
        piece_length, full_size = file_handler.data.piece_length, file_handler.data.files.length
        self.block_manager = BlockManager(piece_manager, piece_length, full_size)
        try:
            self.piece_manager.add_bitfield(self.peer_id, self._bitfield)
        except Exception as e:
            print('EX HERE', str(e))
    
    async def download_meta(self, metadata_manager):
        self.metadata_manager = metadata_manager
        await self.succ_ext_handshake.wait()
        
        # send first chunk of metadata requests
        for block in metadata_manager.request_blocks():
            mid = self.extension.extensions['ut_metadata']
            msg = bld_metadata_request(mid, block)
            self.transport.write(msg)
            
        await metadata_manager.finished.wait()

    def resume_downloading(self):
        self.resume_download.set()
        self._send_interested()
        self._send_requests()
    
    def pause_downloading(self):
        self.resume_download.clear()
        self._send_uninterested()
        
    def data_received(self, data: bytes):
        recv = self.stream.parse(data)
        
        if recv == None:
            return
        elif isinstance(recv, PeerMessageStructures.Choke):
            self.am_choking = True
        elif isinstance(recv, PeerMessageStructures.Unchoke):
            self.am_choking = False
            if self.am_interested and self.resume_download.is_set():
                self._send_requests()
        elif isinstance(recv, PeerMessageStructures.Interested):
            self.am_interested = True
        elif isinstance(recv, PeerMessageStructures.NotInterested):
            self.am_interested = False
        elif isinstance(recv, PeerMessageStructures.Have):
            pass#self.piece_manager.add_piece(self.peer_id, recv.piece_index)
            #if recv.piece_index not in self.pieces:
            #    self.pieces.append(int(recv.piece_index))
        elif isinstance(recv, PeerMessageStructures.Bitfield):
            #if self.first_message: 
            if self.piece_manager:
                self.piece_manager.add_bitfield(self.peer_id, recv.bitfield)
                print(self.piece_manager.availability)
            # save bitfield in temporary variable until metadata is retrieved and piece manager can be created
            else:
                self._bitfield = recv.bitfield
            #else:
            #    print("bitfield is not first message after handshake")
        elif isinstance(recv, PeerMessageStructures.Request):
            # TODO implement with seeding
            pass
        elif isinstance(recv, PeerMessageStructures.Piece):
            is_last_block = self.block_manager.add_block(recv.index, recv.begin, recv.block)
            if is_last_block:
                data = self.block_manager.get_piece_data(recv.index)
                if self.file_handler.verify_piece(recv.index, data):
                    self.piece_manager.finished_piece(recv.index)
                    self.file_handler.write_piece(recv.index, data)
                else:
                    self.piece_manager.reject_piece(recv.index)
                    print('hash' * 100)
            
                print('FULL PIECE', recv.index)
                print(f"{self.piece_manager.downloaded_percent}% {self.piece_manager.health}% {self.piece_manager.availability}")
            
            # requests outstanding piece
            if self.resume_download.is_set():
                self._send_requests()
        elif isinstance(recv, PeerMessageStructures.Cancel):
            pass
        # TODO implement with DHT
        elif isinstance(recv, PeerMessageStructures.Port):
            print("dht port received", recv.listen_port)
            asyncio.create_task(DHT.ping(self.transport.get_extra_info('peername')))
        elif isinstance(recv, ExtensionHandshakeMessage):
            self.succ_ext_handshake.set()
            
            # send handshake back
            msg = self.extension.bld_handshake()
            self.transport.write(msg)
            
            if 'ut_metadata' in self.extension.extensions and self.metadata_manager:
                self.metadata_manager.set_full_size(recv.raw['metadata_size'])
        elif isinstance(recv, MetadataData):
            self.metadata_manager.finished_block(recv.piece, recv.data)
            
            for block in self.metadata_manager.request_blocks():
                mid = self.extension.extensions['ut_metadata']
                msg = bld_metadata_request(mid, block)
                self.transport.write(msg)
        elif isinstance(recv, MetadataReject):
            print('RJ' * 100,  recv.piece)
        else:
            print(recv)
        
        
        
        print('received data', type(recv))
        self.first_message = False
    

    def _send_requests(self):
        # don't request if paused by client or other peer
        if not self.resume_download.is_set() or self.am_choking:
            return
        
        requests = self.block_manager.fill_request()
        for request in requests:
            msg = bld_request(request.piece_id, request.startbit, request.length)
            self.transport.write(msg)
    
    async def _add_bitfield_process(self, recv):
        loop = asyncio.get_running_loop()
        with concurrent.futures.ProcessPoolExecutor() as pool:
                
                f = self.piece_manager.add_bitfield
                r = await loop.run_in_executor(pool, f, self.peer_id, recv.bitfield)
    
    def _send_choke(self):
        if self.transport and not self.peer_choking:
            self.peer_choking = True
            self.transport.write(bld_choke())
    
    def _send_unchoke(self):
        if self.transport and self.peer_choking:
            self.peer_choking = False
            self.transport.write(bld_unchoke())
    
    def _send_interested(self):
        if self.transport and not self.am_interested:
            self.am_interested = True
            print('INTERESTED'*30)
            self.transport.write(bld_interested())
            
    def _send_uninterested(self):
        if self.transport and self.am_interested:
            self.am_interested = False
            self.transport.write(bld_uninterested())
    
    def _send_have(self, piece_index):
        #print('send finished full piece')
        if self.transport and not self.transport.is_closing():
            msg = bld_have(piece_index)
            self.transport.write(msg)

    def _send_reject(self, piece_index):
        pass

    def eof_received(self):
        print('connection closed: eof')
        self.transport.close()
    
    def connection_lost(self, exc):
        print('connection lost')
    
    


class MPeer:
    def __init__(self, source, address, info_hash, peer_id):
        super().__init__()
        self._sources = [source]
        self.address = address
        self.info_hash = info_hash
        self.peer_id = bytes(peer_id, 'utf-8')
        self.client = "".join([*PeerIDs.get_client(self.peer_id)])
        
        self.extension = ExtensionProtocol()
        self.metadata_manager = None
        self.piece_manager = None
        self.file_handler = None
        
        self._resume = False
        self.transport, self.protocol = None, None
        self.conn_task = asyncio.create_task(self.init_conn())
    
    async def init_conn(self):
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
            
            # create transport and start asnychrono communication
            protocol_factory = lambda: PPeer(handshake.peer_id, self.extension)
            self.transport, self.protocol = await loop.create_connection(protocol_factory, sock=sock)
            
            if self.piece_manager and self.file_handler:
                self.protocol.set_torrent(self.piece_manager, self.file_handler)
            if self.metadata_manager:
                asyncio.create_task(self.protocol.download_meta(self.metadata_manager))
            
            # send interested message and start downloading
            print('||' * 30)
            if self._resume:
                self.protocol.resume_downloading()
            else:
                self.protocol.pause_downloading()
            
            # send libtorrent extension handshake if supported
            if ReservedExtensions.LibtorrentExtensionProtocol in extensions:
                #msg = self.extension.bld_handshake()
                pass#self.transport.write(msg)
            
            # send udp port, if supported
            if ReservedExtensions.BitTorrentDHT in extensions:
                print('supports DHT')
                self.transport.write(bld_port())
        except Exception as e:
            print('EEE', e)
            if self.transport:
                self.transport.close()
            #logging.exception('EEE')
            
    
    def resume(self):
        if self.transport == None or self.transport.is_closing():
            self.conn_task = asyncio.create_task(self.init_conn())
        if self.conn_task.done() and self.transport:
            self.protocol.resume_downloading()
        self._resume = True
    
    def pause(self):
        if self.conn_task.done() and self.transport:
            self.protocol.pause_downloading()
        self._resume = False
        
    def stop(self):
        if self.conn_task != None:
            self.conn_task.cancel()
        if self.transport != None:    
            self.transport.close()
      
    async def request_metadata(self, metadata_manager: MetadataManager):
        if self.conn_task.done() and self.transport:
            asyncio.create_task(self.protocol.download_meta(metadata_manager))
        self.metadata_manager = metadata_manager
      
    def set_torrent(self, piece_manager, file_handler):
        self.piece_manager = piece_manager
        self.file_handler = file_handler
        if self.transport and self.protocol:
            self.protocol.set_torrent(piece_manager, file_handler)

    def add_source(self, source):
        if source not in self._sources:
            self._sources.append(source)

    @property
    def active(self):
        if self.transport == None or self.transport.is_closing():
            return False
        return self._resume

    @property
    def entirety(self):
        return self.piece_manager.get_entirety(self.peer_id)

    @property
    def flags(self):
        flags = list()
        
        if self.protocol.am_interested and self.protocol.am_choking:
            flags.append(u'\u2193')
        elif self.protocol.am_interested and not self.protocol.am_choking:
            flags.append(u'\u25BC')

        if self.protocol.peer_interested and self.protocol.peer_choking:
            flags.append(u'\u1403')
        elif self.protocol.peer_interested and not self.protocol.peer_choking:
            flags.append(u'\u25B2')
        
        return " ".join(flags)

    
    @property
    def sources(self):
        sources = list()

        if PeerSources.METADATA in self._sources:
            sources.append('M')
        if PeerSources.TRACKER in self._sources:
            sources.append('T')
        if PeerSources.DHT in self._sources:
            sources.append('D')
        if PeerSources.PEX in self._sources:
            sources.append('P')
        if PeerSources.LPD in self._sources:
            sources.append('L')

        return " ".join(sources)