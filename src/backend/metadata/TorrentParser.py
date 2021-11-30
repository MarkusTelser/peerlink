from os.path import exists
from datetime import datetime
from .Bencoder import decode, encode
from .TorrentData import TorrentData, TorrentFile
from src.backend.exceptions import *

class TorrentParser:
    @staticmethod
    def parse_file(file):
        if file == None:
            raise Exception("Error: File equals None")
        encry = file.read()
        data = decode(encry)
        return TorrentParser.parse(data)
    
    @staticmethod
    def parse_filepath(filepath: str):
        if exists(filepath):
            with open(filepath, "rb") as f:
                encry = f.read()
            data = decode(encry)
            return TorrentParser.parse(data)
        else:
            print("Error: File doesnt exist")

    @staticmethod
    def parse(data):
        if data == None:
            raise Exception("Error: no file data")

        # create torrent object to save torrent
        torrent = TorrentData()    
        
        # check if contains tracker, in announce/announce-list otherwise error
        if "announce" in data:
            torrent.announces.append(data["announce"])
        else:
            raise MissingRequiredField("announce key not in torrent")
        if "announce-list" in data:
            for announce in data["announce-list"]:
                if not announce[0] in torrent.announces:
                    torrent.announces.append(announce[0])

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
        if "httpseeds" in data:
            for address in data["httpseeds"]:
                torrent.httpseeds.add(address)
        
        if "info" in data:
            info = data.get("info")
            torrent.info_hash = TorrentData.gen_info_hash(info)
            torrent.info_hash_hex = TorrentData.gen_info_hash_hex(info)

            if "pieces" not in info:
                raise MissingRequiredField("Pieces not in torrent")
            if "piece length" not in info:
                raise MissingRequiredField("Piece length not in torrent")
            
            torrent.pieces = info["pieces"]
            torrent.pieces_count = int(len(info["pieces"]) / 20)
            torrent.piece_length = int(info["piece length"])
            #del info["pieces"]

            # TODO BEP-0030 merkle trees
            
            # either single or multiple file mode, otherwise error
            if "files" in info:
                if "name" not in info:
                    raise MissingRequiredField("Name not in torrent")
                
                torrent.has_multi_file = True
                first = TorrentFile(info["name"])
                torrent.files[first] = []

                for file in info["files"]:
                    if "path" not in file:
                        raise MissingRequiredField("Path not in torrent")
                    if "length" not in file:
                        raise MissingRequiredField("Length not in torrent")

                    file_path = '/'.join(file["path"])
                    f = TorrentFile(file_path, file["length"])
                    
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
                if "name" not in info:
                    raise MissingRequiredField("Name not in torrent")
                if "length" not in info:
                    raise MissingRequiredField("Length not in torrent")
                torrent.has_multi_file = False
                f = TorrentFile(info["name"], info["length"])
                torrent.files = {f:None}
            else:
                raise MissingRequiredField("Neither single or multiple file mode")

            # optional fields
            if "private" in info:
                torrent.private = bool(info["private"] == 1)
        else:
            raise MissingRequiredField("info key not in torrent")
    
        return torrent