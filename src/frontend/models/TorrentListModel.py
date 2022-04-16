from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt
from datetime import datetime

from src.frontend.utils.utils import convert_bits, convert_seconds


class TorrentListModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        labels = ["name", "size", "download speed", "eta", "downloaded", "progress", "health", "availability", "share ratio", "creation date", "start date", "finish date"]
        labels = [self.tr(label) for label in labels]
        self.setHorizontalHeaderLabels(labels)
    
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
        
        download_speed = str(swarm.speed_measurer.avg_down_speed)
        item = QStandardItem(download_speed)
        row.append(item)

        eta = chr(0x221E) if swarm.speed_measurer.eta == -1 else convert_seconds(swarm.speed_measurer.eta)
        item = QStandardItem(eta)
        row.append(item)

        downloaded = convert_bits(swarm.piece_manager.downloaded_bytes)
        item = QStandardItem(downloaded)
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

        creation_date = swarm.data.creation_date
        item = QStandardItem(creation_date)
        row.append(item)

        if len(swarm.start_date) > 0:
            start_date = datetime.fromisoformat(swarm.start_date)
            local_date = start_date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            local_date = self.tr("not yet")
        item = QStandardItem(local_date)
        row.append(item)

        if len(swarm.finish_date) > 0:
            finish_date = datetime.fromisoformat(swarm.finish_date)
            local_date = finish_date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            local_date = self.tr("not yet")
        item = QStandardItem(local_date)
        row.append(item)        

        return row