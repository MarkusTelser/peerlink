from os.path import exists
from bencode import decode
from datetime import datetime
from Torrent import TorrentData, TorrentFile

class TorrentParser:
    def __init__(self, file=None, filepath=None):
        self.file = file
        self.filepath = filepath
        self.data = None

    def main(self):
        # get file and extract data
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

        # create torrent object to save torrent
        torrent = TorrentData()    
        
        # check if contains tracker, in announce/announce-list otherwise error
        if "announce" in self.data:
            torrent.announce.add(self.data["announce"])
        if "announce-list" in self.data:
            for announce in self.data["announce-list"]:
                torrent.announce.add(announce[0])
        if not "announce" in self.data and not "announce-list" in self.data:
            print("Error: Neither announce nor announce-list in torrent")
            return

        # optional fields
        if "created by" in self.data:
            torrent.created_by = self.data["created by"]
        if "creation date" in self.data:
            torrent.creation_date = self.data["creation date"]
        if "comment" in self.data:
            torrent.comment = self.data["comment"]
        if "encoding" in self.data:
            torrent.encoding = self.data["encoding"]
        if "nodes" in self.data:
            for ip, port in self.data["nodes"]:
                torrent.nodes.add(tuple((ip, port)))
        
        if "info" in self.data:
            info = self.data.get("info")

            torrent.pieces = info["pieces"]
            torrent.piece_length = info["piece length"]
            del info["pieces"]
            
            # either single or multiple file mode, otherwise error
            if "files" in info:
                torrent.has_multi_file = True
                first = TorrentFile(info["name"])
                torrent.files[first] = []

                for file in info["files"]:
                    f = TorrentFile(file["path"][0])
                    
                    # optional fields
                    if all(enc in file for enc in ["md5", "md5sum"]):
                        f.encoding = "md5"
                        f.checksum = file["md5"] if "md5" in file else file["md5sum"]
                    if "crc32" in file:
                        f.encoding = "crc32"
                        f.checksum = file["crc32"]
                    if "sha1" in file:
                        f.encoding = "sha1"
                        f.checksum = file["sha1"]
                    torrent.files[first].append(f)
            elif "length" in info:
                torrent.has_multi_file = False
                f = TorrentFile(info["name"], info["length"])
                torrent.files = {f:None}
            else:
                raise Exception("Error: Neither single or multiple file mode")

            # optional fields
            if "private" in info:
                torrent.private = True if info["private"] == 0 else False
        else:
            raise Exception("Error: Doesnt contain info in torrent")

        return torrent
