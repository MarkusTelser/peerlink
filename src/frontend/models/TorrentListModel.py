from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import pyqtSlot, pyqtSignal

class TorrentListModel(QStandardItemModel):
    updatedData = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.updatedData.connect(self._update)
        self.data = list()
        self.torrent_list = list()
        self._update()
        
    @pyqtSlot()
    def _update(self):
        self.clear()
        self.setHorizontalHeaderLabels(["name", "size", "progress"])
        for i, row in enumerate(self.data):
            for j, column in enumerate(row):
                item = QStandardItem(column)
                self.setItem(i, j, item)