import logging
from queue import Queue
from threading import Thread
import threading
from src.backend.trackers.HTTPTracker import HTTPEvents, HTTPTracker
from asyncio import BoundedSemaphore
from datetime import datetime
from src.backend.trackers.UDPTracker import UDPTracker

from .peer_protocol.PeerIDs import PeerIDs
from .peer_protocol.PieceManager import PieceManager
from .FileHandler import FileHandler
from .trackers.Tracker import give_object
from .peer_protocol.Peer import Peer
import asyncio

class Swarm:
    MAX_TRACKER = 100
    MAX_PEERS = 70
    LISTEN_PORT = 6881
    
    def __init__(self, data, path) -> None:
        self.data = data
        self.announces = data.announces
        self.info_hash = data.info_hash
        self.peer_id = PeerIDs.generate()
        self.piece_manager = PieceManager(data.pieces_count, data.piece_length)
        self.file_handler = FileHandler(data, path)
        
        self.peer_limit = BoundedSemaphore(value=Swarm.MAX_PEERS)
        self.tracker_limit = BoundedSemaphore(value=Swarm.MAX_TRACKER)
        self.peer_list = list()
        self.tracker_list = list()
        
        self.start_thread = None
        
        self.path = path
        self.category = ""
        self.backup_name = ""
        self.start_date = ""
        self.finish_date = ""
    
    def start(self):
        print(threading.current_thread().name)
        self.start_thread = asyncio.create_task(self._start())
        print('after creating start ')
    
    async def _start(self):
        try:
            if len(self.start_date) == 0:
                self.start_date = datetime.now().isoformat()
            
            self.init_tracker()
            await self.scrape_trackers()
            #await self.announce_trackers(HTTPEvents.STARTED)
            
            
            
            #self.connect_peers()
        except Exception:
            raise Exception('crashed')
    
    def pause(self):
        self.start_thread.cancel()

    def init_tracker(self):
        print(self.announces)
        
        for tiers in self.announces: 
            for announce in tiers:
                tracker = give_object(announce, self.info_hash, self.peer_id, Swarm.LISTEN_PORT, self.tracker_limit)
                if tracker != None:
                    self.tracker_list.append(tracker)
    
    async def announce_trackers(self, event=None):
        tasks = list()
        for tracker in self.tracker_list:
            uploaded = self.piece_manager.uploaded_bytes
            downloaded = self.piece_manager.downloaded_bytes
            left = self.piece_manager.left_bytes
            
            task = asyncio.create_task(tracker.announce(event, uploaded, downloaded, left), name=tracker.address)
            task.add_done_callback(self.finished_tracker)
            tasks.append(task)
        
        await asyncio.gather(*[t for t in tasks])
        
    async def scrape_trackers(self):
        tasks = list()
        for tracker in self.tracker_list:
            print(tracker)
            task = asyncio.create_task(tracker.scrape(), name=tracker.address)
            tasks.append(task)
        await asyncio.gather(*[t for t in tasks])
    
    def finished_tracker(self, future):
        if future.exception():
            print(future.exception())
            logging.exception('exception')
        elif future.result():
            if type(future.result()) == tuple:
                print(future.result()[1])
            print(len(future.result()), future.get_name())


    def connect_peers(self):
        finished = 0 
        while finished != len(self.tracker_list):
            item = self.finished_tracker.get()
            finished += 1
            
            print(item.error)
            if item:
                if item.peers:
                    # iterate over returned peers
                    print(item.peers)
                    self.add_peerlist(item.peers)
                    
    def add_peerlist(self, peer_list: list):
        for peer in peer_list:
            ip, port = peer[0], peer[1]
            
            found = False
            for p in self.peer_list:
                if p.address[0] == ip and p.address[1] == port:
                    found = True
                    break
            
            if not found:
                address = (ip, port)
                if len(peer) == 2:
                    p = Peer(address, self.data, self.piece_manager, self.file_handler)
                elif len(peer) == 3:
                    p = Peer(address, self.data, self.piece_manager, self.file_handler, peer[2])
                p.start()
                print(address, "started")
                
                self.peer_list.append(p)
