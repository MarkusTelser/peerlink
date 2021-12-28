from PyQt6.QtWidgets import QPushButton, QToolBar, QLabel
from PyQt6.QtGui import QAction, QIcon

class ToolBar(QToolBar):
    def __init__(self):
        super().__init__()
        
        self.setMovable(False)
        
        self.setStyleSheet("margin-left: 15px; margin: 7px; border: none")
       
        self.open_file = QPushButton(self)
        self.open_file.setText("open file")
        self.open_file.setStyleSheet("QPushButton{background: palette(window); border: palette(window)}QPushButton:hover{background: palette(button)}")
        self.open_file.setIcon(QIcon('resources/file.svg'))
        self.addWidget(self.open_file)
        
        self.open_magnet_link = QPushButton(self)
        self.open_magnet_link.setText("open magnet link")
        self.open_magnet_link.setIcon(QIcon('resources/link.svg'))
        self.open_magnet_link.setStyleSheet("QPushButton{background: palette(window); border: palette(window)}QPushButton:hover{background: palette(button)}")
        self.addWidget(self.open_magnet_link)
        
        self.addSeparator()
        
        self.resume = QPushButton(self)
        self.resume.setText("resume")
        self.resume.setIcon(QIcon('resources/resume.svg'))
        self.resume.setStyleSheet("QPushButton{background: palette(window); border: palette(window)}QPushButton:hover{background: palette(button)}")
        self.addWidget(self.resume)
        
        self.pause = QPushButton(self)
        self.pause.setText("pause")
        self.pause.setIcon(QIcon('resources/pause.svg'))
        self.pause.setStyleSheet("QPushButton{background: palette(window); border: palette(window)}QPushButton:hover{background: palette(button)}")
        self.addWidget(self.pause)
        
        self.resume_all = QPushButton(self)
        self.resume_all.setText("resume all")
        self.resume_all.setIcon(QIcon('resources/resume.svg'))
        self.resume_all.setStyleSheet("QPushButton{background: palette(window); border: palette(window)}QPushButton:hover{background: palette(button)}")
        self.addWidget(self.resume_all)
        
        self.pause_all = QPushButton(self)
        self.pause_all.setText("pause all")
        self.pause_all.setIcon(QIcon('resources/pause.svg'))
        self.pause_all.setStyleSheet("QPushButton{background: palette(window); border: palette(window)}QPushButton:hover{background: palette(button)}")
        self.addWidget(self.pause_all)