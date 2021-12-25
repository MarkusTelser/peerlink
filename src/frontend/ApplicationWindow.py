from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSizePolicy,
    QSplitter,
    QTabWidget,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget
)

from PyQt6.QtGui import QGuiApplication
import PyQt6
import sys
from PyQt6.QtCore import QSize, Qt
import time
from threading import Thread
from src.frontend.widgets.MenuBar import MenuBar
from src.frontend.widgets.SidePanel import SidePanel
from src.frontend.widgets.StatusBar import StatusBar
from src.frontend.widgets.ToolBar import ToolBar

from src.frontend.TorrentViewModel import TorrentModel, TorrentView

class ApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("FastPeer - Application Window")
        
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
        
        
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background-color: red;")
        self.main_layout = QHBoxLayout()
        
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.addWidgets()
        self.addBars()
        
        Thread(target=self.appendRowEnd).start()
        
        self.show()
    
    def addWidgets(self):
        # horizontal splitter for side panel, vertical splitter
        hori_splitter = QSplitter()
        hori_splitter.setOrientation(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(hori_splitter)
        
        side_panel = SidePanel()
        hori_splitter.addWidget(side_panel)
        hori_splitter.setStretchFactor(0, 30)
        
        # vertical splitter for main table, info table
        vert_splitter = QSplitter()
        vert_splitter.setOrientation(Qt.Orientation.Vertical)
        hori_splitter.addWidget(vert_splitter)
        hori_splitter.setCollapsible(1, False)
        hori_splitter.setStretchFactor(1, 70)
        
        # add main torrent table model / view
        self.table_model = TorrentModel()
        self.table_view = TorrentView(self.table_model, self)
        vert_splitter.addWidget(self.table_view)
        
        # bottom info panel
        panel2 = QTabWidget()
        
        panel2.addTab(QWidget(), "General")
        panel2.addTab(QWidget(), "Trackers")
        panel2.addTab(QWidget(), "Peers")
        
        panel2.setStyleSheet("background-color: blue;")
        vert_splitter.addWidget(panel2)
        vert_splitter.setSizes([1, 0]) # hide info table


    def addBars(self):
        menuBar = MenuBar()
        self.setMenuBar(menuBar)
        
        toolBar = ToolBar()
        self.addToolBar(toolBar)
        
        statusBar = StatusBar()
        self.setStatusBar(statusBar)
        
    def appendRowEnd(self):
        time.sleep(3)
        self.table_model.data.append(["hello1", "hello2"])
        self.table_model.updatedData.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ApplicationWindow()
    window.show()

    app.exec()