from PyQt6.QtCore import QModelIndex, QSortFilterProxyModel, pyqtSignal
from PyQt6.QtGui import QStandardItemModel

class SortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, source_model: QStandardItemModel):
        super().__init__()
        
        self.filters = list()
        self.source_model = source_model
        self.setSourceModel(source_model)
        self.setDynamicSortFilter(True)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex):
        if "Files/Single File" in self.filters:
            if self.source_model.torrent_list[source_row].data.has_multi_file:
                return False
        if "Files/Multi File" in self.filters:
            if not self.source_model.torrent_list[source_row].data.has_multi_file:
                return False
        return super().filterAcceptsRow(source_row, source_parent)
    
    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:  
        column_index = left.column()
        
        # size
        if column_index == 1: 
            sizes = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB'] 
            size1 = self.source_model.data[left.row()][left.column()].split(' ')
            size2 = self.source_model.data[right.row()][right.column()].split(' ')
            
            if sizes.index(size1[1]) == sizes.index(size2[1]):
                return float(size1[0]) < float(size2[0])
            return sizes.index(size1[1]) < sizes.index(size2[1])
        # progress
        elif column_index == 2:
            pass
        
        return super().lessThan(left, right)