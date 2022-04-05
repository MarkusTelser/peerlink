from PyQt6.QtWidgets import (
    QMainWindow, 
    QPushButton, 
    QWidget, 
    QVBoxLayout, 
    QLabel, 
    QCheckBox,
    QStackedLayout,
    QApplication
)
from PyQt6.QtGui import (
    QDragLeaveEvent, 
    QDropEvent, 
    QFont, 
    QGuiApplication, 
    QIcon, 
    QPixmap, 
    QDragEnterEvent,
    QCloseEvent,
    QKeySequence,
    QKeyEvent
)
from PyQt6.QtCore import QSize, Qt, pyqtSlot

from src.backend.metadata import TorrentParser, MagnetParser, TorrentData
from src.backend.Session import Session
from src.frontend.utils.ConfigLoader import ConfigLoader
from src.frontend.windows.ApplicationWindow import ApplicationWindow
from src.frontend.windows.PreviewWindow import PreviewWindow
from src.frontend.widgets.dialogs import FileDialog, MagnetLinkDialog

class LaunchWindow(QMainWindow):
    def __init__(self, conf: ConfigLoader):
        super().__init__()
        
        self.conf = conf
        self.session = Session()
        self.main_window = None
        
        self.setAcceptDrops(True)
        self.setObjectName("LaunchWindow")
        self.setWindowTitle("Launch Window - PeerLink")
        self.setWindowIcon(QIcon('resources/logo.svg'))
        
        # set screen size
        width, height = 700, 600
        min_width, min_height = 750, 550
        self.resize(width, height)
        self.setMinimumSize(QSize(min_width, min_height))
        
        # center in the middle of screen
        qtRectangle = self.frameGeometry()
        centerPoint = QGuiApplication.primaryScreen().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        
        self.addWidgets()


    def addWidgets(self):
        default_font = QFont('Arial', 18)
        small_font = QFont('Arial', 12)

        self.stacked_layout = QStackedLayout()
        stacked_widget = QWidget()
        stacked_widget.setLayout(self.stacked_layout)
        self.setCentralWidget(stacked_widget)
        
        # add main widget&layout onto stacked widget
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_widget.setLayout(self.main_layout)
       
        self.main_layout.addStretch(1)
        
        # add image of logo
        wrapper_label = QLabel()
        wrapper_label.setScaledContents(True)
        pixmap = QPixmap('resources/logo.svg')
        wrapper_label.setPixmap(pixmap)
        self.main_layout.addWidget(wrapper_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addSpacing(25)
        
        # add open torrent file dialog button
        open_file = QPushButton(" open &torrent file", self)
        open_file.clicked.connect(self.open_filedialog)
        open_file.setFixedSize(260, 40)
        add_icon = QIcon('resources/file.svg')
        open_file.setIcon(add_icon)
        open_file.setIconSize(QSize(26, 26))
        open_file.setFont(default_font)
        self.main_layout.addWidget(open_file, alignment=Qt.AlignmentFlag.AlignCenter)         

        # add open magnet link dialog button
        open_link = QPushButton(" add &magnet link")
        open_link.clicked.connect(self.open_magnetlink)
        open_link.setFixedSize(270, 40)
        add_icon = QIcon('resources/link.svg')
        open_link.setIcon(add_icon)
        open_link.setIconSize(QSize(26, 26))
        open_link.setFont(default_font)
        self.main_layout.addWidget(open_link, alignment=Qt.AlignmentFlag.AlignCenter)

        # other ways of dropping/adding torrent
        support = QLabel("+ drag and drop support")
        support.setObjectName("LaunchWindowDark")
        support.setFont(default_font)
        support.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(support)
        
        self.main_layout.addStretch(1)
        
        # dont show again checkbox
        self.show_again = QCheckBox("don't show again")
        self.show_again.setObjectName("LaunchWindowDark")
        self.show_again.setFont(small_font)
        self.main_layout.addWidget(self.show_again, 1, Qt.AlignmentFlag.AlignLeft  | Qt.AlignmentFlag.AlignBottom)
        self.stacked_layout.insertWidget(0, self.main_widget)
        
        # add drag&drop widget/layout onto stackedlayout
        dragdrop_widget = QWidget()
        dragdrop_layout = QVBoxLayout()
        dragdrop_widget.setLayout(dragdrop_layout)
        
        self.drop_label = QLabel(self)
        self.drop_label.setObjectName("DropLabel")
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setText("Drag and Drop\nfiles here")
        self.drop_label.setFont(default_font)
        dragdrop_layout.addWidget(self.drop_label)
        self.stacked_layout.insertWidget(1, dragdrop_widget)
        
        QApplication.clipboard().dataChanged.connect(lambda: print('here'))


    def open_filedialog(self):
        file_dialog = FileDialog()
        if file_dialog.exec():
            for file_path in file_dialog.selectedFiles():
                data = TorrentParser.parse_filepath(file_path)
                if self.conf.open_preview:
                    window = PreviewWindow(self.conf, self)
                    window.add_data.connect(self.open_mainwindow)
                    window.showTorrent(data)
                else:
                    self.open_mainwindow(data)
    

    def open_magnetlink(self):
        magnet_dialog = MagnetLinkDialog()
        
        if magnet_dialog.exec():
            magnet_link = magnet_dialog.text_box.text()
            magnet = MagnetParser.parse(magnet_link)
           
            if self.conf.open_preview:
                window = PreviewWindow(self.conf, self)
                window.add_data.connect(lambda *args: self.open_mainwindow(*args, magnet=True))
                window.showMagnet(magnet, self.session)
            else:
                pass # TODO implement silent download for magnet links

    def open_mainwindow(self, data, extras={}, magnet=False):
        if self.main_window == None:
            self.main_window = ApplicationWindow(self.conf, self.session)
            self.main_window.appendTorrent(data, extras, from_magnet=magnet)
            self.main_window.show()
            self.close()
        else:
            self.main_window.appendTorrent(data, extras, from_magnet=magnet)
    

    @pyqtSlot(QKeyEvent)
    def keyPressEvent(self, event: QKeyEvent):
        if event.matches(QKeySequence.StandardKey.Paste):
            try:
                magnet_link = QApplication.clipboard().text()
                magnet = MagnetParser.parse(magnet_link)
                window = PreviewWindow(self.conf, self)
                window.add_data.connect(lambda *args: self.open_mainwindow(*args, magnet=True))
                window.showMagnet(magnet, self.session)
            except Exception as e:
                pass
        super(LaunchWindow, self).keyPressEvent(event)


    @pyqtSlot(QDropEvent)
    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            if url.isLocalFile() and url.path().endswith('.torrent'):
                if self.conf.open_preview:
                    window = PreviewWindow(self.conf, self)
                    window.add_data.connect(self.open_mainwindow)
                    data = TorrentParser.parse_filepath(url.path())
                    window.showTorrent(data)
                else:
                    self.open_mainwindow(data)
        self.stacked_layout.setCurrentIndex(0)
    

    @pyqtSlot(QDragEnterEvent)
    def dragEnterEvent(self, event: QDragEnterEvent):
        right_format = False
        for url in event.mimeData().urls():
            if url.isLocalFile() and url.path().endswith('.torrent'):
                right_format = True
                break

        if not right_format:
            self.drop_label.setText('Wrong file format')
        
        self.stacked_layout.setCurrentIndex(1)
        event.accept()
    

    @pyqtSlot(QDragLeaveEvent)
    def dragLeaveEvent(self, event: QDragLeaveEvent):
        self.stacked_layout.setCurrentIndex(0)
        event.accept()
    

    @pyqtSlot(QCloseEvent)
    def closeEvent(self, event: QCloseEvent):
        self.conf.settings.setValue('show_launch', not self.show_again.isChecked())
        event.accept()