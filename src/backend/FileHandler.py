from hashlib import sha1
from threading import RLock
from math import ceil
from os.path import join, exists, dirname
from os import mkdir, makedirs
from shutil import copytree, rmtree

class FileHandler:
    def __init__(self, data, path):
        self.lock = RLock()
        
        self.data = data
        self._path = path

    
    def write_piece(self, index, data):
        bit_start = index * self.data.piece_length
        piece_length = min(self.data.piece_length, self.data.files.length - self.data.piece_length * index)
        bit_end = bit_start + piece_length
        
        if len(data) != piece_length:
            raise Exception("piece has wrong size")
        if index < 0 or index >= self.data.pieces_count:
            raise Exception('wrong piece id')
        
        if self.data.has_multi_file:
            file_list = self.get_files_bitrange(bit_start, bit_end)
        else:
            file_list = [self.data.files]
        
        with self.lock:    
            full_length = len(data)
            
            for i, file in enumerate(file_list):
                # create file and directorys, if don't exist
                path = join(self.path, file.fullpath)
                if not exists(path):
                    makedirs(dirname(path), exist_ok=True)
                    open(path, "w").close()
                
                with open(path, 'rb+') as f:
                    write_start = max(0, bit_start - file.startbit) if i == 0 else 0
                    f.seek(write_start)
                    
                    write_length = full_length
                    if i == 0 and full_length > file.startbit + file.length - bit_start:
                        write_length = file.startbit + file.length - bit_start
                    elif i != 0 and full_length > file.length:
                        write_length = file.length
                    f.write(data[:write_length])
                    data = data[write_length:]
                    full_length -= write_length
    
    
    def verify_piece(self, index, data):
        if index < 0 or index >= self.data.pieces_count:
            raise Exception('wrong piece id')
        
        piece_hash = sha1(data).digest()
        reference_hash = self.data.pieces[20 * index: 20 + 20 * index]
        return piece_hash == reference_hash
        

    def check_all_pieces(self):
        invalid_pieces = list()
        for i in range(self.data.pieces_count):
            if not self.check_piece(i):
                invalid_pieces.append(i)
        
        valid_torrent = len(invalid_pieces) == 0 
        return valid_torrent, invalid_pieces
    
    
    def check_piece(self, index):
        if index < 0 or index >= self.data.pieces_count:
            raise Exception('wrong piece id')
        # calculate start, end of piece in bits and length (last piece may be smaller)
        bit_start = index * self.data.piece_length
        piece_length = self.data.piece_length
        if index == self.data.pieces_count - 1 and self.data.files.length % self.data.piece_length != 0: # last piece may be shorter
            piece_length = self.data.files.length % self.data.piece_length
        bit_end = bit_start + piece_length
        
        # read piece across multiple files
        data = bytes()
        data_length = piece_length
        file_list = self.get_files_bitrange(bit_start, bit_end)
        print("---", index, "|", bit_start, bit_end, piece_length, "|", [file.name for file in file_list])
        for i, file in enumerate(file_list):
            if exists(join(self.path, file.fullpath)):
                with open(join(self.path, file.fullpath), 'rb+') as f:
                    read_start = max(0, bit_start - file.startbit) if index == 0 else 0
                    f.seek(read_start)
                        
                    read_length = data_length
                    if i == 0 and data_length > file.startbit + file.length - bit_start:
                        read_length = file.startbit + file.length - bit_start
                        print("here1", read_length)
                    elif i != 0 and data_length > file.length:
                        read_length = file.length
                        print("here2", read_length)
                    data += f.read(read_length)
                    data_length -= read_length
        
        # check calculated hash with given hash from torrent file 
        piece_hash = sha1(data).digest()
        reference_hash = self.data.pieces[20 * index: 20 + 20 * index]
        return piece_hash == reference_hash
    
    
    def get_files_bitrange(self, startbit, endbit, current_node=None):
        if current_node == None:
            current_node = self.data.files

        file_list = list()
        
        if current_node.has_children():
            for child in current_node.children:
                files = self.get_files_bitrange(startbit, endbit, child)
                if files and files[0] == 'stop':
                    for file in files[1]:
                        file_list.append(file)
                    return file_list
                for file in files:
                    file_list.append(file)
        else:
            # case one: range starts in this node
            if startbit >= current_node.startbit and startbit < current_node.startbit + current_node.length:
                if current_node not in file_list:
                    file_list.append(current_node)
            # case two: range started before this node and ends after this node (in-between-node)
            if startbit < current_node.startbit and endbit > current_node.startbit + current_node.length:
                if current_node not in file_list:
                    file_list.append(current_node)
            # case three: range ends in this node
            if endbit > current_node.startbit and endbit <= current_node.startbit + current_node.length:
                if current_node not in file_list:
                    file_list.append(current_node)
                return 'stop', file_list
        
        return file_list
    
    def padd_files(self, current_node=None):
        if current_node == None:
            current_node = self.data.files
        
        if current_node.has_children():
            if not exists(join(self.path, current_node.fullpath)):
                mkdir(join(self.path, current_node.fullpath))
            for file in current_node.children:
                self.padd_files(file)
        elif not exists(join(self.path, current_node.fullpath)):
            with open(join(self.path, current_node.fullpath), 'wb+') as f:
                # padd file in chunks, otherwise high cpu, ram usage
                BLOCK_SIZE = 2 ** 27
                write_size = current_node.length
                for _ in range(ceil(current_node.length / BLOCK_SIZE)):
                    f.write(b'\x00' * min(write_size, BLOCK_SIZE))
                    write_size -= BLOCK_SIZE
                    
    @property 
    def path(self):
        return self._path
    
    @path.setter
    def path(self, new_path):
        if not exists(new_path):
            raise Exception("path doesn't exist")
        if self._path == new_path:
            raise Exception("same path as before")
        if '/' not in new_path:
            raise Exception('no relative paths')
        
        try:
            copytree(join(self._path, self.data.files.name), join(new_path, self.data.files.name), symlinks=True, dirs_exist_ok=True)
            rmtree(join(self._path, self.data.files.name))
        except PermissionError:
            raise Exception("don't have the rights, no permissions")
        
        self._path = new_path
    
    # TODO check errors, exceptions throw
    # TODO add ignoring of files that are not selected

if __name__ == "__main__":
    """
    from src.backend.metadata.TorrentParser import TorrentParser
    fp = "/home/carlos/Desktop/Rise of the Planet of the Apes (2011) [1080p]/Rise of the Planet of the Apes (2011).torrent"
    data = TorrentParser.parse_filepath(fp)
    print(data.files)
    f = FileHandler(data, "/home/carlos/Downloads/")
    print(f.check_piece(0))
    print(f.check_all_pieces(), data.pieces_count)
    
    f.path = '/home/carlos/Desktop/g'
    fp = "/home/carlos/Code/Python/peerlink/data/all/solo.torrent"
    f.data = TorrentParser.parse_filepath(fp)
    f.padd_files()
    """
    from src.backend.metadata.TorrentData import *
    
    # create custom data
    
    children = [TorrentFile("file1", 10), TorrentFile("file2", 20), TorrentFile("file3", 30)]
    parent_folder = TorrentFile("root_folder")
    parent_folder.children = children
    print(parent_folder.startbit)
    data = TorrentData()
    data.files = parent_folder
    calc_folder_size(parent_folder)
    calc_bitstart_fullpath(parent_folder)
    
    data.piece_length = 6
    data.pieces_count = 10
    data.pieces = b'\xde\xb6\xc1\x1e\x19q\xaaa\xdb\xbc\xbcv\xe5\xeauS\xa5\xbe\xa7\xb7' + b'\xde\xb6\xc1\x1e\x19q\xaaa\xdb\xbc\xbcv\xe5\xeauS\xa5\xbe\xa7\xb7'# + b')\xbd\x13(>R\x95\x1e\xfc{/\xb6\xadO\xc7Y\xfak\xf7\xef'
    
    f = FileHandler(data, '/home/carlos/Desktop')
    f.padd_files()
    print(f.check_all_pieces())
    f.write_piece(2, b'\x99'*6)
    
    f.path = '/home/carlos/Downloads'