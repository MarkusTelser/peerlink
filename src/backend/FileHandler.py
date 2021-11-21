from hashlib import sha1
from threading import RLock

class FileHandler:
    def __init__(self, data, path):
        self.lock = RLock()
        self.data = data
        self.path = path

    def write_block(self, id, start, data):
        self.lock.acquire()
        with open(self.path, 'rb+') as f:
            f.seek(self.data.piece_length * id + start)
            f.write(data)
        self.lock.release()

    def check_hash(self, id, hash):
        with open(self.path, "rb") as f:
            f.seek()
            data = f.read(self.data.piece_length)

        file_hash = sha1(data).digest()
        return hash == file_hash
        

    def check_all_hashes():
        pass