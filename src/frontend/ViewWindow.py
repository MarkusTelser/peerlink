import sys
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QAbstractScrollArea, QCheckBox, QComboBox, QFileDialog, QGridLayout, QGroupBox, QLabel, 
    QLineEdit, QMainWindow, QPushButton, QSizePolicy, QTreeView, QWidget, QApplication)
from PyQt6.QtGui import QGuiApplication, QIcon, QStandardItem, QStandardItemModel
from os.path import expanduser

from ..backend.metadata.TorrentParser import TorrentData

class ViewWindow(QMainWindow):
    def __init__(self, parent=None):
        super(ViewWindow, self).__init__(parent)
        self.setWindowTitle("FastPeer - View Torrent")
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
        icon = QIcon('resources/logo.png')
        self.setWindowIcon(icon)
        self.setWindowIconText("logo") 

        # give primary policy focus
        #self.activateWindow()
        #self.raise_()
        #self.setFocus()
        #self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        #self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

        self.addWidgets()
    
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
        self.path_select = QPushButton("select folder")
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
        self.label3 = QLabel('Hash: ')
        self.label4 = QLabel('Comment: ')
        vbox.addWidget(self.label1, 5, 0, 1, 2)
        vbox.addWidget(self.label2, 6, 0, 1, 2)
        vbox.addWidget(self.label3, 7, 0, 1, 2)
        vbox.addWidget(self.label4, 8, 0, 1, 2)

        #groupbox.setMinimumWidth(100)
        #groupbox.setMaximumWidth(self.width() / 2)
        self.layout.addWidget(groupbox, 0, 0, 1, 2)

        # checkbox don't show again
        not_again = QCheckBox("don't show again")
        self.layout.addWidget(not_again, 1, 0, 1, 2)
        
        # add cancel and ok button for this window
        cancel = QPushButton("cancel", self)
        ok = QPushButton("ok", self)
        self.layout.addWidget(cancel, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)        
        self.layout.addWidget(ok, 1, 3, alignment=Qt.AlignmentFlag.AlignCenter)

        # add tree view of files struct
        self.tree_view = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['name', 'size'])
        
        self.tree_view.setModel(self.model)
        self.layout.addWidget(self.tree_view, 0, 2, 1, 2)

        self.setCentralWidget(widget)
    
    def pressedPathSelect(self, event):
        file_dialog = QFileDialog(self, 'Select Directory')
        file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog)
        file_dialog.setOption(QFileDialog.Option.DontUseCustomDirectoryIcons)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        file_dialog.setDirectory(expanduser('~'))

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.download_path.setText(file_path)
        
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
        self.label3.setText(self.label3.text() + torrent_data.info_hash_hex)
        self.label4.setText(self.label4.text() + torrent_data.comment)

        root_file = torrent_data.files
        
        root_name = QStandardItem(root_file.name)
        file_size = self.convert_bits(root_file.length)
        root_size = QStandardItem(file_size)
        
        self.iterate_tree(root_file, root_name)
        
        root_node = self.model.invisibleRootItem()
        root_node.appendRow([root_name, root_size])
        
        self.tree_view.setModel(self.model)
        self.tree_view.expandAll()

        # resize to minimum text
        print(self.model.columnCount(root_name.index()))
        for i in range(self.model.columnCount(root_name.index())):
            self.tree_view.resizeColumnToContents(i)
        
        self.setWindowTitle(torrent_data.files.name)
        super().show()
        
    def iterate_tree(self, root_file, root_node):
        # set folder and file icons
        if root_file.children:
            root_node.setIcon(QIcon('resources/folder.svg'))
        #else:
        #    root_node.setIcon(QIcon('resources/add.svg'))
        
        for child in root_file.children:
            name = QStandardItem(child.name)
            name.setEditable(False)

            size = self.convert_bits(child.length)
            size = QStandardItem(size)
            size.setEditable(False)
                    
            self.iterate_tree(child, name)   
            
            root_node.appendRow([name, size])
                
    def convert_bits(self, bits: int):
        if bits < 1000:
            return f"{bits} B"
        if bits / 1024 < 1000:
            return f"{int(round(bits / 1024, 0))} KiB"
        elif bits / (1024 ** 2) < 1000:
            return f"{round(bits / (1024 ** 2), 1)} MiB"
        elif bits  / (1024 ** 3) < 1000:
            return f"{round(bits / (1024 ** 3), 2)} GiB"
        elif bits / (1024 ** 4) < 1000: 
            return f"{round(bits / (1024 ** 4), 2)} TiB"
        elif bits / (1024 ** 5) < 1000:
            return f"{round(bits / (1024 ** 5), 3)} PiB"


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ViewWindow()
    window.show()

    app.exec()