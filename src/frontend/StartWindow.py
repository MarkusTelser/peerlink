import sys
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QFileDialog, QSizePolicy
from PyQt6.QtGui import QFont, QGuiApplication, QIcon, QPixmap, QDragEnterEvent
from PyQt6.QtCore import QSize, Qt
from src.backend.metadata import TorrentParser
from .load_window import LoadWindow
from os.path import expanduser


class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("FastPeer - StartPage")
        self.setObjectName("StartWindow")

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
        
        self.setAcceptDrops(True)
        QApplication.clipboard().dataChanged.connect(self.clipboardChanged)

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
        add_icon = QIcon('resources/folder.svg')
        open_file.setIcon(add_icon)
        open_file.setIconSize(QSize(32, 32))
        open_file.setFont(default_font)
        mid_layout.addWidget(open_file, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)

        # add open magnet link dialog button
        open_link = QPushButton(" add &magnet link")
        open_link.clicked.connect(self.open_magnetlink)
        open_link.setFixedSize(270, 40)
        add_icon = QIcon('resources/add3.svg')
        open_link.setIcon(add_icon)
        open_link.setIconSize(QSize(32, 32))
        open_link.setFont(default_font)
        #open_link.setToolTip('this is it')
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
        
        label = QLabel(self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setText("Drag and Drop\nfiles here")
        label.setFont(QFont('Arial', 18))
        label.setStyleSheet("""QLabel{
            border: 4px dashed black;
            border-radius: 20px;
        }
        """)
        
        layout.addWidget(label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        urls = event.mimeData().urls()
        if urls and urls[0].scheme() == 'file':
            if len(urls[0].path()) > 8 and urls[0].path()[-8:] == '.torrent':
                event.accept()
                self.drawDragDropScreen()

    def dragLeaveEvent(self, event):
        self.addWidgets()
        
    def dropEvent(self, event):
        data = TorrentParser.parse_filepath(event.mimeData().urls()[0].path())
        window = LoadWindow(self)
        window.show(data)
        
        self.addWidgets()

    def clipboardChanged(self):
        text = QApplication.clipboard().text()
        print(text)

    
    def open_filedialog(self, event):
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
            window = LoadWindow(self)
            window.show(data)
        
    def open_magnetlink(self, event):
        pass


app = QApplication(sys.argv)

window = StartWindow()
window.show()

sys.exit(app.exec())