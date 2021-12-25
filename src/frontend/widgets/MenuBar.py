from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QIcon, QKeySequence

class MenuBar(QMenuBar):
    def __init__(self):
        super().__init__()
        
         # file menu
        fileMenu = QMenu("&File", self)
        fileIcon = QIcon("resources/file.svg")
        fileShortcut = QKeySequence("Ctrl+O")
        fileMenu.addAction(fileIcon, "Open file", self.pressed, fileShortcut)
        fileMenu.addAction("Open magnet link")
        fileMenu.addSeparator()
        fileMenu.addAction("Exit")
        self.addMenu(fileMenu)
        
        # edit menu
        editMenu = QMenu("&Edit", self)
        self.addMenu(editMenu)
        
        # settings menu
        settingsMenu = QMenu("&Settings", self)
        self.addMenu(settingsMenu)
        
        # help menu
        helpMenu = QMenu("&Help", self)
        self.addMenu(helpMenu)
    
    def pressed(self):
        print("pressed")