from trackers.UDPTracker import UDPTracker
from trackers.HTTPTracker import HTTPTracker
from TorrentParser import TorrentParser
from concurrent.futures import ThreadPoolExecutor

fp = "../data/all/testtest.torrent"
parser = TorrentParser(filepath=fp)
data = parser.parse()

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
        return result
    else:
        return False


http_trackers = 0
udp_trackers = 0
rest = set()
for announce in data.announces:
    ann = data.getAnnounceConnection(announce)
    if ann == "udp":
        udp_trackers += 1
    elif ann == "http" or ann == "https":
        http_trackers += 1
    else:
        rest.add(ann)
print("so many http/s connections", http_trackers)
print("so many udp connections", udp_trackers)
print("these are other connections", rest, ) if len(rest) != 0 else ""
print("-" * 30)

future_list = []
with ThreadPoolExecutor(max_workers=50) as executor:
    for announce in data.announces:
        print(announce)
        ann = data.getAnnounceConnection(announce)
        if ann == "udp":
            future = executor.submit(udp_communication, data, announce)
            future_list.append(future)
        elif ann == "http" or ann == "https":
            future = executor.submit(http_communication, data, announce)
            future_list.append(future)
        else:
            raise Exception("unknown tracker type:", ann)


    executor.shutdown(wait=True)

print("-"*30)
worked = 0
for future in future_list:
    f = future.exception()
    if f == None:
        if future.result() != False:
            worked += 1
            print(future.result())
    else:
        print("has exception", f)

print("-" * 30)
print(worked, "trackers work from", len(data.announces))