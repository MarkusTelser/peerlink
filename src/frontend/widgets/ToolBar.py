from PyQt6.QtWidgets import QToolBar

from PyQt6.QtWidgets import QToolBar
from PyQt6.QtGui import QAction

class ToolBar(QToolBar):
    def __init__(self):
        super().__init__()
        
        self.setMovable(False)
        
        self.open_file = QAction("Open file", self)
        self.open_file.setToolTip("open torrent file to download")
        self.addAction(self.open_file)
        
        self.open_magnet_link = QAction("Open magnet link", self)
        self.open_magnet_link.setToolTip("open magnet link")
        self.addAction(self.open_magnet_link)
        
        self.resume = QAction("Resume", self)
        self.resume.setToolTip("is resuming the current torrent")
        self.addAction(self.resume)
        
        self.pause = QAction("Pause", self)
        self.pause.setToolTip("is pausing the current torrent")
        self.addAction(self.pause)
        
        self.resume_all = QAction("Resume All", self)
        self.resume_all.setToolTip("resuming all torrents")
        self.addAction(self.resume_all)
        
        self.pause_all = QAction("Pause All", self)
        self.pause_all.setToolTip("pausing all torrents")
        self.addAction(self.pause_all)