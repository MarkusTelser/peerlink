from abc import abstractmethod
from enum import Enum
from src.backend.trackers.HTTPTracker import HTTPTracker
from src.backend.trackers.UDPTracker import UDPTracker

# exception catching
from ..exceptions import *

class TrackerType(Enum):
    HTTP = 0
    UDP = 1
    UNSUPPORTED = 2

class Tracker(object):
    def __init__(self) -> None:
        self.address = ''
        self.leechers = 0
        self.seeders = 0
        self.peers = list()
        self.status = None
        self.error = None
    
    @abstractmethod
    def announce(self):
        pass
    
    @abstractmethod
    def scrape(self):
        pass

"""
parse URL according to URI (Uniform Resource Identifiers) schemes
https://datatracker.ietf.org/doc/html/rfc3986
"""
def parse_url(announce_url: str):
    typ = announce_url.split("://")[0]
    
    tracker_type = None
    tracker_address = None
    print(announce_url)
    if typ in ["http", "https"]:
        tracker_type = TrackerType.HTTP
        tracker_address = (announce_url)
    elif typ == "udp":
        tracker_type = TrackerType.UDP
        ip = announce_url.split("/")[2].split(":")[0]
        port = int(announce_url.split("/")[2].split(":")[1])
        if len(announce_url.split("/")) > 3:
            extension = "/" + "/".join(announce_url.split("/")[3:])
        else:
            extension = "" 
        tracker_address = (ip, port, extension)
    else:
        tracker_type = TrackerType.UNSUPPORTED
        
    return (tracker_type, tracker_address)


def give_object(announce, info_hash, peer_id, port, semaphore):
    try:
        typ, address = parse_url(announce)
    except Exception as e:
        print('error parsing url')
        return None

    tracker = None
    
    if typ == TrackerType.HTTP:
        tracker = HTTPTracker(address, info_hash, peer_id, port, semaphore)
    elif typ == TrackerType.UDP:
        host, port, extension = address
        addr = host, port
        tracker = UDPTracker(addr, extension, info_hash, peer_id, port, semaphore)
    elif typ == TrackerType.UNSUPPORTED:
        # TODO tracker type not recognized
        pass
    
    return tracker 