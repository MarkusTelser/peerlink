from src.backend.metadata import TorrentParser
from src.backend.swarm import Swarm

from multiprocessing import Process, Pool
from threading import Thread
from time import time

fp = "/home/carlos/MEGASYNC/Torrent Files/Allegiant (2016).torrent"
dp = "/home/carlos/Desktop"
data = TorrentParser.parse_filepath(fp)

s = Swarm()
s.set_meta_data(data, dp)


start = time()
p = Process(target=s.file_handler.padd_files)
p.start()
p.join()
print(f"Took about {time() - start}")