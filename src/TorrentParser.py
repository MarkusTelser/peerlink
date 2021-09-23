from os.path import exists
from bencode import decode
from datetime import datetime

# remove after
import json

class TorrentParser:
    def __init__(self, file=None, filepath=None):
        self.file = file
        self.filepath = filepath
        self.data = None

    def main(self):
        if self.evaluate():
            self.getData()

    def getData(self):
        if self.filepath != None:
            print(self.filepath)
            if exists(self.filepath):
                with open(self.filepath, "rb") as f:
                    encry = f.read()
                self.data = decode(encry)
            else:
                print("Error: File doesnt exist")
        elif self.file != None:
            encry = self.file.read()
            self.data = decode(encry)
        else:
            print("Error: No File or Filepath provided")

    def evaluate(self):
        if self.data == None:
            print("Error: No data loaded")
        try:
            keys = list(self.data.keys())
            # some torrents dont follow standards and use announce-list only
            if "announce" in self.data or "announce-list" in self.data:
                if "announce" in self.data:
                    keys.remove("announce")
                if "announce-list" in self.data:
                    keys.remove("announce-list")
            else:
                print("Error: Neither announce nor announce-list in torrent")
            if "created by" in self.data:
                keys.remove("created by")
            if "creation date" in self.data:
                keys.remove("creation date")
            if "comment" in self.data:
                keys.remove("comment")
            if "encoding" in self.data:
                keys.remove("encoding")
            # peers for DHT
            if "nodes" in self.data:
                keys.remove("nodes")
           
            
            if "info" in self.data:
                del self.data.get("info")["pieces"]
                print(self.data.get("info"))
            else:
                print("Error: Doesnt contain info in torrent")
            
            # print the remaining keys
            for item in keys:
                print(self.data[item])
            print(keys)
            
        except KeyError:
            print("Error: Key doesn't exist")

    def getDebugInformation(self):
        print(json.dumps(self.data, indent=4, sort_keys=True))
        #print("Announce: ", self.data['announce'])
        print("Info: ", self.data['info'])
        if "announce-list" in self.data:
            print("Announce-List: ", self.data["announce-list"][:3])
        if "creation date" in self.data:
            print("Creation date: ", datetime.fromtimestamp(self.data["creation date"]))
        if "created by" in self.data:
            print("Created by:", self.data["created by"])
        if "comment" in self.data:
            print("Comment: ", self.data["comment"])
        
        info = self.data
        del info["info"]["pieces"]
        if "announce-list" in info:
            del info["announce-list"][3:]
        print(json.dumps(info, indent=4, sort_keys=True))

    def has_multi_file(self):
        if "files" in self.data["info"]:
            return True
        elif "length" in self.data["info"]:
            return False
        else:
            print("Error: Incorrect Format")

    def get_files(self):
        pass

import os
for file in os.listdir("../data/all"):
    filepath = os.path.join("../data/all", file)
    parse = TorrentParser(filepath=filepath)
    parse.getData()
    parse.evaluate()
