from urllib.parse import unquote_plus

class MagnetLink:
    def __init__(self):
        self.name = ""
        self.size = 0
        self.hashes = set()
        self.webseeds = set()
        self.trackers = set()


    def parse(self, link):
        if link[:8] != "magnet:?":
            raise Exception("Error: link doesn't start right")
        
        data = unquote_plus(link[8:])
        elements = data.split("&")

        for element in elements:
            param = element.split("=")[0]
            if param == "dn":
                self.name = element.split("=")[1]
            elif param == "xl":
                self.size = int(element.split("=")[1])
            elif param == "xt":
                elems = element.split("=")[1].split(":")
                if len(elems) == 3:
                    if elems[0] == "urn":
                        if elems[1] == "btih":
                            self.hashes.add(elems[2])
                        else:
                            raise Exception("Error: unknown xt")
            elif param == "ws":
                self.webseeds.add(element.split("=")[1])
            elif param == "as":
                raise Exception("not implemented")
            elif param == "xs":
                raise Exception("not implemented")
            elif param == "kt":
                raise Exception("not implemented")
            elif param == "mt":
                raise Exception("not implemented")
            elif param == "tr":
                self.trackers.add(element.split("=")[1])

    
        print(elements)

link = "magnet:?xt=urn:btih:C26E7479CEA81FEF46693539E0525C90C490C67E&dn=Copshop+%282021%29+%5B720p%5D+%5BWEBRip%5D+%5BYTS+MX%5D&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.internetwarriors.net%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Fretracker.lanta-net.ru%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&tr=udp%3A%2F%2Fipv4.tracker.harry.lu%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&tr=udp%3A%2F%2Fipv6.tracker.harry.lu%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.open-internet.nl%3A6969%2Fannounce&tr=udp%3A%2F%2Fopen.demonii.si%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.pirateparty.gr%3A6969%2Fannounce&tr=udp%3A%2F%2Fdenis.stalker.upeer.me%3A6969%2Fannounce&tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce"
m = MagnetLink()
m.parse(link)

print()
print("Name:", m.name)
print("Trackers:", m.trackers)
print("Hashes:", m.hashes)