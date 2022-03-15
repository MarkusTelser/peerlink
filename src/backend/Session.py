import asyncio
import threading
from typing import List
from src.backend.dht.DHT import DHT

from src.backend.swarm import Swarm
from src.backend.peer_protocol.TCPServer import TCPServer


class Session(threading.Thread):
    def __init__(self):
        super(Session, self).__init__()
        self.queue = asyncio.Queue(maxsize=10)
        self.loop = asyncio.new_event_loop()
        self.loop.set_debug(True)
        
        self.swarm_list = list()
        self.server = TCPServer()
        self.dht = DHT()

        
        self.start()
    
    def run(self):
        print('started')
        
        print('created event loop')
        asyncio.set_event_loop(self.loop)
        

        self.loop.run_until_complete(self._run())
        #self.loop.call_soon(self._run())
        #self.loop.run_forever()
        #asyncio.run(self._run(), debug=True)
    
    async def _run(self):
        #print(asyncio.get_running_loop())
        #self.loop = asyncio.get_running_loop()
        
        # start DHT up
        await self.server.start()
        asyncio.create_task(self.dht.start())
        
        while True:
            func, args, kargs = await self.queue.get()
            print(func, args, kargs)
            asyncio.create_task(func(*args, **kargs))
    
    def resume(self, *args, **kargs):
        f = self.queue.put((self._resume, args, kargs))
        asyncio.run_coroutine_threadsafe(f, self.loop)
    
    def stop(self, *args, **kargs):
        f = self.queue.put((self._stop, args, kargs))
        asyncio.run_coroutine_threadsafe(f, self.loop)
    
    def download_meta(self, *args, **kargs):
        f = self.queue.put((self._download_meta, args, kargs))
        asyncio.run_coroutine_threadsafe(f, self.loop)
    
    def resume_all(self, *args, **kargs):
        self.queue.put_nowait((self._resume_all, args, kargs))
    
    def stop_all(self, *args, **kargs):
        self.queue.put_nowait((self._stop_all, args, kargs))
    
    def add(self, *args, **kargs):
        self.queue.put_nowait((self._add, args, kargs))
        print(self.queue.qsize())
    
    def add_all(self, *args, **kargs):
        self.queue.put_nowait((self._add_all, args, kargs))
    
    async def _resume(self, index: int):
        if len(self.swarm_list) > index:
            self.swarm_list[index].start()
    
    async def _stop(self, index: int):
        if len(self.swarm_list) > index:
            print('paused', index)
            await self.swarm_list[index].pause()
    
    async def _download_meta(self, index: int, magnet):
        if len(self.swarm_list) > index:
            await self.swarm_list[index].download_metadata(magnet)
            
    async def _resume_all(self):
        for torrent in self.swarm_list:
            torrent.start()
    
    async def _stop_all(self):
        for torrent in self.swarm_list:
            torrent.stop()
    
    async def _add(self, swarm: Swarm):
        swarm.LISTEN_PORT = self.server.port
        self.swarm_list.append(swarm)
        
    async def _add_all(self, swarms: List[Swarm]):
        for swarm in swarms:
            self.swarm_list.append(swarm)

    @property
    def upload_speed(self):
        pass

    @property
    def download_speed(self):
        return sum([s.speed_measurer.raw_down_speed for s in self.swarm_list]) / (len(self.swarm_list) or 1)

    @property
    def peers(self):
        return sum(s.peers for s in self.swarm_list)

    @property
    def nodes(self):
        pass