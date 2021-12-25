from PyQt6.QtCore import QModelIndex
from PyQt6.QtWidgets import QTabWidget, QVBoxLayout, QWidget


from PyQt6.QtWidgets import QTabWidget, QSizePolicy, QTreeWidget, QTreeWidgetItem

class OtherTab(QWidget):
    def __init__(self):
        super().__init__()

class FilterTab(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        data = {
            'Torrents' : [
                'Active',
                'Inactive',
                'Downloading',
                'Seeding',
                'Leeching'
            ],
            'Trackers': [
                'Working',
                'Unreachable'
                'Error',
                'Warnings'
            ]
        }
        
        tab_tree = QTreeWidget()
        #tab_tree.setIndentation(0)
        
        for key in data.keys(): 
            category = QTreeWidgetItem(tab_tree)
            category.setText(0, key)
            
            for item in data[key]:
                child = QTreeWidgetItem()
                child.setText(0, item)
                category.addChild(child)
        
        layout.addWidget(tab_tree)        
        

class SidePanel(QTabWidget):
    def __init__(self):
        super().__init__()
        
        # generic settings
        self.setStyleSheet("background-color: green;")
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        tab1 = FilterTab()
        tab2 = OtherTab()
        
        self.addTab(tab1, "Filter")
        self.addTab(tab2, "Others")