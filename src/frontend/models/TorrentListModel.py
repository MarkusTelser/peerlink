from PyQt6.QtWidgets import QApplication, QProgressBar, QStyledItemDelegate, QStyleOptionProgressBar, QStyle
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from src.frontend.utils.utils import convert_bits
import datetime

class TorrentListModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.data = list()
        self.torrent_list = list()
        self.setHorizontalHeaderLabels(["name", "size", "progress", "health", "availability", "share ratio", "start date", "creation date"])
        self._update()
    
    def remove(self, index=-1):
        if index == -1:
            self.torrent_list = list()
            self.data = list()
        else:
            del self.torrent_list[index]
            del self.data[index]
        self._update()
    
    def append(self, torrent_swarm):
        name = torrent_swarm.data.files.name
        size = convert_bits(torrent_swarm.data.files.length)
        self.data.append([name, size])
        self.torrent_list.append(torrent_swarm)
        self._update()
    
    def _update(self):
        self.setRowCount(0)
        for i, torrent in enumerate(self.torrent_list):
            name = torrent.data.files.name
            item = QStandardItem(name)
            item.setData(i, Qt.ItemDataRole.InitialSortOrderRole + 69)
            self.setItem(i, 0, item)
            
            size = convert_bits(torrent.data.files.length)
            item = QStandardItem(size)
            self.setItem(i, 1, item)
            
            progress = f"{torrent.piece_manager.downloaded}%"
            item = QStandardItem(progress)
            self.setItem(i, 2, item)
            
            health = f"{torrent.piece_manager.health}%"
            item = QStandardItem(health)
            self.setItem(i, 3, item)
            
            availability = str(torrent.piece_manager.availability)
            item = QStandardItem(availability)
            self.setItem(i, 4, item)
            
            if len(torrent.start_date) > 0:
                start_date = datetime.fromisoformat(torrent.start_date).strftime("%Y-%m-%d %H:%M:%S")
                local_date = start_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                local_date = "not yet"
            item = QStandardItem(local_date)
            self.setItem(i, 6, item)
            
            creation_date = torrent.data.creation_date
            item = QStandardItem(creation_date)
            self.setItem(i, 7, item)
