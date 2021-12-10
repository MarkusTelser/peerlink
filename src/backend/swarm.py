from .peer_protocol.PeerIDs import PeerIDs
from .peer_protocol.PieceManager import PieceManager
from .FileHandler import FileHandler
from .trackers.Tracker import Tracker
from .peer_protocol.Peer import Peer

class Swarm:
    def __init__(self, data) -> None:
        self.peers = list()

        self.data = data
        self.piece_manager = PieceManager(data.pieces_count)
        self.file_handler = FileHandler(data, "downloaded.file")

    def connect_trackers(self, announces, info_hash, info_hash_quoted):
        threads = []
        print(announces)
        for tiers in announces: 
            for announce in tiers:
                t = Tracker(announce, info_hash, info_hash_quoted)
                threads.append(t)
                t.start()

        for thread in threads:
            thread.join()

        print("-"*30)
        print("Errors:")
        peers = list()
        for thread in threads:
            if thread.successful:
                if thread.peers:
                    for peer in thread.peers:
                        peers.append(peer)
            else:
                print("error: ", thread.error, thread.link)
        print("-" * 30)
        
        print("working trackers:")
        for thread in threads:
            if thread:
                if thread.successful:
                    print(thread.link, len(thread.peers))
        print("amount of peers:", len(peers))
        print("-" * 30)
        
        print(peers)
        self.peers = peers

    
    def connect_peers(self, info_hash):
        threads = []

        for peer in self.peers:
            address = peer
            peer_id = PeerIDs.generate()
            p = Peer(address, peer_id, self.data, self.piece_manager, self.file_handler)
            p.start()
            threads.append(p)

        for thread in threads:
            thread.join()
        
        self.piece_manager.sort_rarest()
        print(self.piece_manager.pieces)
