import socket
import random
import string
    

from TorrentParser import TorrentParser
from Torrent import getHashInfo
from trackers import UDPTracker, HTTPTracker
from ipaddress import ip_address
from peer import Peer

# create torrent parser
t = TorrentParser(filepath="../test.torrent")
#t = TorrentParser(filepath="../data/httptorrents/test4.torrent")
t.getData()
t.getDebugInformation()



def main(con):
    if con == "http" or con == "https":
        adr_url = t.data["announce"]
        print(adr_url)
        tracker = HTTPTracker.HTTPTracker(adr_url)

        info_hash = getHashInfo(t.data["info"])
        peer_id = ''.join(random.choice(string.ascii_letters) for _ in range(20))
        port = 0
        uploaded = "0"
        downloaded = "0"
        left = "1000"
        recv = tracker.request(info_hash, peer_id, port, uploaded, downloaded, left)

        if len(recv["peers"]) != 0:
            ip = recv["peers"][0]["ip"]
            peer_id = recv["peers"][0]["peer id"]
            port = int(recv["peers"][0]["port"])

            p = Peer(ip, port)
            p.handshake(info_hash, peer_id)

    elif con == "udp":
        adr = t.data["announce"].split("/")[2].split(":")[0]
        port = int(t.data["announce"].split("/")[2].split(":")[1])
        # sample data
        adr = "tracker.torrent.eu.org"
        port = 451

        tracker = UDPTracker.UDPTracker(adr, port)
        res = tracker.connect()
        if res != None:
            cid = res
            info_hash = bytes(getHashInfo(t.data["info"]), 'utf-8')
            peer_id = UDPTracker.UDPTracker.gen_pid()
            downloaded = 0
            left = 0
            uploaded = 1000
            event = UDPTracker.Events.STARTED.value
            ip = int.from_bytes(ip_address(socket.gethostbyname(adr)).packed, byteorder='big')
            key = 123
            num_want = 10
            port = port
            
            
            tracker.announce(cid, info_hash, peer_id, downloaded, left, uploaded, event, key, port, ip, num_want)


# maybe skip announce, because is also in announce-list
con = t.data["announce"].split(":")[0]
try:
    main(con)
except Exception as e:
    print(e)

# go through rest of list
if "announce-list" in t.data:
    for announce in t.data["announce-list"]:
        con = announce[0].split(":")[0]
        try:
            main(con)
        except Exception as e:
            print(e)


"""
from src.trackers import UDPTracker
adr = "tracker.torrent.eu.org"
port = 451
udp = UDPTracker(adr, port)
cid = udp.connect()
udp.announce(cid, )
"""
