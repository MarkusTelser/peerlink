import sys
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QFileDialog, QGridLayout, QGroupBox, QLabel, 
    QLineEdit, QMainWindow, QPushButton, QTreeView, QWidget, QApplication)
from PyQt6.QtGui import QGuiApplication, QIcon, QStandardItem, QStandardItemModel
from os.path import expanduser

from src.Torrent import TorrentData

class LoadWindow(QMainWindow):
    def __init__(self, parent=None):
        super(LoadWindow, self).__init__(parent)
        self.setWindowTitle("FastPeer - LoadPage")
        self.torrent_data = None

        # set minimum and standard window size
        width, height = 1000, 800
        min_width, min_height = 300, 300
        self.resize(width, height)
        self.setMinimumSize(QSize(min_width, min_height))

        # center in the middle of screen
        qtRectangle = self.frameGeometry()
        centerPoint = QGuiApplication.primaryScreen().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        # set icon to window
        icon = QIcon('logo.png')
        self.setWindowIcon(icon)
        self.setWindowIconText("logo") 

        # give primary policy focus
        self.activateWindow()
        self.raise_()
        self.setFocus()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        self.addWidgets()
    
    def addWidgets(self):
        # set layout and create central widget
        widget = QWidget()
        layout = QGridLayout(widget)
        widget.setLayout(layout)

        groupbox = QGroupBox("options:")
        
        vbox = QGridLayout()
        groupbox.setLayout(vbox)

        # add download path input
        self.download_path = QLineEdit()
        self.download_path.setPlaceholderText('Enter download path')
        vbox.addWidget(self.download_path, 0, 0)

        # add download path selector
        self.path_select = QPushButton("select file")
        self.path_select.clicked.connect(self.pressedPathSelect)
        vbox.addWidget(self.path_select, 0, 1)

        default_path = QCheckBox("use default path")
        default_path.stateChanged.connect(self.pressedDefaultPath)
        vbox.addWidget(default_path, 1, 0, 1, 0)

        # add combo box for download strategys
        strategy_label = QLabel('Download Strategy:')
        download_strategy = QComboBox()
        items = ['rarest-first (default)', 'sequential', 'random']
        download_strategy.addItems(items)
        vbox.addWidget(strategy_label, 2, 0)
        vbox.addWidget(download_strategy, 2, 1)

        # add extra checkbox options
        start = QCheckBox("start immediately")
        sequential = QCheckBox("check hashes")
        start.toggle()
        sequential.toggle()
        vbox.addWidget(start, 3, 0, 1, 0)
        vbox.addWidget(sequential, 4, 0, 1, 0)

        layout.addWidget(groupbox, 0, 0)

        # add cancel and ok button for this window
        cancel = QPushButton("cancel", self)
        ok = QPushButton("ok", self)
        layout.addWidget(cancel, 3, 3)        
        layout.addWidget(ok, 3, 4)

        tree_view = QTreeView()
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['id', 'name', 'size'])

        root = QStandardItem('1')
        root.setCheckable(True)
        root.appendRow([QStandardItem('2'), QStandardItem('item2'), QStandardItem('item3')])
        model.appendRow([root, QStandardItem('root'), QStandardItem('100')])
        
        tree_view.expand(root.index())
        tree_view.expandRecursively(root.index(), 10)
        print(model.columnCount(), model.rowCount())
        tree_view.setModel(model)

        layout.addWidget(tree_view, 0, 2, 2, 3)

        self.setCentralWidget(widget)
    
    def pressedPathSelect(self, event):
        file_dialog = QFileDialog(self, 'Open Torrent File')
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Torrent files (*.torrent)")
        file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog)
        file_dialog.setOption(QFileDialog.Option.DontUseCustomDirectoryIcons)
        file_dialog.setMimeTypeFilters(['application/x-bittorrent'])
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        file_dialog.setDirectory(expanduser('~'))

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            print(file_path)
        
    def pressedDefaultPath(self):
        if self.sender().isChecked():
            self.download_path.setText('/home/user/path')
            self.download_path.setDisabled(True)
            self.path_select.setDisabled(True)
        else:
            self.download_path.setText('')
            self.download_path.setEnabled(True)
            self.path_select.setEnabled(True)

    def show(self, torrent_data: TorrentData):
        self.download_path.setText(torrent_data.creation_date)



        


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = LoadWindow()
    window.show()

    app.exec()