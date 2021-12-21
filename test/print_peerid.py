from src.backend.metadata import TorrentParser
from src.backend.swarm import Swarm

#fp = "data/all/The Martian (2015).torrent"
#fp = "data/all/test0.torrent"
#fp = "data/all/The Impossible (2012).torrent"
#fp = "data/all/test12.torrent"
#fp = "data/all/manjaro.torrent"
fp = "data/all/ubuntu.torrent"

data = TorrentParser.parse_filepath(fp)

s = Swarm(data)
s.init_tracker()
s.announce_tracker()
s.connect_peers(data.info_hash)
