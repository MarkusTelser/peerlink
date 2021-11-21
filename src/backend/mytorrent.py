from concurrent.futures import ThreadPoolExecutor
from Torrent import TorrentData
from TorrentParser import TorrentParser
from trackers.Tracker import Tracker
import socket

# load data from torrent
fp = "../data/all/testtest.torrent"
data = TorrentParser.parse_filepath("../data/all/testtest.torrent")


def get_peer_list():
    # create all threads and communicate to tracker
    threads = []
    for announce in data.announces: 
        t = Tracker(announce, data)
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
    return peers

peers = get_peer_list()

"""
def peer_communication(ip, port, info_hash):
    peer_id = UDPTracker.gen_pid()
    p = Peer(ip, port)
    p.send_handshake(info_hash, peer_id)
    pid = p.recv_handshake(info_hash, peer_id)
    print(ip, port)
    try:
        r = p.recv()
        #print("recv1", r)
    except Exception as e:
        pass
        #print("ok ", e)
    
    try:
        p.send_interested()
        r2 = p.recv()
        print(ip, port, "recv2", r2)
    except Exception as e:
        pass
        #print("finally after interested", e)


futures = []
with ThreadPoolExecutor(max_workers=500) as executor:
    for ip, port in peer_list:
        future = executor.submit(peer_communication, ip, port, data.info_hash)
        futures.append(future)
    executor.shutdown(wait=True)


print("-"*30)
for future in futures:
    f = future.exception()
    if f == None:
        print(future.result())
    else:
        print("exception peer:",f)
print("-"*30)



In the future maybe implement WebSocket trackers:
- ws connects only to via http without SSL
- wss connects only to via https with SSL
https://stackoverflow.com/questions/46557485/difference-between-ws-and-wss
"""