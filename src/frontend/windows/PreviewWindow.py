
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
    QErrorMessage,
    QScrollArea,
    QSizePolicy
)
from PyQt6.QtGui import QGuiApplication, QIcon, QCloseEvent
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import QSize, Qt
from os.path import expanduser
from psutil import disk_usage
from os.path import exists, isdir
import sys

from src.backend.metadata.TorrentParser import TorrentData, TorrentParser
from src.frontend.utils.ConfigLoader import ConfigLoader
from src.frontend.views.TorrentTreeView import TorrentTreeView
from src.frontend.models.TorrentTreeModel import TorrentTreeModel
from src.frontend.utils.utils import convert_bits

class PreviewWindow(QMainWindow):
    add_data = pyqtSignal(dict)
    
    def __init__(self, conf: ConfigLoader, parent=None):
        super(PreviewWindow, self).__init__(parent=parent)
        self.setWindowTitle("FastPeer - View Torrent")
        self.torrent_data = None
        self.conf = conf

        # set minimum and standard window size
        min_width, min_height = 300, 300
        self.setMinimumSize(QSize(min_width, min_height))
        self.resize(self.conf.preview_size)

        # center in the middle of screen
        print(self.conf.preview_location)
        if not self.conf.preview_location.isNull():
            self.move(self.conf.preview_location)
        else:
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
        
        # add download path input
        self.download_path = QLineEdit()
        self.download_path.setText(self.conf.default_path)
        self.download_path.setPlaceholderText('Enter download path')
        vbox.addWidget(self.download_path, 0, 0)

        # add download path selector
        self.path_select = QPushButton("select folder")
        self.path_select.clicked.connect(self.pressedPathSelect)
        vbox.addWidget(self.path_select, 0, 1)

        self.default_path = QCheckBox("set as default path")
        vbox.addWidget(self.default_path, 1, 0, 1, 0)
        
        # add combo box for category
        category_box = QGroupBox("Category")
        category_layout = QVBoxLayout()
        category_box.setLayout(category_layout)
        group_layout.addWidget(category_box)
        self.category = QComboBox()
        self.category.setEditable(True)
        self.category.lineEdit().setPlaceholderText('Enter new/existing category')
        self.default_category = QCheckBox('set as default category')
        category_layout.addWidget(self.category)
        category_layout.addWidget(self.default_category)
        
        option_box = QGroupBox("Options")
        option_layout = QGridLayout()
        option_box.setLayout(option_layout)
        group_layout.addWidget(option_box)
        
        # add combo box for download strategys
        strategy_label = QLabel('Download Strategy:')
        self.download_strategy = QComboBox()
        items = ['rarest first (default)', 'sequential', 'random']
        self.download_strategy.addItems(items)
        option_layout.addWidget(strategy_label, 3, 0)
        option_layout.addWidget(self.download_strategy, 3, 1)

        # add extra checkbox options
        self.start_box = QCheckBox("start immediately")
        self.checkhash_box = QCheckBox("check hashes")
        self.pad_box = QCheckBox("pre pad empty files")
        self.start_box.setChecked(self.conf.auto_start)
        self.checkhash_box.setChecked(self.conf.check_hashes)
        self.pad_box.setChecked(self.conf.padd_files)
        option_layout.addWidget(self.start_box, 4, 0, 1, 0)
        option_layout.addWidget(self.checkhash_box, 5, 0, 1, 0)
        option_layout.addWidget(self.pad_box, 6, 0, 1, 0)

        # add info about torrent
        info_box = QGroupBox("Torrent Information")
        info_layout = QGridLayout()
        info_box.setLayout(info_layout)
        info_box.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        bold = lambda txt: f"<b>{txt}</b>"  
        self.label1 = QLabel(bold('Size: '))
        self.label2 = QLabel(bold('Creation date: '))
        self.label3 = QLabel(bold('Created by: '))
        self.label4 = QLabel(bold('Comment: '))
        self.label5 = QLabel(bold('Hash: '))
        self.label1.setWordWrap(True)
        self.label2.setWordWrap(True)
        self.label3.setWordWrap(True)
        self.label4.setWordWrap(True)
        info_layout.addWidget(self.label1, 0, 0)
        info_layout.addWidget(self.label2, 1, 0)
        info_layout.addWidget(self.label3, 2, 0)
        info_layout.addWidget(self.label4, 3, 0)
        info_layout.setContentsMargins(10, 10, 0, 10)
        #info_layout.insertStretch(-1, 1)
        
        group_layout.addWidget(info_box)
        
        # checkbox don't show again
        self.not_again = QCheckBox("don't show again")
        group_layout.addStretch()
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
        self.torrent_data = torrent_data
        free_space = lambda: convert_bits(disk_usage('/').free)
        torrent_size = lambda: convert_bits(torrent_data.files.length)
        self.label1.setText(self.label1.text() + f"{torrent_size()} (of {free_space()} on local disk)")
        self.label2.setText(self.label2.text() + torrent_data.creation_date)
        self.label3.setText(self.label3.text() + torrent_data.created_by)
        self.label4.setText(self.label4.text() + torrent_data.comment)
        self.label5.setText(self.label5.text() + torrent_data.info_hash_hex)
        
        self.setWindowTitle(torrent_data.files.name)
        self.model.update(torrent_data.files)
        super().show()
   
    
    """ the following methods are all slots """
    def pressedPathSelect(self):
        file_dialog = QFileDialog(self, 'Select Directory')
        file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog)
        file_dialog.setOption(QFileDialog.Option.DontUseCustomDirectoryIcons)
        file_dialog.setOption(QFileDialog.Option.ShowDirsOnly)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        file_dialog.setDirectory(expanduser('~'))

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.download_path.setText(file_path)
    
    def accept(self):        
        # check if path is not empty, correct and a directory
        default_path = self.default_path.isChecked()
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
        
        category = self.category.currentText()
        default_category = self.default_category.isChecked()
        
        # check which options are selected
        strategy = self.download_strategy.currentText().replace(' (default)', '')
        start = self.start_box.isChecked()
        check_hash = self.checkhash_box.isChecked()
        pad_files = self.pad_box.isChecked()
        not_again = not self.not_again.isChecked()
        
        # TODO if implemeted, check which files are checked and set in model data
        
        data = {
            'size': self.size(),
            'location': self.pos(),
            'path': path,
            'default_path': default_path,
            'category': category,
            'default_category': default_category,
            'strategy': strategy,
            'start': start,
            'check_hash' : check_hash,
            'pad_files' : pad_files,
            'not_again' : not_again,
            'data' : self.torrent_data
        }
        self.close()
        self.add_data.emit(data)
    
    def reject(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    path = "data/all/test.torrent"
    data = TorrentParser.parse_filepath(path)
    
    conf = ConfigLoader()
    
    window = PreviewWindow(conf)
    window.show(data)

    app.exec()