from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtGui import QGuiApplication, QIcon


class IpFilterWindow(QMainWindow):
    def __init__(self, parent):
        super(IpFilterWindow, self).__init__(parent=parent)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.resize(600, 600)
        self.setObjectName("IpFilterWindow")
        self.setWindowTitle("IP Filter - PeerLink")
        self.setWindowIcon(QIcon('resources/icons/logo.svg'))
        
        # center in the middle of screen
        qtRectangle = self.frameGeometry()
        qtRectangle.moveCenter(parent.frameGeometry().center())
        self.move(qtRectangle.topLeft())