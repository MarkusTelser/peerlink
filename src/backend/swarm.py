from queue import Queue
from threading import Thread
from src.backend.trackers.HTTPTracker import HTTPTracker
from threading import BoundedSemaphore
from src.backend.trackers.UDPTracker import UDPTracker

from .peer_protocol.PeerIDs import PeerIDs
from .peer_protocol.PieceManager import PieceManager
from .FileHandler import FileHandler
from .trackers.Tracker import give_object
from .peer_protocol.Peer import Peer

class Swarm:
    MAX_TRACKER = 100
    MAX_PEERS = 70
    
    def __init__(self, data, path) -> None:
        self.data = data
        self.path = path
        self.backup_name = ""
        self.announces = data.announces
        self.info_hash = data.info_hash
        self.piece_manager = PieceManager(data.pieces_count)
        self.file_handler = FileHandler(data, path)
        
        self.peer_limit = BoundedSemaphore(value=Swarm.MAX_PEERS)
        self.tracker_limit = BoundedSemaphore(value=Swarm.MAX_TRACKER)
        self.peer_list = list()
        self.tracker_list = list()
        self.finished_tracker = Queue()
        
        self.start_thread = None
    
    def start(self):
        try:
            self.init_tracker()
            self.announce_tracker()
            self.connect_peers()
        except Exception:
            raise Exception('crashed')
    
    def init_tracker(self):
        print(self.announces)
        
        for tiers in self.announces: 
            for announce in tiers:
                tracker = give_object(announce, self.info_hash, self.tracker_limit, self.finished_tracker)
                if tracker != None:
                    self.tracker_list.append(tracker)
    
    def announce_tracker(self):     
        # wait until previous announces are done
        self.finished_tracker.join()
            
        for t in self.tracker_list:
            thread = Thread(target=t.announce)
            thread.start()
            

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
