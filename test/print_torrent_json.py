from src.backend.metadata.Bencoder import decode
from json import dumps

fp = "data/all/folder.torrent"

with open(fp, "rb") as f:
    raw_data = f.read()
data = decode(raw_data)

print(data["info"]["pieces"][:20])
del data["info"]["pieces"]

print(dumps(data, indent=4))
