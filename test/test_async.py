
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
    
    
    """
    t = Swarm()
    magnet_link = 'magnet:?xt=urn:btih:5C620FD5694A4B0874F732970AAFE23E536F2FE8&dn=Blacklight+%282022%29+%281080p%29+%5BWEBRip%5D+%5B5.1%5D+%5BYTS+MX%5D&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.internetwarriors.net%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.cyberia.is%3A6969%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Fipv4.tracker.harry.lu%3A80%2Fannounce&tr=udp%3A%2F%2Fretracker.lanta-net.ru%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.tiny-vps.com%3A6969%2Fannounce&tr=udp%3A%2F%2Fexodus.desync.com%3A6969%2Fannounce&tr=udp%3A%2F%2Fipv6.tracker.harry.lu%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2710%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.open-internet.nl%3A6969%2Fannounce&tr=udp%3A%2F%2Fopen.demonii.si%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.pirateparty.gr%3A6969%2Fannounce&tr=udp%3A%2F%2Fdenis.stalker.upeer.me%3A6969%2Fannounce&tr=udp%3A%2F%2Fp4p.arenabg.com%3A1337%2Fannounce'
    magnet = MagnetParser.parse(magnet_link)
    t.set_magnet_link(magnet)
    print([list(magnet.trackers)])
    s = Session()
    s.add(t)
    s.download_meta(0)
    
    sleep(5)
    s.stop(0)
    """
    # or this
    
    #fp = 'data/all/magnet.torrent'
    data = TorrentParser.parse_filepath(fp)
    save_path = '/home/carlos/Desktop'
    print(data.announces)
    
    t = Swarm()
    t.set_meta_data(data, save_path)
    
    s = Session()
    s.add(t)
    s.resume(0)
    
    sleep(10000)

run()