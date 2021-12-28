
from os import error
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialogButtonBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QLabel, 
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QApplication,
    QErrorMessage
)
from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import QSize, Qt
from os.path import expanduser, join
from psutil import disk_usage
from os.path import exists, isdir
import sys

from src.backend.metadata.TorrentParser import TorrentData, TorrentParser
from src.frontend.views.TorrentTreeView import TorrentTreeView
from src.frontend.models.TorrentTreeModel import TorrentTreeModel

class ViewWindow(QMainWindow):
    add_data = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super(ViewWindow, self).__init__(parent)
        self.setWindowTitle("FastPeer - View Torrent")
        self.torrent_data = None

        # set minimum and standard window size
        width, height = 1000, 700
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

        self.addWidgets()
    
    def addWidgets(self):
        # set layout and create central widget
        widget = QWidget()
        self.main_layout = QGridLayout()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)
        
        hor_splitter = QSplitter()
        hor_splitter.setOrientation(Qt.Orientation.Horizontal)
        
        group_widget = QWidget()
        group_layout = QVBoxLayout()
        group_layout.setSpacing(20)
        group_widget.setLayout(group_layout)
        
        groupbox = QGroupBox("Path")
        vbox = QGridLayout()
        groupbox.setLayout(vbox)
        group_layout.addWidget(groupbox)
        vbox.setContentsMargins(10, 10, 0, 10)
        groupbox.setStyleSheet("QGroupBox { font-weight: bold; color: red;} ")

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
        
        option_box = QGroupBox("Options")
        option_layout = QGridLayout()
        option_box.setLayout(option_layout)
        group_layout.addWidget(option_box)
        option_box.setStyleSheet("QGroupBox { font-weight: bold; color: red;} ")
        
        # add combo box for download strategys
        strategy_label = QLabel('Download Strategy:')
        self.download_strategy = QComboBox()
        items = ['rarest first (default)', 'sequential', 'random']
        self.download_strategy.addItems(items)
        option_layout.addWidget(strategy_label, 2, 0)
        option_layout.addWidget(self.download_strategy, 2, 1)

        # add extra checkbox options
        self.start_box = QCheckBox("start immediately")
        self.checkhash_box = QCheckBox("check hashes")
        self.pad_box = QCheckBox("pre pad empty files")
        self.start_box.toggle()
        self.checkhash_box.toggle()
        option_layout.addWidget(self.start_box, 3, 0, 1, 0)
        option_layout.addWidget(self.checkhash_box, 4, 0, 1, 0)
        option_layout.addWidget(self.pad_box, 5, 0, 1, 0)

        # add info about torrent
        
        info_box = QGroupBox("Torrent Information")
        info_layout = QVBoxLayout()
        info_box.setLayout(info_layout)
        group_layout.addWidget(info_box)
        
        bold = lambda txt: f"<b>{txt}</b>"  
        info_box.setStyleSheet("QGroupBox { font-weight: bold; color: red;} ")
        self.label1 = QLabel(bold('Size: '))
        self.label2 = QLabel(bold('Creation date: '))
        self.label3 = QLabel(bold('Created by: '))
        self.label4 = QLabel(bold('Comment: '))
        self.label5 = QLabel(bold('Hash: '))
        self.label1.setWordWrap(True)
        self.label2.setWordWrap(True)
        self.label3.setWordWrap(True)
        self.label4.setWordWrap(True)
        info_layout.addWidget(self.label1)
        info_layout.addWidget(self.label2)
        info_layout.addWidget(self.label3)
        info_layout.addWidget(self.label4)
        info_layout.setContentsMargins(10, 10, 0, 10)
        info_layout.insertStretch(-1, 1)

        # checkbox don't show again
        self.not_again = QCheckBox("don't show again")
        group_layout.addWidget(self.not_again)
        
        # add cancel and ok button
        button_box = QDialogButtonBox()
        button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        #button_box.layout().setDirection(QBoxLayout.Direction.LeftToRight)
        button_box.layout().setAlignment(Qt.AlignmentFlag.AlignRight)
        self.main_layout.addWidget(button_box, 1, 0)
        
        # create tree view of file struct
        self.model = TorrentTreeModel()
        self.tree_view = TorrentTreeView(self.model)
        self.tree_view.setModel(self.model)
        
        # add groups and tree widgets
        hor_splitter.addWidget(group_widget)
        hor_splitter.setStretchFactor(0, 20)
        hor_splitter.setCollapsible(0, False)
        hor_splitter.addWidget(self.tree_view)
        hor_splitter.setStretchFactor(1, 80)
        hor_splitter.setCollapsible(1, False)
        self.main_layout.addWidget(hor_splitter, 0, 0)
        super().show()

    def show(self, torrent_data: TorrentData):
        free_space = lambda: self.convert_bits(disk_usage('/').free)
        torrent_size = lambda: self.convert_bits(torrent_data.files.length)
        self.label1.setText(self.label1.text() + f"{torrent_size()} (of {free_space()} on local disk)")
        self.label2.setText(self.label2.text() + torrent_data.creation_date)
        self.label3.setText(self.label3.text() + torrent_data.created_by)
        self.label4.setText(self.label4.text() + torrent_data.comment)
        self.label5.setText(self.label5.text() + torrent_data.info_hash_hex)
        
        self.model.update(torrent_data.files)
        super().show()
            
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
   
    
    """ the following methods are all slots """
    def pressedPathSelect(self):
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
            download_path = join(expanduser('~'), 'Downloads')
            self.download_path.setText(download_path)
            self.download_path.setDisabled(True)
            self.path_select.setDisabled(True)
        else:
            self.download_path.setText('')
            self.download_path.setEnabled(True)
            self.path_select.setEnabled(True)
    
    def accept(self):        
        # check if path is not empty, correct and a directory
        path = self.download_path.text().strip()
        if not path:
            error_msg = QMessageBox(self)
            error_msg.setWindowIcon(QIcon('resources/warning.svg'))
            error_msg.setWindowTitle("Error")
            error_msg.setText("download path is empty")
            error_msg.show()
            return
        if not exists(path):
            error_msg = QErrorMessage(self)
            error_msg.showMessage("download path does not exist")
            return
        if not isdir(path):
            error_msg = QErrorMessage(self)
            error_msg.showMessage("download path is not a directory")
            return
        
        # check which options are selected
        strategy = self.download_strategy.currentText().replace(' (default)', '')
        start = self.start_box.isChecked()
        check_hash = self.checkhash_box.isChecked()
        pad_files = self.pad_box.isChecked()
        
        # check if option dont show again enabled
        not_again = self.not_again.isChecked()
        
        # TODO if implemeted, check which files are checked and set in model data
        
        data = {
            'path': path,
            'strategy': strategy,
            'start': start,
            'check_hash' : check_hash,
            'pad_files' : pad_files,
            'not_again' : not_again,
            'files' : self.model.file_data
        }
        self.add_data.emit(data)
        
        self.close()
    
    def reject(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    path = "data/all/test.torrent"
    data = TorrentParser.parse_filepath(path)
    window = ViewWindow()
    window.show(data)

    app.exec()