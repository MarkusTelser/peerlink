from src.backend.metadata import TorrentParser
from time import time

fp = '/home/carlos/Code/Python/peerlink/data/all/ubuntu.torrent'
data = TorrentParser.parse_filepath(fp)


#print(data.pieces)
#bitfield = data.pieces
bitfield = open("ab'-AZ5770-S3tiEgcuFyKF'", 'rb').read()
print(bitfield)

start = time()
for i, byte in enumerate(bitfield):
            bits = '{0:08b}'.format(byte)
            for j, bit in enumerate(bits):
                if int(bit):
                    index = i * 8 + j

print('TOOK: ', time() - start)