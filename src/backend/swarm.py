import logging
from src.backend.metadata import MagnetLink
from src.backend.trackers.HTTPTracker import HTTPEvents, HTTPTracker
from asyncio import BoundedSemaphore
from datetime import datetime

from .peer_protocol.PeerIDs import PeerIDs
from .peer_protocol.PieceManager import PieceManager
from .FileHandler import FileHandler
from .trackers.Tracker import give_object
from .peer_protocol.Peer import MPeer, PPeer, Peer
import asyncio

class Swarm:
    MAX_TRACKER = 100
    MAX_PEERS = 70
    LISTEN_PORT = 6881
    
    def __init__(self) -> None:
        self.data = None
        self.path = ""
        self.peer_id = PeerIDs.generate()
        self.category = ""
        self.backup_name = ""
        self.start_date = ""
        self.finish_date = ""
        
        self.piece_manager = None
        self.file_handler = None
        
        self.start_task = None
        self.tracker_limit = BoundedSemaphore(value=Swarm.MAX_TRACKER)
        self.peer_limit = BoundedSemaphore(value=Swarm.MAX_PEERS)
        self.tracker_list = list()
        self.peer_list = list()
    
    def set_meta_data(self, data, path):
        self.piece_manager = PieceManager(data.pieces_count, data.piece_length)
        self.file_handler = FileHandler(data, path)
        self.data = data
        self.path = path
        self._create_tracker()
    
    def start(self):
        self.start_task = asyncio.create_task(self._start())
    
    async def _start(self):
        try:
            if len(self.start_date) == 0:
                self.start_date = datetime.now().isoformat()
            await self.announce_trackers(HTTPEvents.STARTED)
        except Exception as e:
            logging.exception('error in swarm')
            print(e)
            raise Exception('crashed')
    
    def download_metadata(self, magnet_link: MagnetLink):
        pass
    
    async def pause(self):
        self.start_task.cancel()
        
        for tracker in self.tracker_list:
            tracker.pause()
        
        for peer in self.peer_list:
            peer.pause()
        
        await self.announce_trackers(HTTPEvents.STOPPED)
    
    async def announce_trackers(self, event=None):
        tasks = list()
        for tracker in self.tracker_list:
            uploaded = self.piece_manager.uploaded_bytes
            downloaded = self.piece_manager.downloaded_bytes
            left = self.piece_manager.left_bytes
            
            task_name = ':'.join([str(t) for t in tracker.address ]) if len(tracker.address) == 2 else tracker.address
            func = tracker.announce(event, uploaded, downloaded, left)
            tracker.announce_wrap(func, name=task_name, callback=self.connect_peers)
            tasks.append(tracker.announce_task)
        
        await asyncio.gather(*[t for t in tasks])
        
    async def scrape_trackers(self):
        tasks = list()
        for tracker in self.tracker_list:
            task_name = ':'.join([str(t) for t in tracker.address ]) if len(tracker.address) == 2 else tracker.address
            tracker.scrape_wrap(tracker.scrape(), name=task_name)
            tasks.append(tracker.scrape_task)
        
        await asyncio.gather(*[t for t in tasks])
    
    def connect_peers(self, future):
        if future.exception():
            print(future.exception())
            logging.exception('exception')
        elif future.result():
            print('peers', future.get_name(), len(future.result()))
            for peer in future.result():
                if self.peer_in_list(peer[0], peer[1]):
                    #print('already in peer list', peer, len(self.peer_list))
                    continue
                
                m = MPeer(peer, self.data.info_hash, self.peer_id, self.piece_manager, self.file_handler)
                m.start()
                self.peer_list.append(m)
    
    def peer_in_list(self, ip, port):
        for peer in self.peer_list:
            if peer.address == (ip, port):
                return True
        return False

    def _create_tracker(self):
        for tiers in self.data.announces: 
            for announce in tiers:
                tracker = give_object(announce, self.data.info_hash, self.peer_id, Swarm.LISTEN_PORT, self.tracker_limit)
                self.tracker_list.append(tracker)