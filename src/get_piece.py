from peer_protocol.peer import Peer
from TorrentParser import TorrentParser
from trackers.UDPTracker import UDPTracker
from random import choice
from string import ascii_letters

# load data from torrent
fp = "../data/all/testtest.torrent"
parser = TorrentParser(filepath=fp)
data = parser.parse()



ip = "5.79.98.220"
port = 48080
p = Peer(ip, port)
peer_id = bytes("-qB3090-" + ''.join(choice(ascii_letters) for _ in range(12)), 'utf-8')

p.send_handshake(data.info_hash, peer_id)
p.recv_handshake(data.info_hash, peer_id)

try:
    r = p.recv()
    print("received",r)
except Exception as e:
    print("1",e)

try:
    r = p.recv()
    print("received",r)
except Exception as e:
    print("2",e)

p.send_interested()
try:
    recv = p.recv()
    print("received 2", recv)
except Exception as e:
    print("3", e)

p.send_request(0, 0, 2**14)
try:
    recv = p.recv()
    print("received 3", recv)
except Exception as e:
    print("4", e)

try:
    recv = p.recv()
    print("received 3", recv)
except Exception as e:
    print("4", e)

try:
    recv = p.recv()
    print("received 3", recv)
except Exception as e:
    print("4", e)

try:
    recv = p.recv()
    print("received 3", recv)
except Exception as e:
    print("4", e)