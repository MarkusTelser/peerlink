from PyQt6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt6.QtGui import QIcon

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
        table_widget.setItem(0, 1, QTableWidgetItem("data"))
        table_widget.setStyleSheet("background: green;")
        main_layout.addWidget(table_widget)
        
        self.setStyleSheet("background: purple")
    
class FilesTab(QWidget):
    def __init__(self):
        super().__init__()

class TorrentDetailView(QTabWidget):
    def __init__(self):
        super().__init__()
        
        self.addTab(GeneralTab(), QIcon('resources/general.svg'), "General")
        self.addTab(TrackersTab(), QIcon('resources/trackers.svg'), "Trackers")
        self.addTab(PeersTab(), QIcon('resources/peer.svg'), "Peers")
        self.addTab(FilesTab(), QIcon('resources/files.svg'), "Files")
        
        self.setStyleSheet("background-color: blue;")