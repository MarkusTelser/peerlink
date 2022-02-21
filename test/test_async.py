
from logging import exception
from src.backend.Session import Session
from src.backend.metadata import TorrentParser
from src.backend.swarm import Swarm
"""
s = Session()

fp = 'data/all/test.torrent'
data = TorrentParser.parse_filepath(fp)
save_path = '~/Desktop'
t = Swarm(data, save_path)

s.add(t)
s.resume(0)
"""

import asyncio

async def run():
    fp = 'data/all/test.torrent'
    data = TorrentParser.parse_filepath(fp)
    save_path = '~/Desktop'
    t = Swarm(data, save_path)
    
    s = Session()
    s.add(t)
    s.resume(0)
    
    await asyncio.sleep(10000)



async def func():
    print('started')
    await asyncio.sleep(5)
    print('finished')
    return 5

def called(result):
    print('called', result.result())


"""
----------------------------------------------------------------------------------------
"""
from struct import pack
from src.backend.trackers.UDPTracker import UDPTracker, Actions

class BackendProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        self.sock = None

    def connection_made(self, sock):
        self.sock = sock
        print('connection made', sock)

    def datagram_received(self, data, addr):
        print("Received:", data, addr)
        print("Close the socket")
        self.sock.close()

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print("Connection closed")
    

class UdpTracker:
    CONNECTION_TIMEOUT = 10
    
    def __init__(self, address) -> None:
        self.address = address
    
    async def announce(self):
        loop = asyncio.get_running_loop()
        loop.sock_recv(sock, )
        try:
            co = loop.create_datagram_endpoint(lambda: BackendProtocol(), remote_addr=self.address)
            transport, protocol = await asyncio.wait_for(co, timeout=self.CONNECTION_TIMEOUT)
            print(type(transport), type(protocol), dir(transport))
            
            # generate connect msg
            TID = UDPTracker.gen_tid()
            msg = pack('!QII', UDPTracker.IDENTIFICATION, Actions.CONNECT.value, TID)
            transport.sendto(msg)
            
            
        except asyncio.exceptions.TimeoutError:
            print('connection timed out')


async def test():
    adr = ('tracker.internetwarriors.net', 1337)
    tracker = UdpTracker(adr)
    await tracker.announce()
    await asyncio.sleep(1000)

asyncio.run(run(), debug=True)