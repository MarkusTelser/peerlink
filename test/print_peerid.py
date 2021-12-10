import src.backend.metadata
from src.backend.metadata import TorrentParser
from src.backend.swarm import Swarm

#fp = "data/all/The Martian (2015).torrent"
#fp = "data/all/test0.torrent"
#fp = "data/all/The Impossible (2012).torrent"
fp = "data/all/test12.torrent"

data = TorrentParser.parse_filepath(fp)

s = Swarm(data)
s.connect_trackers(data.announces, data.info_hash, data.info_hash_quoted)
#s.connect_peers(data.info_hash)
