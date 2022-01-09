from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QTabWidget,
    QHBoxLayout,
    QWidget
)

from PyQt6.QtGui import QGuiApplication, QCloseEvent
from PyQt6.QtCore import QSize, Qt, QModelIndex
import sys
from threading import Thread

from src.backend.metadata.TorrentParser import TorrentParser
from src.backend.swarm import Swarm
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
    def __init__(self, parent=None):
        super(ApplicationWindow, self).__init__(parent)
        
        self.current_torrent = None
        
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
        super().show()
        if data:
            self.appendRowEnd(data)
        
    
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
        self.table_view.doubleClicked.connect(self.doubleclick_torrent)
        self.table_view.clicked.connect(self.select_torrent)
    
    def select_torrent(self, mi):
        data = self.torrent_list[mi.row()]
        self.detail_view._update(data)
    
    def doubleclick_torrent(self, mi):
        if self.vert_splitter.sizes()[1] == 0:
            data = self.torrent_list[mi.row()]
            self.detail_view._update(data)
            fsize = self.vert_splitter.size().height()
            self.vert_splitter.setSizes([int(fsize * 0.7),int(fsize * 0.3)])
        elif self.current_torrent == mi.row():
            self.vert_splitter.setSizes([1,0])
        self.current_torrent = mi.row()
    
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
        #'strategy': strategy,
        #'check_hash' : check_hash,
        #'not_again' : not_again,
        s = Swarm(dt['data'], dt['path'])
        self.torrent_list.append(s)
        
        if dt['pad_files']:
            print("padded torrent files")
            Thread(target=s.file_handler.padd_files).start()
        if dt['start']:
            print('started torrent')
            t = Thread(target=s.start)
            t.start()
        
        self.table_model.data.append([dt['data'].files.name, str(dt['data'].files.length)])
        self.table_model.updatedData.emit()
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ApplicationWindow()
    window.show()

    app.exec()