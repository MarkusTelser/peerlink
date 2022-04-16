from PyQt6.QtWidgets import QStatusBar, QLabel, QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

from src.frontend.utils.utils import convert_bitsps


class StatusBar(QStatusBar):
    def __init__(self):
        super().__init__()
        
        self.setObjectName("StatusBar")
        self.setContentsMargins(2, 2, 2, 2)

        download_icon = QLabel()
        download_icon.setPixmap(QIcon("resources/icons/downloading.svg").pixmap(QSize(20, 20)))
        self.addPermanentWidget(download_icon)
        
        self.download_speed = QLabel("0 B/s")
        self.download_speed.setContentsMargins(-1, -1, 10, -1)
        self.addPermanentWidget(self.download_speed)
        
        upload_icon = QLabel()
        upload_icon.setPixmap(QIcon("resources/icons/seeding.svg").pixmap(QSize(20, 20)))
        self.addPermanentWidget(upload_icon)
        
        self.upload_speed = QLabel("0 B/s")
        self.upload_speed.setContentsMargins(-1, -1, 10, -1)
        self.addPermanentWidget(self.upload_speed)
        
        peers_icon = QLabel()
        peers_icon.setPixmap(QIcon("resources/icons/peer.svg").pixmap(QSize(20, 20)))
        self.addPermanentWidget(peers_icon)
        
        self.peers = QLabel(self.tr("{} Peers").format(0))
        self.peers.setContentsMargins(-1, -1, 10, -1)
        self.addPermanentWidget(self.peers)
        
        nodes_icon = QLabel()
        nodes_icon.setPixmap(QIcon("resources/icons/node.svg").pixmap(QSize(20, 20)))
        self.addPermanentWidget(nodes_icon)
        
        self.nodes = QLabel(self.tr("{} Nodes").format(0))
        self.nodes.setContentsMargins(-1, -1, 10, -1)
        self.addPermanentWidget(self.nodes)
        
        self.speed = QPushButton("")
        self.speed.setIcon(QIcon("resources/icons/chart.svg"))
        self.addPermanentWidget(self.speed)
        
        self.statistics = QPushButton("")
        self.statistics.setIcon(QIcon("resources/icons/stats.svg"))
        self.addPermanentWidget(self.statistics)
    

    def _update(self, session):        
        self.download_speed.setText(convert_bitsps(session.download_speed))
        # self.upload_speed.setText()
        self.peers.setText(self.tr("{} Peers").format(session.peers))
        # self.nodes.setText()
        pass