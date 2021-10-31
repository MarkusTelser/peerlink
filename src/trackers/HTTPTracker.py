import requests
from random import choice
from string import ascii_letters
from bencode import decode

# exception
from exceptions import *
from requests import ConnectionError
from bencode import BencodeDecodeError

class HTTPEvents:
    STARTED = "started"
    STOPPED = "stopped"
    COMPLETED = "completed"

class HTTPTracker:
    TIMEOUT = 5

    def __init__(self, url, info_hash):
        self.url = url
        self.info_hash = info_hash

    def main(self):
        event = HTTPEvents.STARTED
        peer_id = "-qB3090-" + ''.join(choice(ascii_letters) for _ in range(12))

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

        recv = self.request(self.info_hash, peer_id, port, uploaded, downloaded, left, compact=1)
        
        if recv == None or len(recv["peers"]) == 0:
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
    def request(self, info_hash, peer_id, port, uploaded, downloaded, left, ip=None, event=None, numwant=None, no_peer_id=None, compact=None, key=None, trackerid=None):
        params = {}

        # required parameters
        params['info_hash'] = info_hash
        params['peer_id'] = peer_id
        params['port'] = port
        params['uploaded'] = uploaded
        params['downloaded'] = downloaded
        params['left'] = left

        # optional parameters
        if ip is not None:
            params['ip'] = ip
        if event is not None:
            params['event'] = event
        if numwant is not None:
            params['numwant'] = numwant
        if no_peer_id is not None:
            params['no_peer_id'] = no_peer_id
        if compact is not None:
            params['compact'] = compact
        if key is not None:
            params['key'] = key
        if trackerid is not None:
            params['trackerid'] = trackerid 

        try:
            recv = requests.get(self.url, params, timeout=HTTPTracker.TIMEOUT)
        except ConnectionError as e:
            raise NetworkExceptions(str(e) + self.url)

        try:
            answer = decode(recv.text)
        except BencodeDecodeError as e:
            raise MessageExceptions(str(e))
        
        # decode bencoded answer
        if "failure reason" in answer:
            pass
        elif "warning message" in answer:
            pass
        
        # must contain these two fields
        if not "interval" in answer:
            pass
        if not "peers" in answer:
            pass
        
        print(answer(["interval"]))
        print(answer["peers"])
        
        # other optional fields
        if "min interval" in answer:
            pass
        if "tracker id" in answer:
            pass
        if "complete" in answer:
            pass
        if "incomplete" in answer:
            pass

        recv.close()
        return answer


    """
    The original BitTorrent Protocol Specification defines one exchange 
    between a client and a tracker referred to as an announce. In order to 
    build responsive user interfaces, clients desired an additional way
    to query metadata about swarms in bulk. The exchange that fetches this
    metadata for the clients is referred to as a scrape. It should be
    noted that scrape exchanges have no effect on a peer's participation
    in a swarm.
    """
    def scrape(self, info_hashes): 
        if not "announce" in self.url:
            raise NotSupportedOperation(f"Url contains no announce {self.url}")
        link = self.url.replace("announce","scrape")

        params = "?"

        # scrape one or multiple info_hashes
        if type(info_hashes) == list:
            for info_hash in info_hashes:
                params += f"info_hash={info_hash}&"
        elif type(info_hashes) == str:
            params += f"info_hash={info_hashes}"
        
        request_link = link + params
        try:
            recv = requests.get(request_link, timeout=HTTPTracker.TIMEOUT)
        except ConnectionError as e:
            raise NetworkExceptions(str(e))

        try:
            answer = decode(recv.text)
        except BencodeDecodeError as e:
            raise MessageExceptions(str(e))

        if "failure reason" in answer:
            raise MessageExceptions(f"Scrape failed: {answer['failure reason']}")

        if not "files" in answer:
            raise MessageExceptions("Files field in scrape response missing")
        
        return answer.get("files")