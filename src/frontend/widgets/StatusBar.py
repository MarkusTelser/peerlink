from PyQt6.QtWidgets import QStatusBar, QLabel

class StatusBar(QStatusBar):
    def __init__(self):
        super().__init__()
        
        download_speed = QLabel("0 MB/s")
        self.addPermanentWidget(download_speed)
        
        upload_speed = QLabel("0 MB/s")
        self.addPermanentWidget(upload_speed)
        
        count_peers = QLabel("10 Peers")
        self.addPermanentWidget(count_peers)
        
        count_nodes = QLabel("0 DHT Nodes")
        self.addPermanentWidget(count_nodes)