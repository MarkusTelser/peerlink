from PyQt6.QtCore import QStandardPaths, QSettings

class ConfigLoader():
    def __init__(self): 
        settings = QSettings()

        settings.beginGroup('General')
        settings.setValue('default_path', 'penis')
        settings.endGroup()
        
    def loadSettings(self):
        pass
    
    def saveSettings(self):
        pass