import logging
from src.backend.metadata import MagnetLink
from src.backend.peer_protocol.MetadataManager import MetadataManager
from src.backend.trackers.HTTPTracker import HTTPEvents
from asyncio import BoundedSemaphore
from datetime import datetime

from src.backend.utils.SpeedMeasurer import SpeedMeasurer

from .peer_protocol.PeerIDs import PeerIDs
from .peer_protocol.PieceManager import PieceManager
from .FileHandler import FileHandler
from .trackers.Tracker import give_object
from .peer_protocol.Peer import MPeer
import asyncio

class Swarm:
    MAX_TRACKER = 100
    MAX_PEERS = 70
    LISTEN_PORT = 6881
    
    def __init__(self) -> None:
        self.data = None
        self.magnet_link = None
        
        self.path = ""
        self.peer_id = PeerIDs.generate()
        self.category = ""
        self.backup_name = ""
        self.start_date = ""
        self.finish_date = ""
        
        self.piece_manager = None
        self.file_handler = None
        self.metadata_manager = None
        
        self.start_task = None
        self.tracker_limit = BoundedSemaphore(value=Swarm.MAX_TRACKER)
        self.peer_limit = BoundedSemaphore(value=Swarm.MAX_PEERS)
        self.tracker_list = list()
        self.peer_list = list()
    
    def set_meta_data(self, data, path):
        self.data = data
        self.path = path
        self.piece_manager = PieceManager(data.pieces_count, data.piece_length)
        self.file_handler = FileHandler(data, path)
        self.speed_measurer = SpeedMeasurer(self.piece_manager)
        self._create_tracker(self.data.announces, self.data.info_hash)
    
    def set_magnet_link(self, magnet_link: MagnetLink):
        self.magnet_link = magnet_link
        self.metadata_manager = MetadataManager(self.magnet_link.info_hash, self.finished_metadata)
        self._create_tracker([list(self.magnet_link.trackers)], self.magnet_link.info_hash)
    
    def finished_metadata(self):
        print('PENIS' * 100)
        print(len(self.metadata_manager._data), self.metadata_manager.full_size)
        pass
    
    def start(self):
        self.start_task = asyncio.create_task(self._start())
    
    async def _start(self):
        try:
            if len(self.start_date) == 0:
                self.start_date = datetime.now().isoformat()
            asyncio.create_task(self.speed_measurer.execute())
            asyncio.create_task(self._print_speed())
            await self.announce_trackers(HTTPEvents.STARTED)
        except Exception as e:
            logging.exception('error in swarm')
            print(e)
            raise Exception('crashed') 
    
    async def _print_speed(self):
        while True:
            print('-' * 100)
            print(self.speed_measurer.avg_down_speed)
            print('-' * 100)
            await asyncio.sleep(1)
        
    
    async def download_metadata(self):
        print(self.magnet_link.trackers)
        await self.announce_trackers()
    
    async def pause(self):
        if self.start_task:
            self.start_task.cancel()
        
        for tracker in self.tracker_list:
            tracker.pause()
        
        for peer in self.peer_list:
            peer.pause()
        
        await self.announce_trackers(HTTPEvents.STOPPED)
    
    async def announce_trackers(self, event=None):
        tasks = list()
        for tracker in self.tracker_list:
            if self.magnet_link:
                uploaded =  0
                downloaded = 0
                left = self.magnet_link.size
            elif self.data:
                uploaded =  self.piece_manager.uploaded_bytes
                downloaded = self.piece_manager.downloaded_bytes
                left = self.piece_manager.left_bytes
            else:
                raise Exception('Cannot announce no torrent/link given')
            
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
            for address in future.result():
                if self.peer_in_list(address[0], address[1]):
                    #print('already in peer list', peer, len(self.peer_list))
                    continue
                
                info_hash = self.magnet_link.info_hash if self.magnet_link else self.data.info_hash
                
                m = MPeer(address, info_hash, self.peer_id)
                if self.magnet_link:
                    asyncio.create_task(m.request_metadata(self.metadata_manager))
                else:
                    m.set_torrent(self.piece_manager, self.file_handler)
                    asyncio.create_task(m.resume())
                self.peer_list.append(m)
    
    def peer_in_list(self, ip, port):
        for peer in self.peer_list:
            if peer.address == (ip, port):
                return True
        return False

    def _create_tracker(self, trackers: list, info_hash):
        for tiers in trackers: 
            for announce in tiers:
                tracker = give_object(announce, info_hash, self.peer_id, Swarm.LISTEN_PORT, self.tracker_limit)
                self.tracker_list.append(tracker)