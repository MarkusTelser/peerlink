from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import pyqtSlot, pyqtSignal
from src.frontend.utils.utils import convert_bits

class TorrentListModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.data = list()
        self.torrent_list = list()
        self._update()
    
    def remove(self, index=-1):
        if index == -1:
            self.torrent_list = list()
            self.data = list()
        else:
            del self.torrent_list[index]
            del self.data[index]
        self._update()
    
    def append(self, name, size):
        readable_size = convert_bits(size)
        self.data.append([name, readable_size])
        self._update()
    
    def _update(self):
        self.clear()
        self.setHorizontalHeaderLabels(["name", "size", "progress"])
        for i, row in enumerate(self.data):
            for j, column in enumerate(row):
                item = QStandardItem(column)
                self.setItem(i, j, item)