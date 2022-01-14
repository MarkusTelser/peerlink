from PyQt6.QtGui import QStandardItemModel
from PyQt6.QtWidgets import QTreeView

class TorrentTreeView(QTreeView):
    def __init__(self, model):
        super().__init__()
        
        self.model = model
        self.setModel(self.model)        
        self.model.update_data.connect(self.reevaluate)
    
    def reevaluate(self):
        self.expandAll()
        for i in range(self.model.columnCount()):        
            self.resizeColumnToContents(i)
       