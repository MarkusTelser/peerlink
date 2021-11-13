from peer_protocol.Peer import Peer
from TorrentParser import TorrentParser
from trackers.UDPTracker import UDPTracker
from random import choice
from string import ascii_letters
import traceback

# load data from torrent
fp = "../data/all/testtest.torrent"
parser = TorrentParser(filepath=fp)
data = parser.parse()



ip = "5.79.98.220"
port = 48080
p = Peer(ip, port)
peer_id = bytes("-qB3090-" + ''.join(choice(ascii_letters) for _ in range(12)), 'utf-8')

handshake = p.bld_handshake(data.info_hash, peer_id)
p.send_msg(handshake)
p.recv_handshake(data.info_hash, peer_id)

try:
    r = p.recv_msg()
    print("received",r)
except Exception as e:
    import traceback
    traceback.print_exception(e)
    print("1",e)


interested = p.bld_interested()
p.send_msg(interested)
try:
    recv = p.recv_msg()
    print("received 2", recv)
except Exception as e:
    print("3", e)

for i in range(32):
    request = p.bld_request(0, i * 2 ** 16, 2 ** 16)
    p.send_msg(request)
    try:
        recv = p.recv_msg()
        index, begin, block = recv
        print("block id", i, "block", block[:10], len(block))
        with open("test.file", "ab") as f:
            f.write(block)
    except Exception as e:
        traceback.print_exc(e)
        print("4", e)

