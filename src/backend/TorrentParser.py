from os.path import exists
from bencode import decode
from datetime import datetime
from bencode import bdecode, decode
from .Torrent import TorrentData, TorrentFile

class TorrentParser:
    @staticmethod
    def parse_file(file):
        if file == None:
            raise Exception("Error: File equals None")
        encry = file.read()
        data = decode(encry)
        bdata = bdecode(encry)
        return TorrentParser.parse(data, bdata)
    
    @staticmethod
    def parse_filepath(filepath):
        if exists(filepath):
            with open(filepath, "rb") as f:
                encry = f.read()
            data = decode(encry)
            bdata = bdecode(encry)
            return TorrentParser.parse(data, bdata)
        else:
            print("Error: File doesnt exist")
    
    @staticmethod
    def parse_magnet_link(link):
        pass

    @staticmethod
    def parse(data, bdata):
        if data == None or bdata == None:
            raise Exception("Error: File data given equals None")

        # create torrent object to save torrent
        torrent = TorrentData()    
        
        # check if contains tracker, in announce/announce-list otherwise error
        if "announce" in data:
            torrent.announces.append(data["announce"])
        if "announce-list" in data:
            for announce in data["announce-list"]:
                if not announce[0] in torrent.announces:
                    torrent.announces.append(announce[0])
        if not "announce" in data and not "announce-list" in data:
            print("Error: Neither announce nor announce-list in torrent")
            return

        # optional fields
        if "created by" in data:
            torrent.created_by = data["created by"]
        if "creation date" in data:
            date = datetime.utcfromtimestamp(data["creation date"])
            torrent.creation_date = date.strftime('%Y-%m-%d %H:%M:%S')
        if "comment" in data:
            torrent.comment = data["comment"]
        if "encoding" in data:
            torrent.encoding = data["encoding"]
        if "nodes" in data:
            for ip, port in data["nodes"]:
                torrent.nodes.add(tuple((ip, port)))
        
        if "info" in data:
            info = data.get("info")
            torrent.info = bdata['info']

            torrent.pieces = info["pieces"]
            torrent.pieces_count = int(len(info["pieces"]) / 20)
            torrent.piece_length = info["piece length"]
            del info["pieces"]
            
            # either single or multiple file mode, otherwise error
            if "files" in info:
                torrent.has_multi_file = True
                first = TorrentFile(info["name"])
                torrent.files[first] = []

                for file in info["files"]:
                    f = TorrentFile(file["path"][0], file["length"])
                    
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
