from PyQt6.QtCore import QSettings, QSize, QPoint

class ConfigLoader():
    def __init__(self): 
        self.settings = QSettings()
        
        self.win_size = self.settings.value('win_size', QSize(900, 700), QSize)
        self.win_loc = self.settings.value('win_loc', None, QPoint)
        self.show_toolbar = self.settings.value('show_toolbar', True, bool)
        self.show_statusbar = self.settings.value('show_statusbar', True, bool)
        self.hori_splitter = [int(x) for x in self.settings.value('hori_splitter', [30, 70], list)]
        self.vert_splitter = [int(x) for x in self.settings.value('vert_splitter', [1, 0], list)]
        
        self.side_tabs = self.settings.value('side_tabs', [], list)
        self.detail_tabs = self.settings.value('detail_tabs', [], list)
        
        
    def loadSettings(self):
        pass
    
    def saveSettings(self):
        pass