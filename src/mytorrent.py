import struct
import bencode
import codecs
import socket
import requests
import urllib
import hashlib
import random
import string
import libtorrent as lt
import json
from datetime import datetime
    



def peerTCP(ip, port, pid):
    MESSAGE = "Hello, World!"

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((ip, port))
    s.send(MESSAGE)
    data = s.recv(BUFFER_SIZE)
    s.close()

    print(data)



#file = f"udptorrents/test3.torrent"

"""
for i in range(20):
    file = f"udptorrents/test{i}.torrent"
    try:
        readTorrentFile()
    except Exception as e:
        print(e)
"""

from TorrentParser import TorrentParser
from Torrent import getHashInfo
from trackers import UDPTracker, HTTPTracker
from ipaddress import ip_address

# create torrent parser
t = TorrentParser(filepath="../data/udptorrents/test0.torrent")
t.getData()
t.getDebugInformation()

# connect to tracker
con = t.data["announce"].split(":")[0]
if con == "http":
    pass
elif con == "udp":
    adr = t.data["announce"].split("/")[2].split(":")[0]
    port = int(t.data["announce"].split("/")[2].split(":")[1])
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

hash_info = getHashInfo(t.data)





"""
from src.trackers import UDPTracker
adr = "tracker.torrent.eu.org"
port = 451
udp = UDPTracker(adr, port)
cid = udp.connect()
udp.announce(cid, )
"""
