from enum import Enum
import aiohttp
import asyncio
from charset_normalizer import logging
from socket import inet_ntoa, inet_ntop
from socket import AF_INET6
from struct import unpack

from yarl import URL

from ..metadata.Bencoder import bdecode
from ..peer_protocol.PeerIDs import PeerIDs

# exception
from ..exceptions import *
from requests.models import HTTPError
from requests.sessions import TooManyRedirects
from requests import ConnectionError
from requests.exceptions import RequestException, Timeout
from urllib.parse import quote_plus

class HTTPEvents:
    STARTED = "started"
    STOPPED = "stopped"
    COMPLETED = "completed"

class TrackerStatus(Enum):
    NOCONTACT = 0
    CONNECTING = 1
    FINISHED = 2
    ERROR = 3

class HTTPTracker:
    TIMEOUT = 3

    def __init__(self, address, info_hash, peer_id, port, semaphore):
        self.address = address
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.port = port
        
        self.interval = 0
        self.min_interval = 0
        self.min_request_interval = 0 # min scrape interval
        self.leechers = 0
        self.seeders = 0
        self.peers = list()
        self.trackerid = ""
        
        self.semaphore = semaphore
        
        self.status = TrackerStatus.NOCONTACT
        self.error = None

    async def announce(self, event, uploaded, downloaded, left):
        # optional
        ip = 0
        numwant = 50
        no_peer_id = 1
        compact = 1
        key = PeerIDs.generate_key()
        trackerid = ""
        
        async with self.semaphore:
            recv = None
            try:
                self.status = TrackerStatus.CONNECTING
                recv = await self._announce(self.info_hash, self.peer_id, self.port, uploaded, downloaded, left, event)
                self.peers = recv
            except Exception as e:
                #logging.error(e, exc_info=True)
                print('http', e)
                
                self.error = str(e)
                self.status = TrackerStatus.ERROR
            finally:
                if not self.error:
                    self.status = TrackerStatus.FINISHED
                return recv
        
    async def scrape(self):
        async with self.semaphore:
            recv = None
            try:
                recv = await self._scrape(self.info_hash)
                self.peers = recv
            except Exception as e:
                self.error = str(e)
            finally:
                return recv
        
    
    """
    ----Request----
    info_hash
    peer_id
    port
    uploaded
    downloaded
    left
    key (optional): to uniquely identify client with peer_id and key, for statistics (32bits worth of entropy)
    ip (optional)  giving the IP (or dns name) which this peer is at
    event (optional)
    numwant (optional) default 50
    trackerid (optional)
    no_peer_id (optional)
    compact (optional) 1 = true, 0 false
    
    ----Answer----
    interval (should not announce more frequent)
    min interval (optional): (must not announce more frequent)
    failure reason (optional): human readable failure reason
    failure code (optional)
    warning message (optional): similar to failure reason, but response gets processed normally
    complete (optional): number of seeders
    incomplete (optional): number of leechers
    tracker_id (optional): id that must be sent on next announcement
    peers:
        peer id (not if no_peer_id)
        ip
        port
        
        or bencoded benstring (if optional)
    
    peers_ipv6 (optional): when compact ipv6 are requested
    or peers6 (optional): same as peers_ipv6
    """
    async def _announce(self, info_hash, peer_id, port, uploaded, downloaded, left, event=None, ip=None, numwant=None, no_peer_id=None, compact=None, key=None, trackerid=None):
        params = {}

        # required parameters
        params['info_hash'] = quote_plus(info_hash)
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
            async with aiohttp.ClientSession() as session:
                param_url = "&".join([f"{x}={params[x]}" for x in params])
                url = f"{self.address}?{param_url}"
                async with session.get(URL(url, encoded=True), timeout=HTTPTracker.TIMEOUT) as resp:
                    if resp.status != 200:
                        raise Exception('wrong status code ' + str(resp.status) )
                    recv = await resp.read()
        except HTTPError as e:
            raise NetworkExceptions("1" + str(e))
            # unsuccessful status code
        except asyncio.TimeoutError as e:
            raise NetworkExceptions("2 Request timed out")
            # request timed out
        except TooManyRedirects as e:
            raise NetworkExceptions("3" +str(e))
            # exceeds number of max redirect
        except aiohttp.ClientConnectionError as e:
            raise NetworkExceptions("4 Network problem" + self.address)
            # the event of a network problem (e.g. DNS failure, refused connection, etc)
        except RequestException as e:
            raise NetworkExceptions("5" + str(e))
        except Exception as e:
            logging.exception('te')
            print('uncaught', e)
            return
        
        answer = bdecode(recv)
        
        # decode bencoded answer
        if "failure reason" in answer:
            raise NetworkExceptions(answer["failure reason"])
        
        failure_codes = {
            '100' : "Invalid request type: client request was not a HTTP GET",
            '101' : "Missing info_hash",
            '102' :	"Missing peer_id",
            '103' :	"Missing port",
            '150' :	"Invalid infohash: infohash is not 20 bytes long",
            '151' :	"Invalid peerid: peerid is not 20 bytes long",
            '152' :	"Invalid numwant. Client requested more peers than allowed by tracker",
            '200' :	"info_hash not found in the database. Sent only by trackers that do not automatically include new hashes into the database",
            '500' :	"Client sent an eventless request before the specified time",
            '900' :	"Generic error"
        }
        
        if "failure code" in answer:
            failure_code = str(answer["failure code"])
            if failure_code in failure_codes:
                raise NetworkExceptions(failure_codes[failure_code])
            raise NetworkExceptions("Message contains failure code", failure_code)
        if "warning message" in answer:
            print(answer["warning message"])
            # TODO log the warning message
        
        # must contain these two fields
        if not "interval" in answer:
            raise MissingRequiredField("Interval not in tracker response")
        if not "peers" in answer:
            raise MissingRequiredField("Peers not in tracker response")
        
        self.interval = answer["interval"]
        self.min_interval = answer["interval"]
        
        if type(answer.get("peers")) == list:  
            for peer in answer.get("peers"):
                ip = peer["ip"]
                port = peer["port"]
                if no_peer_id is None:
                    peer_id = peer["peer id"]
                    self.peers.append((ip, port, peer_id))
                else:
                    self.peers.append((ip, port))
        # optional compact representation of peers
        elif type(answer.get("peers")) == bytes:
            byte_string = answer.get("peers")
            peer_count = int(len(byte_string) / 6) # 4 bytes ipv4 + 2 bytes port
            for i in range(peer_count):
                ip = inet_ntoa(byte_string[i * 6: i * 6 + 4])
                port = unpack("!H", byte_string[i * 6 + 4: i * 6 + 6])[0]
                self.peers.append((ip, port))
        
        # other optional fields
        if "min interval" in answer:
            self.min_interval = answer["min interval"]
        if "tracker id" in answer:
            self.trackerid = answer["tracker id"]
        if "complete" in answer:
            self.seeders = answer["complete"]
        if "incomplete" in answer:
            self.leechers = answer["incomplete"]

        # list of all ipv6 address currently monitored by tracker
        # peers_ipv6 should be same as peers6, but in earlier extension (may be depreciated)
        if "peers6" in answer or "peers_ipv6" in answer:
            byte_string = answer.get("peers6")
            peer_count = int(len(byte_string) / 18) # 16 bytes ipv6 + 2 bytes port
            for i in range(peer_count):
                ip = inet_ntop(AF_INET6, byte_string[i * 18: i * 18 + 16])
                port = unpack("!H", byte_string[i * 18 + 16: i * 18 + 18])[0]
                self.peers.append((ip, port))
        
        return self.peers


    """
    The original BitTorrent Protocol Specification defines one exchange 
    between a client and a tracker referred to as an announce. In order to 
    build responsive user interfaces, clients desired an additional way
    to query metadata about swarms in bulk. The exchange that fetches this
    metadata for the clients is referred to as a scrape. It should be
    noted that scrape exchanges have no effect on a peer's participation
    in a swarm.
    """
    async def _scrape(self, info_hashes=None): 
        if not "announce" in self.address:
            raise WrongFormat(f"Url contains no announce {self.address}")
        link = self.address.replace("announce","scrape")

        params = {}

        # no info_hash param is send, all stats for all torrents are send (shouldn't be used)
        if info_hashes == None or len(info_hashes) == 0:
            pass
        # scrape one or multiple info_hashes, either str or list
        elif type(info_hashes) == bytes or type(info_hashes) == list:
            params["info_hash"] = quote_plus(info_hashes)
        
        try:
            async with aiohttp.ClientSession() as session:
                param_url = "&".join([f"{x}={params[x]}" for x in params])
                url = f"{link}?{param_url}"
                async with session.get(URL(url, encoded=True), timeout=HTTPTracker.TIMEOUT) as resp:
                    if resp.status != 200:
                        raise Exception('wrong status code ' + str(resp.status) )
                    recv = await resp.read()
        except HTTPError as e:
            raise NetworkExceptions("1" + str(e))
            # unsuccessful status code
        except Timeout as e:
            raise NetworkExceptions("2 Request timed out")
            # request timed out
        except TooManyRedirects as e:
            raise NetworkExceptions("3" +str(e))
            # exceeds number of max redirect
        except ConnectionError as e:
            raise NetworkExceptions("4 Network problem" + self.address)
            # the event of a network problem (e.g. DNS failure, refused connection, etc)
        except RequestException as e:
            raise NetworkExceptions("5" + str(e))
            # any other possible exception

        answer = bdecode(recv)        
        
        if "failure reason" in answer:
            raise MessageExceptions(f"Scrape failed: {answer['failure reason']}")

        if not "files" in answer:
            raise MessageExceptions("Files field in scrape response missing")
        
        files = answer.get("files")
        for file in files:
            print(answer.get("files").get(file))
            if "complete" not in files.get(file):
                raise MissingRequiredField("Complete not in scrape answer")
            if "incomplete" not in files.get(file):
                raise MissingRequiredField("Incomplete not in scrape answer")
            #if "downloaded" not in files.get(file):
            #    raise MissingRequiredField("Downloaded not in scrape answer")
            # optional keys like name
        
        # other optional unofficial keys
        if "flags" in answer:
            flags = answer.get("flags")
            if "min_request_interval" in flags:
                self.min_request_interval = flags["min_request_interval"]
                print(self.min_request_interval)
            print(flags)
        
        return answer.get("files")