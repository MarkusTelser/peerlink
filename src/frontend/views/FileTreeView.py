from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QTreeView


class FileTreeView(QTreeView):
    def __init__(self, model):
        super().__init__()
        
        self.model = model
        self.setModel(self.model)        
        self.model.update_data.connect(self.reevaluate)
        self.setObjectName('filetree')
    
    def reevaluate(self):
        self.expandAll()
        for i in range(self.model.columnCount()):        
            self.resizeColumnToContents(i)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if self.indexAt(event.pos()).row() == -1:
            self.clearSelection()
            self.clearFocus()
        return super().mouseDoubleClickEvent(event)
       