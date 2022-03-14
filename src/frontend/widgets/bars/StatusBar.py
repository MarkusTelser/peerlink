from PyQt6.QtWidgets import QStatusBar, QLabel, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

from src.frontend.utils.utils import convert_bitsps


class StatusBar(QStatusBar):
    def __init__(self):
        super().__init__()
        
        download_icon = QLabel()
        download_icon.setPixmap(QIcon('resources/downloading.svg').pixmap(QSize(20, 20)))
        self.addPermanentWidget(download_icon)
        
        self.download_speed = QLabel("0 B/s")
        self.download_speed.setContentsMargins(-1, -1, 10, -1)
        self.addPermanentWidget(self.download_speed)
        
        upload_icon = QLabel()
        upload_icon.setPixmap(QIcon('resources/seeding.svg').pixmap(QSize(20, 20)))
        self.addPermanentWidget(upload_icon)
        
        self.upload_speed = QLabel("0 B/s")
        self.upload_speed.setContentsMargins(-1, -1, 10, -1)
        self.addPermanentWidget(self.upload_speed)
        
        peers_icon = QLabel()
        peers_icon.setPixmap(QIcon('resources/peer.svg').pixmap(QSize(20, 20)))
        self.addPermanentWidget(peers_icon)
        
        self.peers = QLabel("0 Peers")
        self.peers.setContentsMargins(-1, -1, 10, -1)
        self.addPermanentWidget(self.peers)
        
        nodes_icon = QLabel()
        nodes_icon.setPixmap(QIcon('resources/node.svg').pixmap(QSize(20, 20)))
        self.addPermanentWidget(nodes_icon)
        
        self.nodes = QLabel("0 Nodes")
        self.nodes.setContentsMargins(-1, -1, 10, -1)
        self.addPermanentWidget(self.nodes)
        
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

    def _update(self, session):        
        self.download_speed.setText(convert_bitsps(session.download_speed))
        # self.upload_speed.setText()
        self.peers.setText(f"{session.peers} Peers")
        # self.nodes.setText()
        pass