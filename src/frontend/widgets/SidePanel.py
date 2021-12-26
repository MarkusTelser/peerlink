from PyQt6 import QtCore
from PyQt6.QtCore import QModelIndex
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTabWidget, QVBoxLayout, QWidget


from PyQt6.QtWidgets import QTabWidget, QSizePolicy, QTreeWidget, QTreeWidgetItem, QFrame

class OtherTab(QWidget):
    def __init__(self):
        super().__init__()

class FilterTab(QWidget):
    changed_item = QtCore.pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        data = {
            'Torrents' : [
                ('All', 'resources/all.svg'),
                ('Active', 'resources/active.svg'),
                ('Inactive', 'resources/inactive.svg'),
                ('Downloading', 'resources/downloading.svg'),
                ('Leeching', 'resources/leeching.svg'),
                ('Seeding', 'resources/seeding.svg'),
                ('Overseeding', 'resources/overseeding.svg'),
                ('Stalling', 'resources/stalling.svg'),
                ('Download Stalling', 'resources/stalling_download.svg'),
                ('Upload Stalling', 'resources/stalling_upload.svg')
            ],
            'Trackers': [
                ('Working', 'resources/working.svg'),
                ('Unreachable', 'resources/unreachable.svg'),
                ('Error', 'resources/error.svg'),
                ('Warning', 'resources/warning.svg')
            ]
        }
        
        self.tab_tree = QTreeWidget()
        self.tab_tree.itemSelectionChanged.connect(self.item_selected)
        self.tab_tree.setStyleSheet("""                  
        QTreeView{
            border: 0px solid white;
            show-decoration-selected: 0;
        }
        QTreeView::item:selected {
            border: 1px solid green;
            background: rgb(0,77,0);
        }

        QTreeView::branch:has-children:!has-siblings:closed,
        QTreeView::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(resources/branch-closed.png);
        }

        QTreeView::branch:open:has-children:!has-siblings,
        QTreeView::branch:open:has-children:has-siblings  {
                border-image: none;
                image: url(resources/branch-open.png);
        }
        """)
        self.tab_tree.setFrameShadow(QFrame.Shadow.Raised)
        self.tab_tree.header().hide()
        
        for key in data.keys(): 
            category = QTreeWidgetItem(self.tab_tree)
            category.setText(0, key)
            
            for item in data[key]:
                name, icon = item
                child = QTreeWidgetItem()
                child.setText(0, name)
                child.setIcon(0, QIcon(icon))
                category.addChild(child)
        
        self.tab_tree.expandAll()
        layout.addWidget(self.tab_tree)
        
    def item_selected(self):
        filter_string = ""
        for item in self.tab_tree.selectedItems():
            if item.parent() != None:
                filter_string += item.parent().text(0)
                filter_string += f"/{item.text(0)}"
            else:
                item.setSelected(False)
                filter_string += item.text(0)
        self.changed_item.emit(filter_string)
    
    def mouse_pressed():
        pass
        

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