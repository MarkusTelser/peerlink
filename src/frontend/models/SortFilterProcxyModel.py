from PyQt6.QtCore import QModelIndex, QSortFilterProxyModel
from PyQt6.QtGui import QStandardItemModel


class SortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, source_model: QStandardItemModel, session):
        super().__init__()
        
        self.filters = list()
        self.cat_info = ""
        self.cat_filter = ""
        
        self.session = session
        self.source_model = source_model
        self.setSourceModel(source_model)
        self.setDynamicSortFilter(True)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex):
        if "File Mode/Single File" in self.filters:
            if self.session.swarm_list[source_row].data.has_multi_file:
                return False
        if "File Mode/Multi File" in self.filters:
            if not self.session.swarm_list[source_row].data.has_multi_file:
                return False
        if "All" in self.cat_info:
            return True
        if "Categorized" in self.cat_info:
            if self.session.swarm_list[source_row].category == "":
                return False
        if "Uncategorized" in self.cat_info:
            if self.session.swarm_list[source_row].category != "":
                return False
        if self.cat_filter !=  "" and self.cat_filter != self.session.swarm_list[source_row].category:
            return False    
        
        return super().filterAcceptsRow(source_row, source_parent)
    
    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:  
        column_index = left.column()
        # size
        if column_index == 1: 
            size1 = self.session.swarm_list[left.row()].data.files.length #.data[left.row()][left.column()].split(' ')
            size2 = self.session.swarm_list[right.row()].data.files.length #self.source_model.data[right.row()][right.column()].split(' ')
            return size1 < size2
        # progress
        elif column_index == 2:
            pass
        
        return super().lessThan(left, right)