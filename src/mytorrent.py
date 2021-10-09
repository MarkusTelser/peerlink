import socket
    

from TorrentParser import TorrentParser
from trackers.HTTPTracker import HTTPTracker
from trackers.UDPTracker import UDPTracker, UDPEvents
from ipaddress import ip_address
from peer_protocol.peer import Peer

import os
from hashlib import sha1
from codecs import decode

#def main(con, ann):
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
        print(recv)
        ip = recv["peers"][0]["ip"]
        peer_id = recv["peers"][0]["peer id"]
        port = int(recv["peers"][0]["port"])
        
        p = Peer(ip, port)
        p.handshake(info_hash, peer_id)


def udp_communication(data, announce):
    adress = data.getLinkFromAnnounce(announce)
    port = data.getPortFromAnnounce(announce)
    tracker = UDPTracker(adress, port)
    
    result = tracker.connect()
    print(result)

    if result != None:
        cid = result
        info_hash = data.info_hash
        peer_id = UDPTracker.gen_pid()
        event = UDPEvents.STARTED.value
        print(info_hash,"||", data.info_hash, "||")
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
            for result in results:
                ip, port = result
                p = Peer(ip, port)
                try:
                    p.handshake(info_hash, peer_id)
                except Exception as e:
                    print(e)

# test part
from Torrent import TorrentData

#for file in os.listdir("../data/all/"):
#fp = "../data/all/lotseed.torrent" #+ file
fp = "../data/all/testtest.torrent"
parser = TorrentParser(filepath=fp)
data = parser.parse()

for announce in data.announces:
    print(announce)
    ann = data.getAnnounceConnection(announce)
    """
    if ann == "http" or ann == "https":
        black_list = ["tracker.tfile.co", "inferno.demonoid.me"]
        if all(link not in announce for link in black_list):
            http_communication(data, announce)
    """
    if ann == "udp":
        try:
            udp_communication(data, announce)
        except Exception as e:
            print(e)
#break 
