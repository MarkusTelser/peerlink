from PyQt6 import QtGui
from PyQt6.QtCore import QAbstractItemModel, QStringListModel
from PyQt6.QtGui import (
    QStandardItem,
    QStandardItemModel
)
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLayout,
    QMainWindow,
    QTableView,
    QWidget,
    QLabel
)
from PyQt6 import QtCore
import sys
import time
import threading

class TorrentModel(QStandardItemModel):
    updatedData = QtCore.pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.setHorizontalHeaderLabels(["name", "size", "progress"])
        
        self.data = [
            ["data1", "data1.1"],
            ["data2", "data2.2"]
        ]
        self._update()
        
    @QtCore.pyqtSlot()
    def _update(self):
        for i, row in enumerate(self.data):
            for j, column in enumerate(row):
                item = QStandardItem(column)
                self.setItem(i, j, item)
        

class TorrentView(QTableView):
    def __init__(self, model, parent):
        super().__init__()
        
        self.model = model
        self.parent = parent
        
        # connect model signals to gui
        #self.model.updatedData.connect(self.update_text)
        self.model.updatedData.connect(model._update)
        
        # vertical & horizontal header settings
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setSectionsClickable(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionsMovable(True)
        self.verticalHeader().hide()
        
        # generic settings
        self.setMinimumWidth(200)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setStyleSheet("background-color: yellow;")
        
        self.setModel(model)
        
    @QtCore.pyqtSlot()
    def update_text(self):
        self.parent.label.setText(str(len(self.model.data)))
        self.model._update()
        print("updated", len(self.model.data))


"""
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # set central widget and main layout
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        self.label = QLabel()
        self.label.setText("not changed")
        main_layout.addWidget(self.label)
        
        # add model and view
        self.model = TorrentModel()
        view = TorrentView(self.model, self)
        main_layout.addWidget(view)
        
        self.setWindowTitle("hello world")
        
        threading.Thread(target=self.data_changes_itself).start()
        
    def data_changes_itself(self):
        while True:
            time.sleep(1)
            # changed data here
            self.model.data.append(["data3", "data3.3"])
            self.model.updatedData.emit()
        
"""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    model = TorrentModel()
    view = TorrentView(model, None)
    view.show()
    
    app.exec()