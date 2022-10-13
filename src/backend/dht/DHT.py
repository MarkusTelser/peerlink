import asyncio
from dataclasses import dataclass
from src.backend.metadata.Bencoder import bencode, bdecode
from src.backend.peer_protocol.PeerIDs import PeerIDs

@dataclass
class DHTMessage:
    tid: str = ""
    typ: str = ""
    version: str = ""

def parse(msg: bytes):
    dec = bdecode(msg)
    ret = DHTMessage()
    print(dec)
    if "t" not in dec:
        print("NO transaction Id")
    if "y" not in dec:
        print("no msg type")

    # save t and y
    ret.tid = dec["t"]
    ret.typ = {"q": "query", "r": "response", "e": "error"}[dec["y"]]

    if "v" in dec:
        ret.version = PeerIds.get_client(dec["v"])
    
    return ret


class DHTServer:
    def connection_made(self, transport):
        self.transport = transport
        print('dht running on ', transport.get_extra_info('sockname'))

    def datagram_received(self, data, addr):
        print('-------'* 100)
        print('dht recv' * 100, data, 'from', addr)


class EchoClientProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport
    
    def datagram_received(self, data, addr):
        print("UGAAAA", data, addr)
        print(parse(data))

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print("Connection closed")

class DHT:
    PORT = 6900
    
    def __init__(self) -> None:
        pass
    
    async def start(self):
        loop = asyncio.get_running_loop()
        protocol_factory = lambda: DHTServer()
        transport, protocol  = await loop.create_datagram_endpoint(protocol_factory, local_addr=('0.0.0.0', self.PORT))
        print(transport, protocol)

    
    @staticmethod
    async def ping(address, port):
        loop = asyncio.get_running_loop()
        
        transport, protocol = await loop.create_datagram_endpoint(lambda: EchoClientProtocol(), remote_addr=(address, port))
        
        msg = {"t":"aa", "y":"q", "q":"get_peers", "a": {"id":"abcdefghij0123456789", "info_hash": "C9ABE33E3679593CD89927910D528252CDC44E6E"}}
        enc = bencode(msg)
        transport.sendto(enc)
        print('success pinged node', address)
        await asyncio.sleep(1000)
    
    async def find_node():
        pass

    async def get_peers():
        pass
    
    async def announce_peer():
        pass
    
