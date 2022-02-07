from PyQt6.QtWidgets import QStatusBar, QLabel, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize


class StatusBar(QStatusBar):
    def __init__(self):
        super().__init__()
        
        download_icon = QLabel()
        download_icon.setPixmap(QIcon('resources/downloading.svg').pixmap(QSize(20, 20)))
        self.addPermanentWidget(download_icon)
        
        download_speed = QLabel("0 MB/s")
        download_speed.setContentsMargins(-1, -1, 10, -1)
        self.addPermanentWidget(download_speed)
        
        upload_icon = QLabel()
        upload_icon.setPixmap(QIcon('resources/seeding.svg').pixmap(QSize(20, 20)))
        self.addPermanentWidget(upload_icon)
        
        upload_speed = QLabel("0 MB/s")
        upload_speed.setContentsMargins(-1, -1, 10, -1)
        self.addPermanentWidget(upload_speed)
        
        peers_icon = QLabel()
        peers_icon.setPixmap(QIcon('resources/peer.svg').pixmap(QSize(20, 20)))
        self.addPermanentWidget(peers_icon)
        
        count_peers = QLabel("10 Peers")
        count_peers.setContentsMargins(-1, -1, 10, -1)
        self.addPermanentWidget(count_peers)
        
        nodes_icon = QLabel()
        nodes_icon.setPixmap(QIcon('resources/node.svg').pixmap(QSize(20, 20)))
        self.addPermanentWidget(nodes_icon)
        
        count_nodes = QLabel("0 Nodes")
        count_nodes.setContentsMargins(-1, -1, 10, -1)
        self.addPermanentWidget(count_nodes)
        
        self.speed = QPushButton('')
        self.speed.setIcon(QIcon('resources/chart.svg'))
        self.addPermanentWidget(self.speed)
        
        self.statistics = QPushButton('')
        self.statistics.setIcon(QIcon('resources/stats.svg'))
        self.addPermanentWidget(self.statistics)
        
        self.setContentsMargins(2, 2, 2, 2)
        self.setStyleSheet("""
        QPushButton{
            background-color: transparent; 
            border: 1px solid transparent;
            border-radius: 3px;
            padding: 3px;
        }
        QPushButton:hover{
            background: palette(button)
        }
        """)