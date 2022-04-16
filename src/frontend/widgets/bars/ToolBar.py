from PyQt6.QtWidgets import QPushButton, QToolBar
from PyQt6.QtGui import QIcon

from src.frontend.widgets.SearchBox import SearchBar


class ToolBar(QToolBar):
    def __init__(self):
        super().__init__()
        
        self.setMovable(False)
        self.setObjectName("ToolBar")
        
        self.open_file = QPushButton(self)
        self.open_file.setText(self.tr("open file"))
        self.open_file.setIcon(QIcon('resources/icons/file.svg'))
        self.addWidget(self.open_file)
        
        self.open_link = QPushButton(self)
        self.open_link.setText(self.tr("open magnet link"))
        self.open_link.setIcon(QIcon('resources/icons/link.svg'))
        self.addWidget(self.open_link)
        
        self.addSeparator()
        
        self.resume = QPushButton(self)
        self.resume.setText(self.tr("resume"))
        self.resume.setIcon(QIcon('resources/icons/resume.svg'))
        self.addWidget(self.resume)
        
        self.pause = QPushButton(self)
        self.pause.setText(self.tr("pause"))
        self.pause.setIcon(QIcon('resources/icons/pause.svg'))
        self.addWidget(self.pause)
        
        self.remove = QPushButton()
        self.remove.setText(self.tr("remove"))
        self.remove.setIcon(QIcon('resources/icons/remove.svg'))
        self.addWidget(self.remove)
        
        self.addSeparator()
        
        self.resume_all = QPushButton(self)
        self.resume_all.setText(self.tr("resume all"))
        self.resume_all.setIcon(QIcon('resources/icons/resume.svg'))
        self.addWidget(self.resume_all)
        
        self.pause_all = QPushButton(self)
        self.pause_all.setText(self.tr("pause all"))
        self.pause_all.setIcon(QIcon('resources/icons/pause.svg'))
        self.addWidget(self.pause_all)
        
        self.remove_all = QPushButton(self)
        self.remove_all.setText(self.tr("remove all"))
        self.remove_all.setIcon(QIcon('resources/icons/remove.svg'))
        self.addWidget(self.remove_all)
        
        self.addSeparator()
        self.addSeparator()
        
        self.search_bar = SearchBar()
        self.addWidget(self.search_bar)