from queue import Queue
from threading import Thread
from src.backend.trackers.HTTPTracker import HTTPTracker

from src.backend.trackers.UDPTracker import UDPTracker

from .peer_protocol.PeerIDs import PeerIDs
from .peer_protocol.PieceManager import PieceManager
from .FileHandler import FileHandler
from .trackers.Tracker import give_object
from .peer_protocol.Peer import Peer

class Swarm:
    MAX_TRACKER = 50
    MAX_PEERS = 70
    
    def __init__(self, data) -> None:
        self.peers = list()

        self.data = data
        self.announces = data.announces
        self.info_hash = data.info_hash
        self.piece_manager = PieceManager(data.pieces_count)
        self.file_handler = FileHandler(data, "downloaded.file")
        
        self.start_tracker = Queue(maxsize=Swarm.MAX_TRACKER)
        self.finished_tracker = Queue()
        self.tracker_list = list()

    def init_tracker(self):
        print(self.announces)
        
        for tiers in self.announces: 
            for announce in tiers:
                tracker = give_object(announce, self.info_hash, self.start_tracker, self.finished_tracker)
                if tracker != None:
                    self.tracker_list.append(tracker)
    
    def announce_tracker(self):     
        # wait until previous announces are done
        self.start_tracker.join()
        self.finished_tracker.join()
            
        for t in self.tracker_list:
            thread = Thread(target=t.announce)
            self.start_tracker.put(thread)
            thread.start()
        
        finished = 0
        while finished != len(self.tracker_list):
            t = self.finished_tracker.get()
            finished += 1
        
        print("-"*30)
        for tracker in self.tracker_list:
            if tracker.error == None:
                if type(tracker) == HTTPTracker:
                    print(tracker.url, tracker.peers)
                else:
                    print(tracker.host, tracker.port, tracker.peers)
            else:
                print(tracker.error)
            

    def connect_peers(self, info_hash):
        finished = 0
        while finished != count:
            item = finished_tracker.get()
            finished += 1
            print(item, "finished")
