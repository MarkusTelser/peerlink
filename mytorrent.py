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

def readTorrentFile():
    with open(file, "rb") as f:
        encrypted = f.read()

    data = bencode.decode(encrypted)
  
    # extract data
    announce = data["announce"]
    con = announce.split("/")[0][:-1]
    typ = announce.split("/")[3]
    adr = announce.split("/")[2]
    hasPortDefined = adr.find(":") != -1
    
    # for trackers
    uploaded = "0"
    downloaded = "0"
    left = "2000"
    info_hash = getHashInfo(data)
    port = int(adr.split(":")[1]) if hasPortDefined else 6969
    ip = adr.split(":")[0] if hasPortDefined else adr
    peer_id = ''.join(random.choice(string.ascii_letters) for _ in range(20))

    # debug
    printTorrentFile(data)

    if typ == "announce":
        if con == "udp":
            trackerUPS(ip, port)
        if con == "http":
            trackerHTTP(announce, info_hash, peer_id, port, uploaded, downloaded, left)

    for i in range(3):
        announce = data["announce-list"][i][0]
        print(announce)
        ip = announce.split("/")[2].split(":")[0]
        port = announce.split("/")[2].split(":")[1]
        print(ip, port)
        trackerHTTP(announce, info_hash, peer_id, port, uploaded, downloaded, left)

def printTorrentFile(data):
    print(data.get("info").keys())
    print("Announce: ", data.get("announce"))
    print("Announce-List: ", data.get("announce-list")[:3])
    print("Comment: ", data.get("comment"))
    print("Created by:", data.get("created by"))
    print("Creation date: ", datetime.fromtimestamp(data.get("creation date")))
    info = data.get("info")
    del info["pieces"]
    print(json.dumps(info, indent=4, sort_keys=True))
    

def getHashInfo(data):
    """
    info = lt.torrent_info(open(file,'rb').read())
    info_hash = str(info.info_hash())
    asci = codecs.decode(info_hash, "hex")
    ret = urllib.parse.quote_plus(asci)
    print(ret)
    """

    info = data.get("info")
    encoded = bencode.encode(info)
    hex_enc = hashlib.sha1(encoded).hexdigest()
    ascii_dec = codecs.decode(hex_enc, "hex")
    url_encode = urllib.parse.quote_plus(ascii_dec)
    
    return url_encode


def trackerHTTP(addr, info_hash, peer_id, port, uploaded, downloaded, left, ip=None, event=None, numwant=None, no_peer_id=None, compact=None):
    params = ""

    # required parameters
    params += f"info_hash={info_hash}"
    params += f"&peer_id={peer_id}"
    params += f"&port={port}"
    params += f"&uploaded={uploaded}"
    params += f"&downloaded={downloaded}"
    params += f"&left={left}"
    
    # optional parameters
    if ip is not None:
        params += f"&ip={ip}"
    if event is not None:
        params += f"&event={event}"
    if numwant is not None:
        params += f"&numwant={numwant}"
    if no_peer_id is not None:
        params += "&no_peer_id={no_peer_id}"
    if compact is not None:
        params += "&compact={compact}"

    url = f"{addr}?{params}"
    recv = requests.get(url)
    
    """
    failure_code key that tracker might send back:

    100	Invalid request type: client request was not a HTTP GET.
    101	Missing info_hash.
    102	Missing peer_id.
    103	Missing port.
    150	Invalid infohash: infohash is not 20 bytes long.
    151	Invalid peerid: peerid is not 20 bytes long.
    152	Invalid numwant. Client requested more peers than allowed by tracker.
    200	info_hash not found in the database. Sent only by trackers that do not automatically include new hashes into the database.
    500	Client sent an eventless request before the specified time.
    900	Generic error.
    """
    

    print("full url: ", url)
    answer = bencode.decode(recv.text)
    print(json.dumps(answer, indent=4, sort_keys=True))
    print(recv.status_code)

    recv.close()
    
    peers = answer.get("peers")
    
    """
    for peer in peers:
        peerTCP(peer["ip"], peer["port"], peer["peer id"])
    """

def trackerUPS(adr, port):
    UDP_IDENTIFICATION = 0x41727101980
    TID = random.randint(0, 0xffffffff)
    BUFFER_SIZE = 4096
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(10)
    ip = socket.gethostbyname(adr)
    tracker_adr = (ip, port)
    
    msg = struct.pack('!QII', UDP_IDENTIFICATION, 0, TID)
    send = sock.sendto(msg, tracker_adr)
    print(send)
    
    recv, server = sock.recv(BUFFER_SIZE)
    if len(recv) < 8:
        print("invalid")
    print(recv)

def peerTCP(ip, port, pid):
    MESSAGE = "Hello, World!"

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((ip, port))
    s.send(MESSAGE)
    data = s.recv(BUFFER_SIZE)
    s.close()

    print(data)


for i in range(20):
    file = f"udptorrents/test{i}.torrent"
    #file = f"udptorrents/test3.torrent"
    try:
        readTorrentFile()
    except Exception as e:
        print(e)
