
from abc import abstractmethod
from logging import exception
from src.backend.Session import Session
from src.backend.metadata import TorrentParser
from src.backend.swarm import Swarm
from abc import abstractmethod, ABC

import asyncio

async def run():
    #fp = 'data/all/test.torrent'
    #fp = 'data/all/ubuntu.torrent'
    #fp = 'data/archive/cIOS-firmware-images_archive.torrent'
    fp = 'data/ubuntu-18.04.6-desktop-amd64.iso.torrent'
    data = TorrentParser.parse_filepath(fp)
    save_path = '~/Desktop'
    print(data.announces)
    t = Swarm(data, save_path)
    
    s = Session()
    s.add(t)
    s.resume(0)
    
    await asyncio.sleep(10000)

asyncio.run(run(), debug=True)