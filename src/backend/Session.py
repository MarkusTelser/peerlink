import asyncio
import threading
from typing import List

from src.backend.swarm import Swarm


class Session(threading.Thread):
    def __init__(self):
        super(Session, self).__init__()
        self.queue = asyncio.Queue(maxsize=10)
        self.start()
        
        self.swarm_list = list()
    
    def run(self):
        asyncio.run(self._run(), debug=True)
    
    async def _run(self):
        while True:
            func, args, kargs = await self.queue.get()
            asyncio.create_task(func(*args, **kargs))
    
    def resume(self, *args, **kargs):
        self.queue.put_nowait((self._resume, args, kargs))
    
    def stop(self, *args, **kargs):
        self.queue.put_nowait((self._stop, args, kargs))
    
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
            self.swarm_list[index].start()
            
    async def _resume_all(self):
        for torrent in self.swarm_list:
            torrent.start()
    
    async def _stop_all(self):
        for torrent in self.swarm_list:
            torrent.stop()
    
    async def _add(self, swarm: Swarm):
        self.swarm_list.append(swarm)
        
    async def _add_all(self, swarms: List[Swarm]):
        for swarm in swarms:
            self.swarm_list.append(swarm)