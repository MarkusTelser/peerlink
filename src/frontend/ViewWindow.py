import sys
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QAbstractScrollArea, QCheckBox, QComboBox, QFileDialog, QGridLayout, QGroupBox, QLabel, 
    QLineEdit, QMainWindow, QPushButton, QTreeView, QWidget, QApplication)
from PyQt6.QtGui import QGuiApplication, QIcon, QStandardItem, QStandardItemModel
from os.path import expanduser

from ..backend.metadata.TorrentParser import TorrentData
import os

class ViewWindow(QMainWindow):
    def __init__(self, parent=None):
        super(ViewWindow, self).__init__(parent)
        self.setWindowTitle("FastPeer - View Torrent")
        self.torrent_data = None

        # set minimum and standard window size
        #width, height = 1000, 800
        #min_width, min_height = 300, 300
        #self.resize(width, height)
        #self.setMinimumSize(QSize(min_width, min_height))
        

        # center in the middle of screen
        qtRectangle = self.frameGeometry()
        centerPoint = QGuiApplication.primaryScreen().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        # set icon to window
        icon = QIcon('resources/logo.png')
        self.setWindowIcon(icon)
        self.setWindowIconText("logo") 

        # give primary policy focus
        self.activateWindow()
        self.raise_()
        self.setFocus()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        self.addWidgets()

        self.setFixedSize(self.layout.sizeHint())
    
    def addWidgets(self):
        # set layout and create central widget
        widget = QWidget()
        self.layout = QGridLayout(widget)
        widget.setLayout(self.layout)

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

        # add info about torrent
        self.label1 = QLabel('Created by: ')
        self.label2 = QLabel('Creation date: ')
        self.label3 = QLabel('Comment: ')
        self.label4 = QLabel('Hash: ')
        vbox.addWidget(self.label1, 5, 0)
        vbox.addWidget(self.label2, 6, 0 )
        vbox.addWidget(self.label3, 7, 0)
        vbox.addWidget(self.label4, 8, 0)

        #groupbox.setMinimumWidth(100)
        groupbox.setMaximumWidth(self.width() / 2)
        self.layout.addWidget(groupbox, 0, 0, 1, 2)

        # add cancel and ok button for this window
        cancel = QPushButton("cancel", self)
        ok = QPushButton("ok", self)
        self.layout.addWidget(cancel, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)        
        self.layout.addWidget(ok, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        # add tree view of files struct
        self.tree_view = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['id', 'name', 'size'])

        """
        root = QStandardItem('1')
        root.setCheckable(True)
        root.setChild(0, QStandardItem('2'))
        root.setChild(1, QStandardItem('item2'))
        root.setChild(2, QStandardItem('item3'))
        model.appendRow(root)
        """
        
        self.tree_view.setModel(self.model)
        #tree_view.expand(root.index())

        self.layout.addWidget(self.tree_view, 0, 2, 1, 2)

        print("columns: ", self.layout.columnCount())
        print("rows: ", self.layout.rowCount())
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
    
    def gen_readable_size(bits) -> str:
        pass

    def show(self, torrent_data: TorrentData):
        self.label1.setText(self.label1.text() + torrent_data.created_by)
        self.label2.setText(self.label2.text() + torrent_data.creation_date)
        self.label3.setText(self.label3.text() + torrent_data.comment)
        self.label4.setText(self.label4.text() + torrent_data.info_hash_hex)

        root_file = list(torrent_data.files.keys())[0]
        root_node = QStandardItem(str(0))
        root_node.setEditable(False)
        root_node.setIcon(QIcon('resources/icon.png'))
        
        if torrent_data.files[root_file]:
            for i, item in enumerate(torrent_data.files[root_file]):
                id = QStandardItem(str(i+1))
                id.setCheckable(True)
                id.setEditable(False)
                id.setIcon(QIcon('resources/logo.png'))

                if "/" in item.name:
                    start_node = root_node
                    for folder in item.name.split("/"):
                        QStandardItem(folder)

                name = QStandardItem(item.name)
                name.setEditable(False)

                size = QStandardItem(str(item.length))
                size.setEditable(False)
                
                root_node.appendRow([id, name, size])
        
        self.model.appendRow([root_node, QStandardItem(root_file.name), QStandardItem(str(root_file.length))])
        self.tree_view.setModel(self.model)
        self.tree_view.expandAll()

        # resize to minimum text
        print(self.model.columnCount(root_node.index()))
        for i in range(self.model.columnCount(root_node.index())):
            self.tree_view.resizeColumnToContents(i)
        
        self.setWindowTitle(list(torrent_data.files.keys())[0].name)
        super().show()



        


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ViewWindow()
    window.show()

    app.exec()