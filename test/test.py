from src.backend.metadata import TorrentParser

data = TorrentParser.parse_filepath("data/all/solo.torrent")

print(data.info_hash)
print(data.info_hash_hex)
