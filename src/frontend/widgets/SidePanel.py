from ctypes import alignment
from distutils.log import debug
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QIcon, QMouseEvent, QAction, QFont
from PyQt6.QtWidgets import (
    QTabWidget, 
    QVBoxLayout,
    QWidget, 
    QTreeWidget, 
    QTreeWidgetItem, 
    QFrame, 
    QSizePolicy,
    QPlainTextEdit,
    QLineEdit,
    QComboBox,
    QHBoxLayout,
    QLabel
)

class CategoryTab(QWidget):
    def __init__(self):
        super().__init__()

class LogTab(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        sub_widget = QWidget()
        sub_layout = QHBoxLayout()
        sub_layout.setContentsMargins(0, 0, 0, 0)
        sub_widget.setLayout(sub_layout)
        
        options = ["Debug", "Info", "Warning", "Error", "Critical"]
        debug_level = QComboBox()
        debug_level.addItems(options)
        sub_layout.addStretch()
        sub_layout.addWidget(QLabel('Logging Level: '))
        sub_layout.addWidget(debug_level)
        main_layout.addWidget(sub_widget)
        
        self.log_text = ""
        self.log_view = QPlainTextEdit(self.log_text)
        self.log_view.setReadOnly(True)
        #self.log_view.setDocument()
        self.log_view.setFont(QFont('Arial', 10))
        self.log_view.setStyleSheet('border: 2px solid black;')
        main_layout.addWidget(self.log_view)
        
        filter = QLineEdit()
        filter.setStyleSheet('border: 2px solid black;')
        filter.setPlaceholderText('Filter...')
        filter.setClearButtonEnabled(True)
        filter.findChild(QAction, "_q_qlineeditclearaction").setIcon(QIcon("resources/cancel.svg"))
        main_layout.addWidget(filter)
        
        filter.textChanged.connect(self.filter)
        debug_level.currentTextChanged.connect(self.change_loglevel)
        
    @pyqtSlot(str)
    def filter(self, text: str):
        if text == "":
            self.log_view.setPlainText(self.log_text)
            return
        
        displayed_text = ""
        for line in self.log_text.split('\n'):
            if text not in line:
                displayed_text += line + '\n'
        self.log_view.setPlainText(displayed_text)
    
    @pyqtSlot(str)
    def change_loglevel(self, level: str):
        pass

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
        self.doubleClicked.connect(lambda: self.clearFocus())

    @pyqtSlot()
    def item_selected(self):
        filters = []
        for item in self.selectedItems():
            if item.parent() != None:
                filter = f"{item.parent().text(0)}/{item.text(0)}"
                filters.append(filter)
            else:
                self.currentItem().setSelected(False)
            
        self.changed_item.emit(filters)
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
                ('Warning', 'resources/warning.svg'),
                ('Error', 'resources/error.svg')
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