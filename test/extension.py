from src.backend.peer_protocol.PieceManager import PieceManager
from src.backend.peer_protocol.Peer import Peer
from src.backend.FileHandler import FileHandler
from src.backend.metadata.TorrentParser import TorrentParser

fp = "data/all/last.torrent"
data = TorrentParser.parse_filepath(fp)

l = [('90.101.77.23', 6881), ('193.23.249.55', 49155)]

piece_manager = PieceManager(data.pieces_count)
file_handler = FileHandler(data, "downloaded.file")

for address in l:
    p = Peer(address, data, piece_manager, file_handler)
    p.start()