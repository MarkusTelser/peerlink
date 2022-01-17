from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QIcon, QMouseEvent
from PyQt6.QtWidgets import QTabWidget, QVBoxLayout, QWidget, QTreeWidget, QTreeWidgetItem, QFrame, QSizePolicy

class LogTab(QWidget):
    def __init__(self):
        super().__init__()

class FilterTree(QTreeWidget):
    changed_item = pyqtSignal(list)
    
    def __init__(self, data):
        super().__init__()

        self.setStyleSheet("""                  
        QTreeView{
            border: 0px solid white;
            show-decoration-selected: 0;
        }
        QTreeWidget::item:selected {
            background-color: blue;
        }
        QTreeWidget::branch:has-children:!has-siblings:closed,
        QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(resources/branch-closed.png);
        }

        QTreeWidget::branch:open:has-children:!has-siblings,
        QTreeWidget::branch:open:has-children:has-siblings  {
                border-image: none;
                image: url(resources/branch-open.png);
        }
        """)

        for key in data.keys(): 
            category = QTreeWidgetItem(self)
            category.setText(0, key)
            
            for item in data[key]:
                name, icon = item
                child = QTreeWidgetItem()
                child.setText(0, name)
                child.setIcon(0, QIcon(icon))
                category.addChild(child)
    
        self.expandAll()
        self.header().hide()
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setSelectionMode(QTreeWidget.SelectionMode.MultiSelection)
       

        self.itemSelectionChanged.connect(self.item_selected)
        self.itemDoubleClicked.connect(self.item_doubleclick)
        self.doubleClicked.connect(self.item_selected)

    @pyqtSlot()
    def item_selected(self):
        filters = []
        for item in self.selectedItems():
            if item.parent() != None:
                filter = item.parent().text(0)
                filter += f"/{item.text(0)}"
                if filter not in filters:
                    filters.append(filter)
                    self.changed_item.emit(filters)
            else:
                self.currentItem().setSelected(False)
                self.clearFocus()
    
    @pyqtSlot(QTreeWidgetItem, int)
    def item_doubleclick(self, item: QTreeWidgetItem, column: int):
        # if is a top level category
        if self.currentItem().childCount() != 0:
            self.currentItem().setSelected(False)
            self.clearFocus()
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if self.indexAt(event.pos()).data() == None:
            self.clearSelection()
            self.clearFocus()
        return super().mouseDoubleClickEvent(event)
    

class FilterTab(QWidget):    
    def __init__(self):
        super().__init__()
        
        layout  = QVBoxLayout()
        self.setLayout(layout)
        
        data = {
            'Torrents' : [
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
            ],
            'Files': [
                ('Single File', 'resources/file.svg'),
                ('Multi File', 'resources/multifile.svg')
            ]
        }
        self.filter_tree = FilterTree(data)
        self.filter_tree.topLevelItem(2).setExpanded(False)
        layout.addWidget(self.filter_tree)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if self.filter_tree.itemAt(event.pos()) == None:
            self.filter_tree.clearSelection()
            self.filter_tree.clearFocus()
        return super().mouseDoubleClickEvent(event)
        

class SidePanel(QTabWidget):
    def __init__(self):
        super().__init__()
        
        # generic settings
        self.setMovable(True)
        self.setStyleSheet("background-color: green;")
        self.setUpdatesEnabled(True)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        tab1 = FilterTab()
        tab2 = LogTab()
        
        self.tabs = list()
        self.tabs.append([tab1, "Filter"])
        self.tabs.append([tab2, "Log"])
        
        
    def tabspos(self):
        return [self.indexOf(tab[0]) for tab in self.tabs]
    
    def set_tabspos(self, pos):
        if len(pos) == 0:
            pos = [x for x in range(len(self.tabs))]
        for p in pos:
            self.addTab(self.tabs[int(p)][0], self.tabs[int(p)][1])
        