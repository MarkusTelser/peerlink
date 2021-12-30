from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import pyqtSlot, pyqtSignal

class TorrentListModel(QStandardItemModel):
    updatedData = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.setHorizontalHeaderLabels(["name", "size", "progress"])
        self.data = list()
        self._update()
        
    @pyqtSlot()
    def _update(self):
        for i, row in enumerate(self.data):
            for j, column in enumerate(row):
                item = QStandardItem(column)
                self.setItem(i, j, item)