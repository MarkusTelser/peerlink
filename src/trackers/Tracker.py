from enum import Enum

from trackers.HTTPTracker import HTTPTracker

class TrackerType(Enum):
    UDP = 0
    HTTP = 1
    HTTPS = 2

class Tracker:
    def __init__(self, link):
        self.type = None
        self.address = ()
        self.error = ""

    def main(self):
        self.parse_link()
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
            port = link.split("/")[2].split(":")[1]
            self.type = TrackerType.UDP
            self.address = (ip, port)
        else:
            self.error = f"Error: Unknown tracker type {ann}"
        
    def connect_tracker(self):
        if self.error != "":
            return
        elif self.type == TrackerType.UDP:
            tracker = HTTPTracker()
        elif self.type == TrackerType.HTTP or self.type == TrackerType.HTTPS:
            tracker = HTTPTracker()
        
        # call sub class to get peers, handle exceptions
        try:
            peers = tracker.main()
        except Exception as e:
            self.error = str(e)
        