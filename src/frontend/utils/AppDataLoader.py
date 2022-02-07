from PyQt6.QtCore import QStandardPaths
from os.path import exists, join
from os import mkdir, listdir, remove
from random import choices
from string import ascii_uppercase, digits
from shutil import move

from src.backend.metadata.TorrentParser import TorrentParser
from src.backend.metadata.Bencoder import bdecode


class AppDataLoader:
    def __init__(self):
        self.path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        
        if not exists(self.path):
            mkdir(self.path)
        if not exists(join(self.path, 'torrents')):
            mkdir(join(self.path, 'torrents'))
        if not exists(join(self.path, 'logs')):
            mkdir(join(self.path, 'logs'))
    
    def backup_torrent(self, arg):
        new_name = ''.join(choices(ascii_uppercase + digits, k=50)) + '.torrent'
        new_path = join(self.path, 'torrents', new_name) 
        
        # move file to byte data
        if type(arg) == str:
            try:
                move(arg, new_path)
            except FileNotFoundError:
                print('file not found')
            except PermissionError:
                print('missing permission')
        # write byte data
        elif type(arg) == bytes:
            with open(new_path, 'wb') as f:
                f.write(arg)
        else:
            raise Exception('wrong arg')
        
        return new_name.split('.')[0]

    def remove_torrent(self, backup_name):
        data_path = join(self.path, 'torrents') 
        
        for file in listdir(data_path):
            if backup_name in file:
                print(f"deleted {file}")
                remove(join(data_path, file))
    
    def load_torrents(self):
        torrent_list = list()
        
        if not exists(join(self.path, 'torrents')):
            return torrent_list
        
        torrents = {x.split('.')[0] for x in listdir(join(self.path, 'torrents'))}
        
        for torrent in torrents:
            raw_path = join(self.path, 'torrents', torrent)
            if not exists(raw_path + '.torrent') or not exists(raw_path + '.ben'):
                continue
            
            file_path = raw_path + '.torrent'
            torrent_file = TorrentParser.parse_filepath(file_path)
            extra = open(raw_path +  '.ben', 'rb').read()
            torrent_extra = bdecode(extra)
            torrent_list.append((torrent_file, torrent_extra))
        
        print(torrent_list)
        
        return torrent_list