from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QTabWidget,
    QHBoxLayout,
    QWidget
)

from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import QSize, Qt, QModelIndex
import sys

from src.backend.metadata.TorrentParser import TorrentParser
from src.frontend.widgets.FileDialog import FileDialog
from src.frontend.widgets.MenuBar import MenuBar
from src.frontend.widgets.SidePanel import SidePanel
from src.frontend.widgets.StatusBar import StatusBar
from src.frontend.widgets.ToolBar import ToolBar
from src.frontend.ViewWindow import ViewWindow
from src.frontend.models.TorrentListModel import TorrentListModel
from src.frontend.views.TorrentListView import TorrentListView
from src.frontend.views.TorrentDetailView import TorrentDetailView

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

        self.torrent_list = list()

        self.addWidgets()
        
        self.show()
    
    def show(self, data=None):
        if data:
            self.appendRowEnd(data)
        super().show()
    
    def addWidgets(self):
        menuBar = MenuBar()
        self.setMenuBar(menuBar)
        
        toolBar = ToolBar()
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
        self.vert_splitter = QSplitter()
        self.vert_splitter.setOrientation(Qt.Orientation.Vertical)
        hori_splitter.addWidget(self.vert_splitter)
        hori_splitter.setCollapsible(1, False)
        hori_splitter.setStretchFactor(1, 70)
        
        # add main torrent table model / view
        self.table_model = TorrentListModel()
        self.table_view = TorrentListView(self.table_model, self)
        self.vert_splitter.addWidget(self.table_view)
        
        # bottom info panel
        self.detail_view = TorrentDetailView()
        self.vert_splitter.addWidget(self.detail_view)
        self.vert_splitter.setSizes([1, 0]) # hide info table
        
        toolBar.open_file.clicked.connect(self.open_file_window)
        self.table_view.doubleClicked.connect(self.open_detail)
        #self.table_view.selectionChanged.connect(self.open_detail2)
        
    def open_detail(self, mi):
        print(mi.row())
        print(self.torrent_list[mi.row()]['files'].name)
        if self.vert_splitter.sizes()[1] == 0:
            fsize = self.vert_splitter.size().height()
            self.vert_splitter.setSizes([int(fsize * 0.7),int(fsize * 0.3)])
        else:
            self.vert_splitter.setSizes([1,0])
        
    def open_detail2(self, old: QModelIndex, new: QModelIndex):
        print(old.row(), new.row())
    
    def open_file_window(self):
        dialog = FileDialog()
        
        if dialog.exec():
            file_path = dialog.selectedFiles()[0]
            data = TorrentParser.parse_filepath(file_path)
            window = ViewWindow(self)
            window.add_data.connect(self.appendRowEnd)
            window.show(data)
    
    def appendRowEnd(self, dt):
        self.torrent_list.append(dt)
        self.table_model.data.append([dt['files'].name, str(dt['files'].length)])
        self.table_model.updatedData.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ApplicationWindow()
    window.show()

    app.exec()