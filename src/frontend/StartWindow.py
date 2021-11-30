from PyQt6.QtWidgets import (
    QApplication, 
    QLineEdit, 
    QMainWindow, 
    QPushButton, 
    QWidget, 
    QVBoxLayout, 
    QLabel, 
    QFileDialog, 
    QMessageBox, 
    QDialog, 
    QDialogButtonBox, 
    QBoxLayout
)
from PyQt6.QtGui import (
    QDragLeaveEvent, 
    QDropEvent, 
    QFont, 
    QGuiApplication, 
    QIcon, 
    QPixmap, 
    QDragEnterEvent
)
from PyQt6.QtCore import QSize, Qt
from src.backend.metadata import TorrentParser
from .ViewWindow import ViewWindow
from os.path import expanduser
import sys


class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("FastPeer - Start Page")
        self.setObjectName("StartWindow")
        self.setAcceptDrops(True)

        # set screen size
        width, height = 900, 700
        min_width, min_height = 750, 550
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

        # set background gradient
        self.setStyleSheet("""QMainWindow#StartWindow{
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(255, 0, 0, 255), stop:1 rgba(0, 42, 255, 255));
        }""")

        self.addWidgets()

    def addWidgets(self):
        title_font = QFont('Arial', 50)
        default_font = QFont('Arial', 18)
        small_font = QFont('Arial', 12)

         # set layout and create central widget
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 50, 0, 30) #left, top, right, bottom
        self.central_widget.setLayout(self.layout)      
        self.setCentralWidget(self.central_widget)

        # add title of window
        title = QLabel("BitTorrent Client")
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(title)
        
        # add image of logo
        wrapper_label = QLabel()
        pixmap = QPixmap('resources/logo.png')
        pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        wrapper_label.setPixmap(pixmap)
        self.layout.addWidget(wrapper_label, alignment=Qt.AlignmentFlag.AlignCenter)

        mid_widget = QWidget()
        mid_layout = QVBoxLayout()
        mid_widget.setLayout(mid_layout)
        self.layout.addWidget(mid_widget)

        # add open torrent file dialog button
        open_file = QPushButton(" open &torrent file", self)
        open_file.clicked.connect(self.open_filedialog)
        open_file.setFixedSize(260, 40)
        add_icon = QIcon('resources/file.svg')
        open_file.setIcon(add_icon)
        open_file.setIconSize(QSize(26, 26))
        open_file.setFont(default_font)
        mid_layout.addWidget(open_file, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)

        # add open magnet link dialog button
        open_link = QPushButton(" add &magnet link")
        open_link.clicked.connect(self.open_magnetlink)
        open_link.setFixedSize(270, 40)
        add_icon = QIcon('resources/link.svg')
        open_link.setIcon(add_icon)
        open_link.setIconSize(QSize(26, 26))
        open_link.setFont(default_font)
        mid_layout.addWidget(open_link, alignment=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)

        # other ways of dropping/adding torrent
        support = QLabel("+ drag and drop support")
        support.setFont(default_font)
        support.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        mid_layout.addWidget(support)
        
        # license, author, year, link to github page, etc
        extra_info = QLabel("@CopyRight 2021 by Markus Telser")
        extra_info.setFont(small_font)
        extra_info.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(extra_info)
    
    def drawDragDropScreen(self):
        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        self.drop_label = QLabel(self)
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setText("Drag and Drop\nfiles here")
        self.drop_label.setFont(QFont('Arial', 18))
        self.drop_label.setStyleSheet("""QLabel{
            border: 4px dashed black;
            border-radius: 20px;
        }
        """)
        
        layout.addWidget(self.drop_label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        self.drawDragDropScreen()
        
        urls = event.mimeData().urls()
        if not urls or urls[0].scheme() != 'file' or len(urls[0].path()) <= 8 or urls[0].path()[-8:] != '.torrent':
            self.drop_label.setText('Wrong file format')

        event.accept()

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        self.addWidgets()
        
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls and urls[0].scheme() == 'file':
            if len(urls[0].path()) > 8 and urls[0].path()[-8:] == '.torrent':
                event.acceptProposedAction()
        
                file_path = event.mimeData().urls()[0].path()
                data = TorrentParser.parse_filepath(file_path)
                
                window = ViewWindow(self)
                window.show(data)

        self.addWidgets()
    
    def open_filedialog(self):
        dialog = QFileDialog(self, 'Open Torrent File')
        dialog.setMinimumSize(1000, 700)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("Torrent files (*.torrent)")
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog)
        dialog.setOption(QFileDialog.Option.DontUseCustomDirectoryIcons)
        dialog.setMimeTypeFilters(['application/x-bittorrent'])
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dialog.setDirectory(expanduser('~'))

        if dialog.exec():
            file_path = dialog.selectedFiles()[0]
            print(file_path)
            data = TorrentParser.parse_filepath(file_path)
            window = ViewWindow(self)
            window.show(data)
        
    def open_magnetlink(self):
        dialog = MagnetLinkDialog()
        
        if dialog.exec():
            magnet_link = dialog.text_box.text()
            #data = TorrentParser.parse_magnet_link(magnet_link)
            #window = ViewWindow(self)
            #window.show(data)


class MagnetLinkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setWindowTitle('Add Magnet Link')
        self.setWindowIcon(QIcon('resources/logo.png'))
        QApplication.clipboard().dataChanged.connect(self.insert_clipboard)
        self.setFixedSize(600, 120)
        
        message = QLabel("Enter magnet link:")
        self.layout.addWidget(message)

        self.text_box = QLineEdit()
        self.insert_clipboard()
        self.layout.addWidget(self.text_box)

        # button box with add and cancel
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)
        add_button = QPushButton(QIcon('resources/add.svg'), ' Add', self)
        buttonBox.addButton(add_button, QDialogButtonBox.ButtonRole.AcceptRole)
        buttonBox.layout().setDirection(QBoxLayout.Direction.LeftToRight)
        buttonBox.layout().setAlignment(Qt.AlignmentFlag.AlignRight)
        buttonBox.rejected.connect(self.reject)
        buttonBox.accepted.connect(self.accept)
        self.layout.addWidget(buttonBox)

    def insert_clipboard(self):
        clipboard = QApplication.clipboard().text()
        if clipboard.startswith('magnet:?'):
            self.text_box.setText(clipboard)
    
    def accept(self):
        if self.text_box.text():
            return super().accept()
        else:
            error_window = QMessageBox(self)
            error_window.setIcon(QMessageBox.Icon.Critical)
            error_window.setText('No magnet link inserted!')
            error_window.setWindowTitle("Error")
            error_window.show()