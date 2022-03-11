
from abc import abstractmethod
from logging import exception
from src.backend.Session import Session
from src.backend.metadata import TorrentParser
from src.backend.metadata.MagnetLink import MagnetLink, MagnetParser
from src.backend.swarm import Swarm
from abc import abstractmethod, ABC
from time import sleep

def run():
    fp = 'data/all/folder.torrent'
    #fp = 'data/all/test.torrent'
    #fp = 'data/all/ubuntu.torrent'
    #fp = 'data/archive/cIOS-firmware-images_archive.torrent'
    #fp = 'data/ubuntu-18.04.6-desktop-amd64.iso.torrent'
    
    
    t = Swarm()
    #magnet_link = 'magnet:?xt=urn:btih:A53E3226A59F4032EEFA26CEFE6A9BDEE17AA970&dn=KMSpico%2010.1.8%20FINAL%20%2B%20Portable%20(Office%20and%20Windows%2010%20Activator&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.openbittorrent.com%3A6969%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2710%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2780%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2730%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337&tr=http%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce'
    magnet_link = 'magnet:?xt=urn:btih:362e48d8dfaa287a752800a9df414b1a189ac335&dn=Who%20Am%20I%20(2014)%20%5bBluRay%5d%20%5b1080p%5d%20%5bYTS.AM%5d&tr=udp%3a%2f%2ftracker.coppersurfer.tk%3a6969%2fannounce&tr=udp%3a%2f%2f9.rarbg.com%3a2710%2fannounce&tr=udp%3a%2f%2fp4p.arenabg.com%3a1337&tr=udp%3a%2f%2ftracker.leechers-paradise.org%3a6969&tr=udp%3a%2f%2ftracker.internetwarriors.net%3a1337&tr=udp%3a%2f%2ftracker.opentrackr.org%3a1337%2fannounce'
    magnet = MagnetParser.parse(magnet_link)
    t.set_magnet_link(magnet)
    print([list(magnet.trackers)])
    s = Session()
    s.add(t)
    s.download_meta(0)
    
    #sleep(10)
    #s.stop(0)
    
    
    # or this
    """
    
    #fp = 'data/all/magnet.torrent'
    data = TorrentParser.parse_filepath(fp)
    save_path = '/home/carlos/Desktop'
    print(data.announces)
    
    t = Swarm()
    t.set_meta_data(data, save_path)
    
    s = Session()
    s.add(t)
    s.resume(0)
    """
    sleep(10000)

run()