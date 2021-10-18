from TorrentParser import TorrentParser
from trackers.HTTPTracker import HTTPTracker
from trackers.UDPTracker import UDPTracker, UDPEvents
from peer_protocol.peer import Peer


def http_communication(data, announce):
    adress = data.getLinkFromAnnounce(announce) 
    tracker = HTTPTracker(adress)

    info_hash = data.info_hash_quoted
    peer_id = data.gen_peer_id()
    
    # demo values
    port = 0
    uploaded = "0"
    downloaded = "0"
    left = "1000"

    recv = tracker.request(info_hash, peer_id, port, uploaded, downloaded, left)

    if recv != None and len(recv["peers"]) != 0:
        return recv
    else:
        return False


def udp_communication(data, announce):
    adress = data.getLinkFromAnnounce(announce)
    port = data.getPortFromAnnounce(announce)
    tracker = UDPTracker(adress, port)
    
    result = tracker.connect()

    if result != None:
        cid = result
        info_hash = data.info_hash
        peer_id = UDPTracker.gen_pid()
        event = UDPEvents.STARTED.value

        # demo values
        downloaded = 0
        left = 0
        uploaded = 0
        num_want = 500
        # if not given
        ip = 0
        port = 0
        key = 0
        
        results = tracker.announce(cid, info_hash, peer_id, downloaded, left, uploaded, event, key, port, ip, num_want)
        tracker.close_con()

        if result != None:
            return results
        else:
            return False
            

def peer_communication(ip, port, info_hash):
    peer_id = UDPTracker.gen_pid()
    p = Peer(ip, port)
    p.send_handshake(info_hash, peer_id)
    pid = p.recv_handshake(info_hash, peer_id)
    p.recv()
    p.send_interested()
    p.recv()
    

# load data from torrent
from Torrent import TorrentData
fp = "../data/all/testtest.torrent"
parser = TorrentParser(filepath=fp)
data = parser.parse()

from concurrent.futures import ThreadPoolExecutor

# create all threads and communicate to tracker
print("-"*30)
futures = []
with ThreadPoolExecutor(max_workers=50) as executor:
    for i, announce in enumerate(data.announces):
        print(announce)
        ann = data.getAnnounceConnection(announce)
        if ann == "http" or ann == "https":
            future = executor.submit(http_communication, data, announce)
            futures.append(future)
        elif ann == "udp":
            future = executor.submit(udp_communication, data, announce)
            futures.append(future)
        else:
            print("Unknown tracker type:", ann)
    executor.shutdown(wait=True)
print("-" * 30)


# get peers back
print("-" * 30)
peer_list = set()
for future in futures:
    f = future.exception()
    if f == None:
        if type(future.result()) == list:
            for res in future.result():
                peer_list.add(res)
    else:
        print("exception tracker", f)
print("-" * 30)


# iterate over peers
print("-" * 30)
futures = []
with ThreadPoolExecutor(max_workers=500) as executor:
    for peer in peer_list:
        ip, port = peer
        future = executor.submit(peer_communication, ip, port, data.info_hash)
        futures.append(future)
    executor.shutdown(wait=True)
print("-" * 30)


# get working ones
print("-" * 30)
for future in futures:
    f = future.exception()
    if f == None:
        print(f)
    else:
        print("exception peer", f)
print("-" * 30)


"""
In the future maybe implement WebSocket trackers:
- ws connects only to via http without SSL
- wss connects only to via https with SSL
https://stackoverflow.com/questions/46557485/difference-between-ws-and-wss
"""
