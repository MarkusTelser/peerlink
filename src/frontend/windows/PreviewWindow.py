from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialogButtonBox,
    QGridLayout,
    QGroupBox,
    QLabel, 
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QApplication,
    QSizePolicy,
    QProgressBar
)
from PyQt6.QtGui import QGuiApplication, QIcon, QCloseEvent
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QTimer, QSize, Qt
from psutil import disk_usage
from os.path import exists, isdir
import sys

from src.backend.metadata.TorrentParser import TorrentData, TorrentParser
from src.backend import Swarm
from src.backend.metadata.MagnetLink import MagnetLink
from src.frontend.widgets.dialogs.FileDialog import FolderDialog
from src.frontend.utils.ConfigLoader import ConfigLoader
from src.frontend.views.FileTreeView import FileTreeView
from src.frontend.models.FileTreeModel import FileTreeModel
from src.frontend.utils.utils import convert_bits, showError


class PreviewWindow(QMainWindow):
    add_data = pyqtSignal(TorrentData, dict)
    UPDATE_DELAY = 500
    
    def __init__(self, conf: ConfigLoader, parent):
        super(PreviewWindow, self).__init__(parent=parent)
        
        self.conf = conf
        self.session = None
        self.torrent_data = None
        self._close_state = None

        self.setAutoFillBackground(True)
        self.setObjectName("PreviewWindow")
        self.setWindowTitle(self.tr("View Torrent - PeerLink"))
        self.setWindowIcon(QIcon("resources/icons/logo.svg"))
        
        # set minimum and standard window size
        min_width, min_height = 300, 300
        self.setMinimumSize(QSize(min_width, min_height))
        self.resize(self.conf.preview_size)

        # center in the middle of screen
        if not self.conf.preview_location.isNull():
            self.move(self.conf.preview_location)
        else:
            qtRectangle = self.frameGeometry()
            qtRectangle.moveCenter(parent.frameGeometry().center())
            self.move(qtRectangle.topLeft())

        self.addWidgets()

        self.update_task = QTimer(self)
        self.update_task.timeout.connect(self._update)
        self.update_task.start(self.UPDATE_DELAY)
    
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
        
        groupbox = QGroupBox(self.tr("Path"))
        vbox = QGridLayout()
        groupbox.setLayout(vbox)
        group_layout.addWidget(groupbox)
        vbox.setContentsMargins(10, 10, 0, 10)
        
        # add download path input
        self.download_path = QLineEdit()
        self.download_path.setText(self.conf.default_path)
        self.download_path.setPlaceholderText(self.tr("Enter download path"))
        vbox.addWidget(self.download_path, 0, 0)

        # add download path selector
        self.path_select = QPushButton(self.tr("select folder"))
        self.path_select.clicked.connect(self.pressedPathSelect)
        vbox.addWidget(self.path_select, 0, 1)

        self.default_path = QCheckBox(self.tr("set as default path"))
        vbox.addWidget(self.default_path, 1, 0, 1, 0)
        
        # add combo box for category
        category_box = QGroupBox(self.tr("Category"))
        category_layout = QVBoxLayout()
        category_box.setLayout(category_layout)
        group_layout.addWidget(category_box)
        
        self.category = QComboBox()
        self.category.setEditable(True)
        self.category.setAutoFillBackground(True)
        self.category.addItems(self.conf.categorys)
        self.category.setEditText(self.conf.default_category)
        self.category.lineEdit().setPlaceholderText(self.tr("Enter new/existing category"))
        self.default_category = QCheckBox(self.tr("set as default category"))
        
        category_layout.addWidget(self.category)
        category_layout.addWidget(self.default_category)
        
        option_box = QGroupBox(self.tr("Options"))
        option_layout = QGridLayout()
        option_box.setLayout(option_layout)
        group_layout.addWidget(option_box)
        
        # add combo box for download strategys
        strategy_label = QLabel(self.tr("Download Strategy:"))
        self.download_strategy = QComboBox()
        self.download_strategy.setAutoFillBackground(True)
        strategys = [self.tr('rarest first (default)'), self.tr('sequential'), self.tr('random')]
        self.download_strategy.addItems(strategys)
        self.download_strategy.setCurrentIndex(self.conf.strategy)
        option_layout.addWidget(strategy_label, 3, 0)
        option_layout.addWidget(self.download_strategy, 3, 1)

        # add extra checkbox options
        self.start_box = QCheckBox(self.tr("start immediately"))
        self.checkhash_box = QCheckBox(self.tr("check hashes"))
        self.pad_box = QCheckBox(self.tr("pre pad empty files"))
        self.start_box.setChecked(self.conf.auto_start)
        self.checkhash_box.setChecked(self.conf.check_hashes)
        self.pad_box.setChecked(self.conf.padd_files)
        option_layout.addWidget(self.start_box, 4, 0, 1, 0)
        option_layout.addWidget(self.checkhash_box, 5, 0, 1, 0)
        option_layout.addWidget(self.pad_box, 6, 0, 1, 0)

        # add info about torrent
        info_box = QGroupBox(self.tr("Torrent Information"))
        info_layout = QGridLayout()
        info_box.setLayout(info_layout)
        info_box.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        italic = lambda txt: f"<em>{txt}</em>"  
        self.label1 = QLabel(italic(self.tr("Size:")))
        self.label2 = QLabel(italic(self.tr("Creation date:")))
        self.label3 = QLabel(italic(self.tr("Created by:")))
        self.label4 = QLabel(italic(self.tr("Comment:")))
        self.label5 = QLabel(italic(self.tr("Hash:")))
        self.label1.setWordWrap(True)
        self.label2.setWordWrap(True)
        self.label3.setWordWrap(True)
        self.label4.setWordWrap(True)
        info_layout.addWidget(self.label1, 0, 0)
        info_layout.addWidget(self.label2, 1, 0)
        info_layout.addWidget(self.label3, 2, 0)
        info_layout.addWidget(self.label4, 3, 0)
        info_layout.setContentsMargins(10, 10, 0, 10)
        
        group_layout.addWidget(info_box)
        
        # checkbox don't show again
        self.not_again = QCheckBox(self.tr("don't show again"))
        group_layout.addStretch()
        group_layout.addWidget(self.not_again)
       
        
        # add cancel and ok button
        self.button_box = QDialogButtonBox()
        self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        self.button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.layout().setAlignment(Qt.AlignmentFlag.AlignRight)
        self.main_layout.addWidget(self.button_box, 1, 1)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedSize(250, 25)
        self.progress_bar.setRange(0, 100)
        self.main_layout.addWidget(self.progress_bar, 1, 0)

        # create tree view of file struct
        self.model = FileTreeModel()
        self.tree_view = FileTreeView(self.model)
        self.tree_view.setModel(self.model)
        
        # add groups and tree widgets
        hor_splitter.addWidget(group_widget)
        hor_splitter.setStretchFactor(0, 20)
        hor_splitter.setCollapsible(0, False)
        hor_splitter.addWidget(self.tree_view)
        hor_splitter.setStretchFactor(1, 80)
        hor_splitter.setCollapsible(1, False)
        self.main_layout.addWidget(hor_splitter, 0, 0, 1, 2)
    
    def showTorrent(self, torrent_data):
        self.torrent_data = torrent_data
        italic = lambda txt: f"<em>{txt}</em>"  
        free_space = lambda: convert_bits(disk_usage("/").free)
        torrent_size = lambda: convert_bits(torrent_data.files.length)
        
        self.label1.setText(self._size_text(torrent_size(), free_space()))
        self.label2.setText(f"{self.label2.text()} {torrent_data.creation_date}")
        self.label3.setText(f"{self.label3.text()} {torrent_data.created_by}")
        self.label4.setText(f"{self.label4.text()} {torrent_data.comment}")
        self.label5.setText(f"{self.label5.text()} {torrent_data.info_hash_hex}")
        
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
        self.setWindowTitle(torrent_data.files.name)
        self.model.update(torrent_data.files)
        self.progress_bar.hide()

        super().show()

    def showMagnet(self, magnet_link, session):
        self.session = session
        self.index = self.session.add(Swarm())
        self.session.download_meta(self.index, magnet_link)

        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setDisabled(True)
        self.setWindowTitle(magnet_link.name or self.tr("View Torrent - PeerLink"))

        super().show()
        
    
    @pyqtSlot()
    def pressedPathSelect(self):
        file_dialog = FolderDialog(self)

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.download_path.setText(file_path)
    

    @pyqtSlot()    
    def accept(self):        
        # check if path is not empty, correct and a directory
        default_path = self.default_path.isChecked()
        path = self.download_path.text().strip()
        if not path:
            showError(self.tr("Save path is empty!"), self)
            return
        if not exists(path):
            showError(self.tr("Save path does not exist!"), self)
            return
        if not isdir(path):
            showError(self.tr("Save path is not a directory!"), self)
            return
        
        category = self.category.currentText()
        default_category = self.default_category.isChecked()
        
        # check which options are selected
        strategy = self.download_strategy.currentIndex()
        start = self.start_box.isChecked()
        check_hash = self.checkhash_box.isChecked()
        pad_files = self.pad_box.isChecked()
        not_again = not self.not_again.isChecked()
        
        # TODO if implemeted, check which files are checked and set in model data
        
        extras = {
            'start': start,
            'path': path,
            'category': category,
            'strategy': strategy,
            'check_hash' : check_hash,
            'pad_files' : pad_files,
        
            'size': self.size(),
            'location': self.pos(),
            'default_path': default_path,
            'default_category': default_category,
            'not_again' : not_again
        }
        
        self._close_state = True
        self.close()
        self.add_data.emit(self.torrent_data, extras)        
    

    @pyqtSlot()
    def reject(self):
        self._close_state = False
        self.close()

    
    @pyqtSlot(QCloseEvent)
    def closeEvent(self, event):
        if not self._close_state and self.session:
            self.session.remove(self.index)
        self.update_task.stop()
        super().closeEvent(event)

    def _size_text(self, torrent_size, size_disc):
        return f"<em>{self.tr('Size:')}</em> {torrent_size} ({self.tr('of {} on local disk').format(size_disc)})"

    def _update(self):
        if self.torrent_data:
            # refresh free space on local disk
            italic = lambda txt: f"<em>{txt}</em>"  
            free_space = lambda: convert_bits(disk_usage("/").free)
            torrent_size = lambda: convert_bits(self.torrent_data.files.length)
            self.label1.setText(self._size_text(torrent_size(), free_space()))
            return 

        if self.session._swarm_list[self.index].metadata_manager:
            value = self.session._swarm_list[self.index].metadata_manager.downloaded
            self.progress_bar.setValue(value)
        else:
            torrent = self.session._swarm_list[self.index].data
            self.showTorrent(torrent)
