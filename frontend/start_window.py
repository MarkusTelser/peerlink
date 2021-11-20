import sys
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont, QGuiApplication, QIcon, QPixmap
from PyQt6.QtCore import QSize, Qt
from load_window import LoadWindow



class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FastPeer - StartPage")

        # set screen size
        width = 900
        min_width = 875
        height = 700
        min_height = 550
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

        # set background gradient
        self.setStyleSheet("""QMainWindow{
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(255, 0, 0, 255), stop:1 rgba(0, 42, 255, 255));
        }""")
        
        # TODO set start drag time
        self.setAcceptDrops(True)
        QApplication.clipboard().dataChanged.connect(self.clipboardChanged)

        self.addWidgets()

        self.setCentralWidget(self.widget)  

    def addWidgets(self):
        # set layout and create central widget
        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(100, 100, 100, 100)
        self.widget.setLayout(self.layout)

        # add all items from here on
        label1 = QLabel("BitTorrent Client")
        label1.setFont(QFont('Arial', 50))
        self.layout.addWidget(label1, alignment=Qt.AlignmentFlag.AlignHCenter)

        label = QLabel()
        pixmap = QPixmap('logo.png')
        pixmap2 = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        label.setPixmap(pixmap2)
        self.layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout2 = QHBoxLayout()
        b1 = QPushButton("open file", self)
        b1.setMinimumSize(200, 30)
        b1.setFont(QFont('Arial', 18))
        layout2.addWidget(b1, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout.addLayout(layout2)

        label1 = QLabel("paste magnet link")
        label1.setFont(QFont('Arial', 18))
        self.layout.addWidget(label1, alignment=Qt.AlignmentFlag.AlignCenter)

        label1 = QLabel("drag and drop support")
        label1.setFont(QFont('Arial', 18))
        self.layout.addWidget(label1, alignment=Qt.AlignmentFlag.AlignCenter)

        label1 = QLabel("""@CopyRight 2021 by Markus Telser""")
        label1.setFont(QFont('Arial', 12))
        self.layout.addStretch(300)
        self.layout.addWidget(label1, alignment=Qt.AlignmentFlag.AlignCenter)
        

    def dragEnterEvent(self, event):
        print("enter drag")

        urls = event.mimeData().urls()
        if urls and urls[0].scheme() == 'file':
            if len(urls[0].path()) > 8 and urls[0].path()[-8:] == '.torrent':
                event.accept()
        
        print(event.mimeData().urls())

        layout = QVBoxLayout()
        label = QLabel(self)
        label.setStyleSheet("""QLabel{
            border: 4px dashed black;
            border-radius: 20px;
        }
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setText("Drag and Drop\nfiles here")
        label.setFont(QFont('Arial', 18))
        layout.addWidget(label)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def dragLeaveEvent(self, event):
        print("leave drag")

        self.addWidgets()
        self.setCentralWidget(self.widget)   
        
        
    def dropEvent(self, event):
        print("drop event")
        
        LoadWindow().show()
        
        """
        # if not working then do this
        # display start screen
        self.addWidgets()
        self.setCentralWidget(self.widget)   
        """

    def clipboardChanged(self):
        text = QApplication.clipboard().text()
        print(text)
        # TODO check if it is magnet link







app = QApplication(sys.argv)

window = StartWindow()
window.show()

app.exec()