from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from datetime import datetime

from src.frontend.utils.utils import convert_bits


class TorrentListModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels(["name", "size", "progress", "health", "availability", "share ratio", "start date", "creation date"])
    
    def remove(self, index):
        self.removeRow(index)
    
    def remove_all(self):
        self.setRowCount(0)

    def append(self, swarm):
        row = self._get_row(swarm)
        self.appendRow(row)

    def _update(self, swarm_list):
        self.remove_all()
        for swarm in swarm_list:
            row = self._get_row(swarm)
            self.appendRow(row)

    def _get_row(self, swarm):
        row = list()

        name = swarm.data.files.name
        item = QStandardItem(name)
        item.setData(self.rowCount(), Qt.ItemDataRole.InitialSortOrderRole + 69)
        row.append(item)
        
        size = convert_bits(swarm.data.files.length)
        item = QStandardItem(size)
        row.append(item)
        
        progress = f"{swarm.piece_manager.downloaded_percent}%"
        item = QStandardItem(progress)
        row.append(item)
        
        health = f"{swarm.piece_manager.health}%"
        item = QStandardItem(health)
        row.append(item)
        
        availability = str(swarm.piece_manager.availability)
        item = QStandardItem(availability)
        row.append(item)
        
        share_ratio = str()
        item = QStandardItem(share_ratio)
        row.append(item)

        if len(swarm.start_date) > 0:
            start_date = datetime.fromisoformat(swarm.start_date)
            local_date = start_date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            local_date = "not yet"
        item = QStandardItem(local_date)
        row.append(item)
        
        creation_date = swarm.data.creation_date
        item = QStandardItem(creation_date)
        row.append(item)

        return row