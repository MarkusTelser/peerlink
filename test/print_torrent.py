from json import encoder
from src.backend.metadata.TorrentParser import TorrentParser
from src.backend.metadata.Bencoder import bdecode
from collections import OrderedDict
import json
import os


for item in os.listdir("data/all"):
    with open(f"data/all/{item}",'rb') as f:
        data = f.read()
    
    d = bdecode(data)
    
    del d.get("info")["pieces"]
    if "magnet-info" in d:
        del d.get("magnet-info")["info_hash"]
    # print(d)
    
    # remove standard keys
    del d["info"]
    if "announce" in d:
        del d["announce"]
    if "announce-list" in d:
        for tiers in d.get("announce-list"):
            for announce in tiers:
                if "?" in announce:
                    print(announce)
        del d["announce-list"]
    if "created by" in d:
        del d["created by"]
    if "creation date" in d:
        del d["creation date"]
    if "comment" in d:
        del d["comment"]
    if "encoding" in d:
        del d["encoding"]

    print(json.dumps(d, indent=4, sort_keys=True))


"""
with open("../../../data/all/testtest.torrent", "rb") as f:
    data = f.read()

d = bencode.bdecode(data)

del d.get("info")["pieces"]
print(json.dumps(d, indent=4, sort_keys=True))
"""
