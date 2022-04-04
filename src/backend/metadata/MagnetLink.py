from dataclasses import dataclass
from urllib.parse import unquote_plus
from ..exceptions import *
from .Bencoder import bencode, bdecode

@dataclass
class MagnetLink:
    name: str = ""
    size: int = 0
    info_hash: bytes = b''
    info_hash_hex: str = ""
    tagged_info_hash: str = ""
    trackers = set()
    webseeds = set()
    keywords = set()
    select_only = set()
    sources = set()
    fallback = set()
    manifest_topics = set()
    peers = set()


class MagnetParser:
    @staticmethod
    def parse(link: str):
        if link[:8] != "magnet:?":
            raise WrongFormat("doesn't start like a magnet link")
        
        data = unquote_plus(link[8:])
        elements = data.split("&")
        ret = MagnetLink()

        for element in elements:
            key, value = element.split("=")

            # filename to display to the user, for convenience
            if key == "dn":
                ret.name = value
            # size in bytes (exact length)
            elif key == "xl":
                ret.size = int(value)
            # URN containing info hash of file
            elif key == "xt":
                elems = value.split(":")
                if len(elems) != 3 or elems[0] != "urn":
                    raise WrongFormat("not a uniform resource name")
                
                if elems[1] == "btih":
                    # TODO check if 40 byte or 32 byte base 32 encoded
                    ret.info_hash = bytes.fromhex(elems[2])
                    ret.info_hash_hex = elems[2]
                elif elems[1] == "btmh":
                    # TODO multihash formatted hex encoded infohash format
                    pass
            # is a web seed, same as url_list (for BEP 19)
            elif key == "ws":
                ret.webseeds.add(value)
            # download source for the file pointed to by the magnet link
            elif key == "xs":
                ret.sources.add(value)
            # same as/alternative to xs (direct download from a web server)
            elif key == "as":
                ret.fallback.add(value)
            # string of search keywords (for BEP 18)
            elif key == "kt":
                keywords = element.split("=")[1]
                for keyword in keywords.split("+"):
                    ret.keywords.add(keyword)
            # link to metafile that contains a list of links (??)
            elif key == "mt":
                ret.manifest_topics.add(value)
            # url encoded tracker url (no DHT needed)
            elif key == "tr":
                ret.trackers.add(value)
            # peer address expressed as hostname:port, ipv4-literal:port or [ipv6-literal]:port
            elif key == "x.pe":
                ip, port = value.rsplit(':', 1)
                ret.trackers.add((ip, port))
            # select specific file indices for download (BEP 53)
            elif key == "so":
                for id in value.split(","):
                    if "-" in id:
                        start = int(id.split("-")[0])
                        end = int(id.split("-")[1]) + 1 
                        for i in range(start, end):
                            ret.select_only.add(int(i))
                    else:
                        ret.select_only.add(int(id))

        if not ret.info_hash:
            raise MissingRequiredField("Hash not in magnet link")
        
        return ret
    
    @staticmethod
    def encode(magnet_link: MagnetLink, info_data: dict):
        dec = dict()
        
        if len(magnet_link.trackers) > 0:
            dec["announce"] = list(magnet_link.trackers)[0]
        if len(magnet_link.trackers) > 1:
            dec["announce-list"] = [list(magnet_link.trackers)]
        
        dec["info"] = info_data
        
        return bencode(dec)

if __name__ == "__main__":
    link = "magnet:?xt=urn:btih:6EEFF1201E4649AB020B5104E9642D97935823DF&dn=Free+Solo+%282018%29+%2B+Extras+%281080p+BluRay+x265+HEVC+10bit+EAC3+5+1+Bandi%29&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Fipv4.tracker.harry.lu%3A80%2Fannounce&tr=udp%3A%2F%2Fretracker.lanta-net.ru%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fipv6.tracker.harry.lu%3A80%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.open-internet.nl%3A6969%2Fannounce&tr=udp%3A%2F%2Fopen.demonii.si%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.pirateparty.gr%3A6969%2Fannounce&tr=udp%3A%2F%2Fdenis.stalker.upeer.me%3A6969%2Fannounce&tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce"
    data = MagnetParser.parse(link)
    print(data)