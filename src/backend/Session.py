import asyncio
import uvloop
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

    def resume(self, *args, **kargs):
        f = self.queue.put((self._resume, args, kargs))
        asyncio.run_coroutine_threadsafe(f, self.loop)
    
    def pause(self, *args, **kargs):
        f = self.queue.put((self._pause, args, kargs))
        asyncio.run_coroutine_threadsafe(f, self.loop)

    def stop(self, *args, **kargs):
        f = self.queue.put((self._stop, args, kargs))
        asyncio.run_coroutine_threadsafe(f, self.loop)
    
    def download_meta(self, *args, **kargs):
        f = self.queue.put((self._download_meta, args, kargs))
        asyncio.run_coroutine_threadsafe(f, self.loop)
    
    def resume_all(self, *args, **kargs):
        f = self.queue.put((self._resume_all, args, kargs))
        asyncio.run_coroutine_threadsafe(f, self.loop)
    
    def pause_all(self, *args, **kargs):
        f = self.queue.put((self._pause_all, args, kargs))
        asyncio.run_coroutine_threadsafe(f, self.loop)

    def stop_all(self, *args, **kargs):
        f = self.queue.put((self._stop_all, args, kargs))
        asyncio.run_coroutine_threadsafe(f, self.loop)
    
    def add(self, swarm):
        swarm.LISTEN_PORT = self.server.port
        self.swarm_list.append(swarm)
        return len(self.swarm_list) - 1 
    
    def remove(self, index):
        if len(self.swarm_list) > index:
            del self.swarm_list[index]

    def run(self):
        print('created event loop')
        uvloop.install()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._run())
    
    async def _run(self):
        # start DHT up
        await self.server.start()
        asyncio.create_task(self.dht.start())
        
        while True:
            func, args, kargs = await self.queue.get()
            print(func, args, kargs)
            asyncio.create_task(func(*args, **kargs))

    async def _resume(self, index: int):
        if len(self.swarm_list) > index:
            self.swarm_list[index].start()
    
    async def _pause(self, index: int):
        print('PAUSE' * 100)
        if len(self.swarm_list) > index:
            await self.swarm_list[index].pause()

    async def _stop(self, index: int):
        print('STOP' * 100)
        if len(self.swarm_list) > index:
            self.swarm_list[index].stop()
    
    async def _download_meta(self, index: int, magnet):
        if len(self.swarm_list) > index:
            await self.swarm_list[index].download_metadata(magnet)
            
    async def _resume_all(self):
        for swarm in self.swarm_list:
            swarm.start()
    
    async def _pause_all(self):
        tasks = [swarm.pause() for swarm in self.swarm_list]
        await asyncio.gather(*[task for task in tasks])

    async def _stop_all(self):
        tasks = [swarm.stop() for swarm in self.swarm_list]
        await asyncio.gather(*[task for task in tasks])