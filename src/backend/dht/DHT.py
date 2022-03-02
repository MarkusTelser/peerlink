import asyncio

from src.backend.metadata.Bencoder import bencode

class DHTServer:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        print('peniss'* 100)
        print('dht recv', data, 'from', addr)


class EchoClientProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport
    
    def datagram_received(self, data, addr):
        print("UGAAAA", data, addr)

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
        await loop.create_datagram_endpoint(protocol_factory, local_addr=('0.0.0.0', self.PORT))
        await asyncio.sleep(3600)
    
    @staticmethod
    async def ping(address):
        loop = asyncio.get_running_loop()
        
        transport, protocol = await loop.create_datagram_endpoint(lambda: EchoClientProtocol(), remote_addr=(address))
        
        msg = {"t":"aa", "y":"q", "q":"ping", "a":{"id":"abcdefghij0123456789"}}
        enc = bencode(msg)
        transport.sendto(enc, address)
        print('success pinged node', address)
        await asyncio.sleep(1000)
    