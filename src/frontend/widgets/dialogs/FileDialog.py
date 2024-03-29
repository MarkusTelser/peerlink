from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFileDialog
from os.path import expanduser


class FileDialog(QFileDialog):
    def __init__(self, parent):
        super(FileDialog, self).__init__(parent=parent)

        self.setBaseSize(1000, 700)
        self.setMinimumSize(400, 400)
        self.setWindowIcon(QIcon("resources/icons/logo.svg"))
        self.setWindowTitle(self.tr("Open Torrent File - PeerLink"))
        
        # center in the middle of screen
        qtRectangle = self.frameGeometry()
        qtRectangle.moveCenter(parent.frameGeometry().center())
        self.move(qtRectangle.topLeft())
        
        self.setFileMode(QFileDialog.FileMode.ExistingFiles)
        self.setNameFilter(self.tr("Torrent files (*.torrent)"))
        self.setOption(QFileDialog.Option.DontUseNativeDialog, False)
        self.setOption(QFileDialog.Option.DontUseCustomDirectoryIcons)
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        self.setDirectory(expanduser("~"))


class FolderDialog(QFileDialog):
    def __init__(self, parent):
        super(FolderDialog, self).__init__(parent=parent)

        self.setBaseSize(1000, 700)
        self.setMinimumSize(400, 400)
        self.setWindowIcon(QIcon("resources/icons/logo.svg"))
        self.setWindowTitle(self.tr("Select Directory - PeerLink"))
        
        # center in the middle of screen
        qtRectangle = self.frameGeometry()
        qtRectangle.moveCenter(parent.frameGeometry().center())
        self.move(qtRectangle.topLeft())
        
        self.setFileMode(QFileDialog.FileMode.Directory)
        self.setOption(QFileDialog.Option.DontUseNativeDialog)
        self.setOption(QFileDialog.Option.DontUseCustomDirectoryIcons)
        self.setOption(QFileDialog.Option.ShowDirsOnly)
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        self.setDirectory(expanduser("~"))