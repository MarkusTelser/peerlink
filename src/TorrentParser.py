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

    def main():
        if self.evaluate():
            self.getData()

    def getData(self):
        if self.filepath != None:
            if exists(self.filepath):
                with open(self.filepath, "rb") as f:
                    encry = f.read()
                print(encry)
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
            self.data["announce"]
            self.data["info"]
            
        except KeyError:
            print("Error: Key doesn't exist")

    def getDebugInformation(self):
        print("Announce: ", self.data['announce'])
        print("Announce-List: ", self.data["announce-list"])
        print("Comment: ", self.data["comment"])
        print("Created by:", self.data["created by"])
        print("Creation date: ", datetime.fromtimestamp(self.data["creation date"]))
        info = self.data
        del info["info"]["pieces"]
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
    """
    # extract data
    announce = data["announce"]
    con = announce.split("/")[0][:-1]
    typ = announce.split("/")[3]
    adr = announce.split("/")[2]
    hasPortDefined = adr.find(":") != -1
                                                      
    # for trackers
    uploaded = "0"
    downloaded = "0"
    left = "2000"
    info_hash = getHashInfo(data)
    port = int(adr.split(":")[1]) if hasPortDefined else 6969
    ip = adr.split(":")[0] if hasPortDefined else adr
    peer_id = ''.join(random.choice(string.ascii_letters) for _ in range(20))
    
    # debug
    printTorrentFile(data)

    if typ == "announce":
        if con == "udp":
            trackerUPS(ip, port)
        if con == "http":
            trackerHTTP(announce, info_hash, peer_id, port, uploaded, downloaded, left)

            for i in range(3):
                announce = data["announce-list"][i][0]
                print(announce)
                ip = announce.split("/")[2].split(":")[0]
                port = announce.split("/")[2].split(":")[1]
                print(ip, port)
                trackerHTTP(announce, info_hash, peer_id, port, uploaded, downloaded, left)
    """
