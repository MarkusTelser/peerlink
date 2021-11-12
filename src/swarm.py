from peer_protocol.PeerIDs import PeerIDs
from trackers.Tracker import Tracker
from peer_protocol.Peer import Peer

class Swarm:
    def __init__(self) -> None:
        self.peers = list()

    def connect_trackers(self, announces, info_hash, info_hash_quoted):
        threads = []
        for announce in announces: 
            t = Tracker(announce, info_hash, info_hash_quoted)
            threads.append(t)
            t.start()

        for thread in threads:
            thread.join()

        print("-"*30)
        peers = list()
        for thread in threads:
            if thread.successful:
                if thread.peers:
                    for peer in thread.peers:
                        peers.append(peer)
            else:
                print(thread.error, thread.link)
        print("-" * 30)
        print(peers)
        self.peers = peers

    
    def connect_peers(self, info_hash):
        threads = []

        for peer in self.peers:
            address = peer
            peer_id = PeerIDs.generate()
            p = Peer(address, info_hash, peer_id)
            p.start()
            threads.append(p)
