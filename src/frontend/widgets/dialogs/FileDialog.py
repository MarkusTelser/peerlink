from PyQt6.QtCore import QFile
from PyQt6.QtWidgets import QFileDialog
from os.path import expanduser

class FileDialog(QFileDialog):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('Open Torrent File')
        self.setBaseSize(1000, 700)
        self.setMinimumSize(400, 400)
        self.setFileMode(QFileDialog.FileMode.ExistingFiles)
        self.setNameFilter("Torrent files (*.torrent)")
        self.setOption(QFileDialog.Option.DontUseNativeDialog, False)
        self.setOption(QFileDialog.Option.DontUseCustomDirectoryIcons)
        self.setMimeTypeFilters(['application/x-bittorrent'])
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        self.setDirectory(expanduser('~'))