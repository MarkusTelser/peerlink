from PyQt6.QtWidgets import QHeaderView, QTableView, QAbstractItemView
from PyQt6.QtCore import pyqtSlot

class TorrentListView(QTableView):
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
        
    @pyqtSlot()
    def update_text(self):
        self.parent.label.setText(str(len(self.model.data)))
        self.model._update()
        print("updated", len(self.model.data))