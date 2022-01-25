from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QIcon, QMouseEvent
from PyQt6.QtWidgets import QTabWidget, QVBoxLayout, QWidget, QTreeWidget, QTreeWidgetItem, QFrame, QSizePolicy

class CategoryTab(QWidget):
    def __init__(self):
        super().__init__()

class LogTab(QWidget):
    def __init__(self):
        super().__init__()

class FilterTree(QTreeWidget):
    changed_item = pyqtSignal(list)
    
    def __init__(self, data):
        super().__init__()

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
            'File Mode': [
                ('Single File', 'resources/file.svg'),
                ('Multi File', 'resources/multifile.svg')
            ],
            'Peer Discovery': [
                ('Centralized', 'resources/centralized.svg'),
                ('Decentralized', 'resources/decentralized.svg'),
                ('Mixed', 'resources/mixed.svg')
            ]
        }
        self.filter_tree = FilterTree(data)
        self.filter_tree.topLevelItem(2).setExpanded(False)
        self.filter_tree.topLevelItem(3).setExpanded(False)
        layout.addWidget(self.filter_tree)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if self.filter_tree.itemAt(event.pos()) == None:
            self.filter_tree.clearSelection()
            self.filter_tree.clearFocus()
        return super().mouseDoubleClickEvent(event)
        

class SidePanel(QTabWidget):
    def __init__(self, tabs_pos):
        super().__init__()
        
        # generic settings
        self.setMovable(True)
        self.setUpdatesEnabled(True)
        self.setObjectName('sidepanel')
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        tab1 = FilterTab()
        tab2 = CategoryTab()
        tab3 = LogTab()
        
        self.tabs = list()
        self.tabs.append([tab1, QIcon('resources/filter.svg'), "Filters"])
        self.tabs.append([tab2, QIcon('resources/category.svg'), "Categorys"])
        self.tabs.append([tab3, QIcon('resources/log.svg'), "Logs"])
        self.setUsesScrollButtons(False)
        
        # arrange in right order 
        if len(tabs_pos) == 0:
            tabs_pos = [x for x in range(len(self.tabs))]
        for p in tabs_pos:
            self.addTab(self.tabs[int(p)][0], self.tabs[int(p)][1], self.tabs[int(p)][2])
        
        # add hidden ones
        for p in set([x for x in range(len(self.tabs))]) - set([int(x) for x in tabs_pos]):
            self.addTab(self.tabs[int(p)][0], self.tabs[int(p)][1], self.tabs[int(p)][2])
            self.setTabVisible(self.count()-1, False)
        
    def tabspos(self):
        tab_texts = [x[2] for x in self.tabs]
        return [tab_texts.index(self.tabText(i)) for i in range(len(self.tabs)) if self.isTabVisible(i)]