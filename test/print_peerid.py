import src.backend.metadata
from src.backend.metadata import TorrentParser
from src.backend.swarm import Swarm
fp = "data/all/testtest.torrent"
data = TorrentParser.parse_filepath(fp)
print(data)
s = Swarm(data)
s.connect_trackers(data.announces, data.info_hash, data.info_hash_quoted)
s.connect_peers(data.info_hash)
