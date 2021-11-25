from json import encoder
import bencode
from collections import OrderedDict
import json

with open("../../../data/all/test.torrent",'rb') as f:
    data = f.read()

d = bencode.decode(data)
del d.get("info")["pieces"]

print(json.dumps(d, indent=4, sort_keys=True))
