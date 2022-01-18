from PyQt6.QtWidgets import QPushButton, QToolBar
from PyQt6.QtGui import QIcon

from src.frontend.widgets.SearchBox import SearchBar

class ToolBar(QToolBar):
    def __init__(self):
        super().__init__()
        
        self.setMovable(False)
        
        self.setStyleSheet("margin-left: 15px; margin: 7px; border: none")
       
        self.open_file = QPushButton(self)
        self.open_file.setText("open file")
        self.open_file.setIcon(QIcon('resources/file.svg'))
        self.addWidget(self.open_file)
        
        self.open_link = QPushButton(self)
        self.open_link.setText("open magnet link")
        self.open_link.setIcon(QIcon('resources/link.svg'))
        self.addWidget(self.open_link)
        
        self.addSeparator()
        
        self.resume = QPushButton(self)
        self.resume.setText("resume")
        self.resume.setIcon(QIcon('resources/resume.svg'))
        self.addWidget(self.resume)
        
        self.pause = QPushButton(self)
        self.pause.setText("pause")
        self.pause.setIcon(QIcon('resources/pause.svg'))
        self.addWidget(self.pause)
        
        self.remove = QPushButton()
        self.remove.setText("remove")
        self.remove.setIcon(QIcon('resources/remove.svg'))
        self.addWidget(self.remove)
        
        self.addSeparator()
        
        self.resume_all = QPushButton(self)
        self.resume_all.setText("resume all")
        self.resume_all.setIcon(QIcon('resources/resume.svg'))
        self.addWidget(self.resume_all)
        
        self.pause_all = QPushButton(self)
        self.pause_all.setText("pause all")
        self.pause_all.setIcon(QIcon('resources/pause.svg'))
        self.addWidget(self.pause_all)
        
        self.remove_all = QPushButton(self)
        self.remove_all.setText("remove all")
        self.remove_all.setIcon(QIcon('resources/remove.svg'))
        self.addWidget(self.remove_all)
        
        self.addSeparator()
        self.addSeparator()
        
        self.search_bar = SearchBar()
        self.addWidget(self.search_bar)
        
        self.setStyleSheet("""
        QToolBar{

        }
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