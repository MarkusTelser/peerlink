from PyQt6.QtWidgets import QToolBar

from PyQt6.QtWidgets import QToolBar
from PyQt6.QtGui import QAction

class ToolBar(QToolBar):
    def __init__(self):
        super().__init__()
        
        self.setMovable(False)
        
        resume = QAction("Resume", self)
        resume.setToolTip("is resuming the current torrent")
        self.addAction(resume)
        
        pause = QAction("Pause", self)
        pause.setToolTip("is pausing the current torrent")
        self.addAction(pause)
        
        resume_all = QAction("Resume All", self)
        resume_all.setToolTip("resuming all torrents")
        self.addAction(resume_all)
        
        pause_all = QAction("Pause All", self)
        pause_all.setToolTip("pausing all torrents")
        self.addAction(pause_all)