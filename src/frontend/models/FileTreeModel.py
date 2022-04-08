from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtWidgets import QFileIconProvider
from PyQt6.QtCore import QFileInfo, pyqtSignal

from src.backend.metadata.TorrentData import TorrentFile


class FileTreeModel(QStandardItemModel):
    update_data = pyqtSignal()
    
    def __init__(self, data=None):
        super().__init__()
        
        self.file_data = data
        self.root_node = self.invisibleRootItem()
        
        headers = [self.tr("name"), self.tr("size")]
        self.setHorizontalHeaderLabels(headers)
        
    def update(self, data: TorrentFile):
        self.file_data = data
        self.removeRow(0)
        self._update(self.file_data, self.root_node)
        self.update_data.emit()
    
    def _update(self, file_data: TorrentFile, parent_node: QStandardItem):
        name = QStandardItem(file_data.name)
        name.setEditable(False)
        #name.setCheckable(True)
        #name.setCheckState(QStandardItem().checkState().Checked)

        # set fitting icon to file type
        if not file_data.has_children():
            fileInfo = QFileInfo(file_data.name)
            iconProvider = QFileIconProvider()
            icon = iconProvider.icon(fileInfo)
            name.setIcon(icon)
        else:
            folder_icon = QIcon('resources/icons/folder.svg')
            name.setIcon(folder_icon)
        
        size = self.convert_bits(file_data.length)
        size = QStandardItem(size)
        size.setEditable(False)
        
        parent_node.appendRow([name, size])
        
        for child_data in file_data.children:    
            self._update(child_data, name)
            
    
    def convert_bits(self, bits: int):
        if bits < 1000:
            return f"{bits} B"
        if bits / 1024 < 1000:
            return f"{int(round(bits / 1024, 0))} KiB"
        elif bits / (1024 ** 2) < 1000:
            return f"{round(bits / (1024 ** 2), 1)} MiB"
        elif bits  / (1024 ** 3) < 1000:
            return f"{round(bits / (1024 ** 3), 2)} GiB"
        elif bits / (1024 ** 4) < 1000: 
            return f"{round(bits / (1024 ** 4), 2)} TiB"
        elif bits / (1024 ** 5) < 1000:
            return f"{round(bits / (1024 ** 5), 3)} PiB"