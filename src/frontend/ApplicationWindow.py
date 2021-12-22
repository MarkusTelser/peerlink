from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenuBar,
    QMenu,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QToolBar,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QFrame
)

from PyQt6.QtGui import (
    QAction,
    QGuiApplication,
    QIcon,
    QKeySequence
)
import PyQt6
import sys
from PyQt6.QtCore import QSize, Qt
import time
from threading import Thread

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
        self.layout = QHBoxLayout()
        
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.addWidgets()
        self.addBars()
        
        Thread(target=self.appendRowEnd).start()
        
        self.show()
        
    def appendRowEnd(self):
        time.sleep(3)
        row_count = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_count)
        self.tableWidget.setItem(row_count, 0, QTableWidgetItem("text1"))
        self.tableWidget.setItem(row_count, 1, QTableWidgetItem("text2"))
    
    def addWidgets(self):
        # horizontal splitter between left side panel and right two panels
        hori_splitter = QSplitter()
        hori_splitter.setOrientation(Qt.Orientation.Horizontal)
        self.layout.addWidget(hori_splitter)
        
        # vertical splitter between top und bottom right panels
        vert_splitter = QSplitter()
        vert_splitter.setOrientation(Qt.Orientation.Vertical)
        
        # left side panel
        tabWidget = QTabWidget()
        tabWidget.setStyleSheet("background-color: green;")
        tabWidget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        tab1 = QWidget()
        tabWidget.addTab(tab1, "filters")
        
        tab2 = QWidget()
        tabWidget.addTab(tab2, "other")
        hori_splitter.addWidget(tabWidget)
        hori_splitter.setStretchFactor(0, 30)
        
        # default panel
        header_data = ["name", "city"]
        rows = [
            ["Aloysius", "Indore"],
            ["Alan", "Bhopal"],
            ["Arnavi", "Mandsaur"]
        ]
        
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(rows))
        self.tableWidget.setColumnCount(len(rows[0]))
        self.tableWidget.setStyleSheet("background-color: yellow;")
        
        self.tableWidget.setHorizontalHeaderLabels(header_data)
        for i, row in enumerate(rows):
            print(i, row)
            self.tableWidget.insertRow(i)
            for j, column in enumerate(row):
                item = QTableWidgetItem(column)
                self.tableWidget.insertItem(i, j, item)
   
        
        
        # make
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tableWidget.horizontalHeader().setSectionsMovable(True)
        self.tableWidget.verticalHeader().hide()
        
        self.tableWidget.horizontalHeader().setSectionsClickable(True) # sort if clicked
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        
        vert_splitter.addWidget(self.tableWidget)
        
        # bottom info panel
        panel2 = QTabWidget()
        
        panel2.addTab(QWidget(), "General")
        panel2.addTab(QWidget(), "Trackers")
        panel2.addTab(QWidget(), "Peers")
        
        panel2.setStyleSheet("background-color: blue;")
        vert_splitter.addWidget(panel2)
        vert_splitter.setSizes([1, 0])
        
        hori_splitter.addWidget(vert_splitter)
        hori_splitter.setCollapsible(1, False)
        hori_splitter.setStretchFactor(1, 70)
        

    def addBars(self):
        self.attachMenuBar()
        self.attachToolBar()
        self.attachStatusBar()
        
    def attachMenuBar(self):
        menuBar = QMenuBar()
        
        # file menu
        fileMenu = QMenu("&File", self)
        fileIcon = QIcon("resources/file.svg")
        fileShortcut = QKeySequence("Ctrl+O")
        fileMenu.addAction(fileIcon, "Open file", self.pressed, fileShortcut)
        fileMenu.addAction("Open magnet link")
        fileMenu.addSeparator()
        fileMenu.addAction("Exit")
        menuBar.addMenu(fileMenu)
        
        # edit menu
        editMenu = QMenu("&Edit", self)
        menuBar.addMenu(editMenu)
        
        # settings menu
        settingsMenu = QMenu("&Settings", self)
        menuBar.addMenu(settingsMenu)
        
        # help menu
        helpMenu = QMenu("&Help", self)
        menuBar.addMenu(helpMenu)
        
        self.setMenuBar(menuBar)
    
    def attachToolBar(self):
        toolBar = QToolBar()
        toolBar.setMovable(False)
        
        resume = QAction("Resume", self)
        resume.setToolTip("is resuming the current torrent")
        toolBar.addAction(resume)
        toolBar.addAction("Pause")
        toolBar.addAction("Resume All")
        toolBar.addAction("Pause All")
        
        self.addToolBar(toolBar)
        
    def attachStatusBar(self):
        statusBar = QStatusBar()
        
        download_speed = QLabel("0 MB/s")
        statusBar.addPermanentWidget(download_speed)
        
        upload_speed = QLabel("0 MB/s")
        statusBar.addPermanentWidget(upload_speed)
        
        count_peers = QLabel("10 Peers")
        statusBar.addPermanentWidget(count_peers)
        
        count_nodes = QLabel("0 DHT Nodes")
        statusBar.addPermanentWidget(count_nodes)
        
        self.setStatusBar(statusBar)
    
    def pressed(self):
        print("pressed")
    
    

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ApplicationWindow()
    window.show()

    app.exec()