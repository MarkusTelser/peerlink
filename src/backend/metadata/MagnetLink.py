from urllib.parse import unquote_plus
from src.backend.exceptions import *

class MagnetLink:
    def __init__(self):
        self.name = ""
        self.size = 0
        self.hash = ""
        self.block_size = 2 ** 14 # 16KiB
        self.webseeds = set()
        self.trackers = set()
        self.keywords = list()
        self.select_only = list()

    
    def parse(self, link):
        if link[:8] != "magnet:?":
            raise WrongFormat("doesn't start like a magnet link")
        
        data = unquote_plus(link[8:])
        elements = data.split("&")
        print(elements)

        for element in elements:
            param, result = element.split("=")
            print(param)

            if param == "dn":
                self.name = result
            elif param == "xl":
                self.size = int(result)
            elif param == "xt":
                elems = result.split(":")
                if len(elems) == 3:
                    if elems[0] == "urn":
                        if elems[1] == "btih":
                            self.hash = elems[2]
                        elif elems[1] == "btmh":
                            pass
                    else:
                        raise WrongFormat("not a uniform resource name")
            elif param == "ws":
                self.webseeds.add(element.split("=")[1])
            elif param == "as":
                raise Exception("not implemented")
            elif param == "xs":
                raise Exception("not implemented")
            elif param == "kt":
                keywords = element.split("=")[1]
                for keyword in keywords.split("+"):
                    self.keywords.append(keyword)
                raise Exception("not implemented")
            elif param == "mt":
                raise Exception("not implemented")
            elif param == "tr":
                self.trackers.add(element.split("=")[1])
            # BEP 53
            elif param == "so":
                for id in result.split(","):
                    if "-" in id:
                        start = int(id.split("-")[0])
                        end = int(id.split("-")[1]) + 1 
                        for i in range(start, end):
                            if int(i) not in self.select_only:
                                self.select_only.append(int(i))
                    elif int(id) not in self.select_only:
                        self.select_only.append(int(id))

        if not self.hash:
            raise MissingRequiredField("Hash not in magnet link")


link = "magnet:?xt=urn:btih:6EEFF1201E4649AB020B5104E9642D97935823DF&dn=Free+Solo+%282018%29+%2B+Extras+%281080p+BluRay+x265+HEVC+10bit+EAC3+5+1+Bandi%29&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Fipv4.tracker.harry.lu%3A80%2Fannounce&tr=udp%3A%2F%2Fretracker.lanta-net.ru%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fipv6.tracker.harry.lu%3A80%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.open-internet.nl%3A6969%2Fannounce&tr=udp%3A%2F%2Fopen.demonii.si%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.pirateparty.gr%3A6969%2Fannounce&tr=udp%3A%2F%2Fdenis.stalker.upeer.me%3A6969%2Fannounce&tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce"
m = MagnetLink()
m.parse(link)

print()
print("Name:", m.name)
print("Trackers:", m.trackers)
print("Hashes:", m.hash)
print(m.select_only)