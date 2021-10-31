from enum import Enum
from threading import Thread
from trackers.HTTPTracker import HTTPTracker
from trackers.UDPTracker import UDPTracker

# exception catching
from exceptions import *

class TrackerType(Enum):
    UDP = 0
    HTTP = 1
    HTTPS = 2

class Tracker(Thread):
    def __init__(self, link, data):
        Thread.__init__(self)
        self.link = link
        self.data  =data

        self.type = None
        self.peers = list()
        self.address = ()

        self.error = ""
        self.successful = False

    def run(self):
        self.parse_link(self.link)
        self.connect_tracker()
    
    def parse_link(self, link):
        ann = link.split("://")[0]
        if ann == "http":
            self.type = TrackerType.HTTP
            self.address = (link)
        elif ann == "https":
            self.type = TrackerType.HTTPS
            self.address = (link)
        elif ann == "udp":
            ip = link.split("/")[2].split(":")[0]
            port = int(link.split("/")[2].split(":")[1])
            self.type = TrackerType.UDP
            self.address = (ip, port)
        else:
            self.error = UnknownTrackerType(f"Unknown Tracker Type {ann}")
        
    def connect_tracker(self):
        if self.error != "":
            return
        elif self.type == TrackerType.HTTP or self.type == TrackerType.HTTPS:
            tracker = HTTPTracker(self.address, self.data.info_hash_quoted)
        elif self.type == TrackerType.UDP:
            ip, port = self.address
            tracker = UDPTracker(ip, port, self.data.info_hash)
        
        # call sub class to get peers, handle exceptions
        try:
            peers = tracker.main()
            self.peers = peers
        except TorrentExceptions as e:
            self.error = e
        except Exception as e:
            # TODO log unexpected exception
            print("----", type(e).__name__, str(e))
        else:
            self.successful = True
