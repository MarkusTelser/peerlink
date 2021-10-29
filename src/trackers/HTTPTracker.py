import json
from random import
from string import ascii_letters, choice

from requests import get
from bencode import decode

class HTTPEvents:
    STARTED = "started"
    STOPPED = "stopped"
    COMPLETED = "completed"

class HTTPTracker:
    def __init__(self, adr_url):
        self.adr_url = adr_url

    def main(self, info_hash, peer_id):
        event = HTTPEvents.STARTED
        peer_id = "-qB3090-" + ''.join(choice(ascii_letters) for _ in range(12)), 'utf-8'

        # demo values
        ip = 0
        port = 0
        uploaded = "0"
        downloaded = "0"
        left = "1000"

        # optional
        numwant = 50
        no_peer_id = 1
        compact = 0
        key = ""
        trackerid = ""

        recv = self.request(info_hash, peer_id, port, uploaded, downloaded, left)

        if recv == None:
            raise Exception("Error: HTTP-Tracker results are null")
        if len(recv["peers"]) == 0:
            raise Exception("Error: HTTP-Tracker results contain no peers")
        return recv
        
    
    """
    failure_code key that tracker might send back:

    100	Invalid request type: client request was not a HTTP GET.
    101	Missing info_hash.
    102	Missing peer_id.
    103	Missing port.
    150	Invalid infohash: infohash is not 20 bytes long.
    151	Invalid peerid: peerid is not 20 bytes long.
    152	Invalid numwant. Client requested more peers than allowed by tracker.
    200	info_hash not found in the database. Sent only by trackers that do not automatically include new hashes into the database.
    500	Client sent an eventless request before the specified time.
    900	Generic error.
    """
    def request(self, info_hash, peer_id, port, uploaded, downloaded, left, ip=None, event=None, numwant=None, no_peer_id=None, compact=None):
        params = ""

        # required parameters
        params += f"info_hash={info_hash}"
        params += f"&peer_id={peer_id}"
        params += f"&port={port}"
        params += f"&uploaded={uploaded}"
        params += f"&downloaded={downloaded}"
        params += f"&left={left}"

        # optional parameters
        if ip is not None:
            params += f"&ip={ip}"
        if event is not None:
            params += f"&event={event}"
        if numwant is not None:
            params += f"&numwant={numwant}"
        if no_peer_id is not None:
            params += "&no_peer_id={no_peer_id}"
        if compact is not None:
            params += "&compact={compact}"

        url = f"{self.adr_url}?{params}"
        
        request_parameters = {
            'info_hash' : info_hash,
            'peer_id'   : peer_id,
            'port'      : port,
            'uploaded'  : uploaded,
            'downloaded': downloaded,
            'left'      : left
        }
        
        try:
            recv = get(url, request_parameters, timeout=10)
        except Exception as e:
            return e
        
        try:
            answer = decode(recv.text)
        except Exception as e:
            return e

        recv.close()
        return answer
    
    def gen_pid(self):
        return 
