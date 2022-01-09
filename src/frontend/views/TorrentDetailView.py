from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt6.QtGui import QIcon
from src.backend.metadata.TorrentData import TorrentFile

from src.backend.swarm import Swarm
from src.frontend.models.TorrentTreeModel import TorrentTreeModel
from src.frontend.views.TorrentTreeView import TorrentTreeView

class GeneralTab(QWidget):
    def __init__(self):
        super().__init__()
 
class TrackersTab(QWidget):
    def __init__(self):
        super().__init__()    
        
class PeersTab(QWidget):
    def __init__(self):
        super().__init__()   
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        table_widget = QTableWidget()
        table_widget.setColumnCount(4)
        table_widget.setRowCount(5)
        headers = ["ip", "port", "connection type", "status"]
        table_widget.setHorizontalHeaderLabels(headers)
        table_widget.verticalHeader().hide()
        table_widget.horizontalHeader().setStretchLastSection(True)
        table_widget.setItem(0, 1, QTableWidgetItem("data"))
        table_widget.setStyleSheet("background: green;")
        main_layout.addWidget(table_widget)
        
        self.setStyleSheet("background: purple")
    
class FilesTab(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        self.model = TorrentTreeModel()
        self.tree_view = TorrentTreeView(self.model)
        self.tree_view.setModel(self.model)
        self.tree_view.setStyleSheet("background: green;")
        main_layout.addWidget(self.tree_view)
        
    def _update(self, data: TorrentFile):
        self.model.update(data)

class TorrentDetailView(QTabWidget):
    def __init__(self):
        super().__init__()
        
        self.general_tab = GeneralTab()
        self.trackers_tab = TrackersTab()
        self.peers_tab = PeersTab()
        self.files_tab = FilesTab()
        
        self.addTab(self.general_tab, QIcon('resources/general.svg'), "General")
        self.addTab(self.trackers_tab, QIcon('resources/trackers.svg'), "Trackers")
        self.addTab(self.peers_tab, QIcon('resources/peer.svg'), "Peers")
        self.addTab(self.files_tab, QIcon('resources/files.svg'), "Files")
        
        self.setStyleSheet("background-color: blue;")
    
    def _update(self, dt: Swarm):
        self.files_tab._update(dt.data.files)