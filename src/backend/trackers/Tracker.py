from enum import Enum
from .HTTPTracker import HTTPTracker
from .UDPTracker import UDPTracker

# exception catching
from ..exceptions import *

class TrackerType(Enum):
    HTTP = 0
    UDP = 1
    UNSUPPORTED = 2

def parse_url(announce_url: str):
    typ = announce_url.split("://")[0]
    
    tracker_type = None
    tracker_address = None
    
    if typ in ["http", "https"]:
        tracker_type = TrackerType.HTTP
        tracker_address = (announce_url)
    elif typ == "udp":
        tracker_type = TrackerType.UDP
        ip = announce_url.split("/")[2].split(":")[0]
        port = int(announce_url.split("/")[2].split(":")[1])
        tracker_address = (ip, port)
    else:
        tracker_type = TrackerType.UNSUPPORTED
        
    return (tracker_type, tracker_address)


def give_object(announce_url: str, info_hash: bytes, start_queue, result_queue):
    typ, address = parse_url(announce_url)
    
    tracker = None
    
    if typ == TrackerType.HTTP:
        tracker = HTTPTracker(address, info_hash, start_queue, result_queue)
    elif typ == TrackerType.UDP:
        host, port = address
        tracker = UDPTracker(host, port, info_hash, start_queue, result_queue)
    elif typ == TrackerType.UNSUPPORTED:
        # TODO tracker type not recognized
        pass
    
    return tracker 