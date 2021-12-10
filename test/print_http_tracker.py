import os
from src.backend.metadata.TorrentParser import TorrentParser

for file in os.listdir("data/all/"):    
    data = TorrentParser.parse_filepath(f"data/all/{file}")
    
    count = 0
    #print(data.announces)
    for tiers in data.announces:
        for tracker in tiers:
            if tracker.startswith("http") or tracker.startswith("https"):
                count += 1
    
    print(f"{count} http/https tracker : {file}")
