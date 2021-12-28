from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QTabWidget,
    QHBoxLayout,
    QWidget
)

from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import QSize, Qt
import sys

from src.backend.metadata.TorrentParser import TorrentParser
from src.frontend.widgets.MenuBar import MenuBar
from src.frontend.widgets.SidePanel import SidePanel
from src.frontend.widgets.StatusBar import StatusBar
from src.frontend.widgets.ToolBar import ToolBar
from src.frontend.ViewWindow import ViewWindow
from src.frontend.models.TorrentListModel import TorrentListModel
from src.frontend.views.TorrentListView import TorrentListView

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
        
        self.show()
    
    def addWidgets(self):
        menuBar = MenuBar()
        self.setMenuBar(menuBar)
        
        toolBar = ToolBar()
        toolBar.open_file.triggered.connect(self.open_file_window)
        self.addToolBar(toolBar)
        
        statusBar = StatusBar()
        self.setStatusBar(statusBar)
        
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
        self.table_model = TorrentListModel()
        self.table_view = TorrentListView(self.table_model, self)
        vert_splitter.addWidget(self.table_view)
        
        # bottom info panel
        panel2 = QTabWidget()
        
        panel2.addTab(QWidget(), "General")
        panel2.addTab(QWidget(), "Trackers")
        panel2.addTab(QWidget(), "Peers")
        
        panel2.setStyleSheet("background-color: blue;")
        vert_splitter.addWidget(panel2)
        vert_splitter.setSizes([1, 0]) # hide info table
    
    def open_file_window(self):
        path = "data/all/solo.torrent"
        data = TorrentParser.parse_filepath(path)
       
        window = ViewWindow(self)
        window.add_data.connect(self.appendRowEnd)
        window.show(data)
    
    def appendRowEnd(self, txt):
        self.table_model.data.append([txt["name"], "hello2"])
        self.table_model.updatedData.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ApplicationWindow()
    window.show()

    app.exec()