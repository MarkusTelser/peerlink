from unicodedata import category
from PyQt6.QtWidgets import (
    QTabWidget, 
    QVBoxLayout,
    QWidget, 
    QListWidget,
    QListWidgetItem, 
    QTreeWidget,
    QTreeWidgetItem,
    QFrame, 
    QSizePolicy,
    QPlainTextEdit,
    QLineEdit,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QMenu,
    QInputDialog,
    QAbstractScrollArea
)
from PyQt6.QtGui import QIcon, QMouseEvent, QAction, QFont
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt

from src.frontend.utils.utils import showError, showInput

class CategoryMenu(QMenu):
    def __init__(self, parent):
        super(CategoryMenu, self).__init__(parent)
        
        self.menu_new = QAction(self.tr("New"))
        self.menu_new.setIcon(QIcon('resources/icons/add.svg'))
        self.menu_rename = QAction(self.tr("Rename"))
        self.menu_rename.setIcon(QIcon('resources/icons/rename.svg'))
        self.menu_delete = QAction(self.tr("Delete"))
        self.menu_delete.setIcon(QIcon('resources/icons/remove.svg'))
        self.addAction(self.menu_new)
        self.addAction(self.menu_rename)
        self.addAction(self.menu_delete)


class CategoryList(QListWidget):
    def __init__(self) -> None:
        super().__init__()
        
        self.setSortingEnabled(True)
        
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Ignored)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # create context menu
        self.menu = CategoryMenu(self)
        
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            if self.itemAt(event.pos()) == None or len(self.selectedIndexes()) == 0:
                self.menu.menu_rename.setDisabled(True)
                self.menu.menu_delete.setDisabled(True)
            else:
                self.menu.menu_rename.setEnabled(True)
                self.menu.menu_delete.setEnabled(True)
                
            self.menu.popup(self.viewport().mapToGlobal(event.pos()))
            self.menu.exec()
        elif self.itemAt(event.pos()) == None:
            self.clearSelection()
        return super().mousePressEvent(event)

class CategoryTab(QWidget):
    infoSelected = pyqtSignal(str)
    catSelected = pyqtSignal(str)
    
    newCategory = pyqtSignal(str)
    renameCategory = pyqtSignal(str, str)
    deleteCategory = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        self._all = 0
        self._cat = 0
        self._uncat = 0
        self._cats = dict()
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        self.info_list = QListWidget()
        self.option1 = QListWidgetItem(QIcon('resources/icons/general.svg'), self.tr("All ({})").format(0), self.info_list)
        self.option2 = QListWidgetItem(QIcon('resources/icons/category.svg'), self.tr("Categorized ({})").format(0), self.info_list)
        self.option3 = QListWidgetItem(QIcon('resources/icons/inactive.svg'), self.tr("Uncategorized ({})").format(0), self.info_list)
        print(self.info_list.sizeHint())
        main_layout.addWidget(self.info_list)    
        
        self.cat_box = QGroupBox(self.tr("Categorys ({})").format(len(self._cats)))
        self.cat_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.cat_layout = QVBoxLayout()
        self.cat_box.setLayout(self.cat_layout)
        self.cat_list = CategoryList()
        self.cat_layout.addWidget(self.cat_list)
        main_layout.addWidget(self.cat_box)
        
        self.info_list.itemClicked.connect(self._info_selected)
        self.cat_list.itemClicked.connect(self._cat_selected)
        self.cat_list.menu.menu_new.triggered.connect(self._new)
        self.cat_list.menu.menu_rename.triggered.connect(self._rename)
        self.cat_list.menu.menu_delete.triggered.connect(self._delete)
    
    def setCategorys(self, categorys, show_error=False):
        for category in categorys:
            if category not in self._cats:
                self.cat_list.addItem(QListWidgetItem(f"{category} (0)"))
                self._cats[category] = 0
            elif show_error:
                showError(self.tr("Category name exists already!"), self)
        
        self.cat_box.setTitle(self.tr("Categorys ({})").format(len(self._cats)))
    
    def append(self, torrent):
        self._all += 1
        self._cat += 1 if len(torrent.category) > 0 else 0
        self._uncat += 1 if len(torrent.category) == 0 else 0
        
        self.option1.setText(self.tr("All ({})").format(self._all))
        self.option2.setText(self.tr("Categorized ({})").format(self._cat))
        self.option3.setText(self.tr("Uncategorized ({})").format(self._uncat))
        
        if torrent.category != "":
            # add category if not already existing
            if torrent.category not in self._cats:
                self.setCategorys([torrent.category])
                self.newCategory.emit(torrent.category)
                
            find_name = f"{torrent.category} ({self._cats[torrent.category]})"
            finds = self.cat_list.findItems(find_name, Qt.MatchFlag.MatchExactly)
            if len(finds) != 0:
                self._cats[torrent.category] += 1
                finds[0].setText(f"{self._extract(finds[0].text())} ({self._cats[torrent.category]})")
    
    def remove(self, category):
        self._all -= 1
        self._cat -= 1 if len(category) > 0 else 0
        self._uncat -= 1 if len(category) == 0 else 0
        
        self.option1.setText(self.tr("All ({})").format(self._all))
        self.option2.setText(self.tr("Categorized ({})").format(self._cat))
        self.option3.setText(self.tr("Uncategorized ({})").format(self._uncat))
        
        if len(category) != 0:
            find_name = f"{category} ({self._cats[category]})"
            finds = self.cat_list.findItems(find_name, Qt.MatchFlag.MatchExactly)
            
            self._cats[category] -= 1
            finds[0].setText(f"{category} ({self._cats[category]})")
        
    @pyqtSlot()
    def _new(self):
        dialog = showInput(self.tr("Enter new category name:"), self)
        
        if dialog.exec():
            name = dialog.textValue()
            self.setCategorys([name], show_error=True)
            self.newCategory.emit(name)
    
    @pyqtSlot()
    def _rename(self):  
        indexes = self.cat_list.selectedItems()
        cat_name = self._extract(indexes[0].data(0))        
        dialog = showInput(self.tr('Rename category "{}" to:').format(cat_name), self)

        if dialog.exec():
            new_name = dialog.textValue()
            
            # show error if new name exists already
            if new_name in self._cats:
                showError(self.tr("Category name exists already!"), self)
                return
            
            # rename gui item, change internal struct
            indexes[0].setText(f"{new_name} ({self._cats[cat_name]})")
            self._cats[new_name] = self._cats[cat_name]
            del self._cats[cat_name]
            
            self.renameCategory.emit(cat_name, new_name)
    
    @pyqtSlot()
    def _delete(self): 
        indexes = self.cat_list.selectedIndexes()
        cat_name = self._extract(indexes[0].data()) 
        item = self.cat_list.takeItem(indexes[0].row())
        del item
        
        # update info texts
        self._cat -= self._cats[cat_name]
        self._uncat += self._cats[cat_name]
        self.option1.setText(self.tr("All ({})").format(self._all))
        self.option2.setText(self.tr("Categorized ({})").format(self._cat))
        self.option3.setText(self.tr("Uncategorized ({})").format(self._uncat))
        
        # update category group title
        del self._cats[cat_name]
        self.cat_box.setTitle(self.tr("Categorys ({})").format(len(self._cats)))
        
        self.deleteCategory.emit(cat_name)
            
  
    @pyqtSlot(QListWidgetItem)  
    def _info_selected(self, item):
        self.cat_list.clearSelection()
        self.infoSelected.emit(self._extract(item.text()))
    
    @pyqtSlot(QListWidgetItem)
    def _cat_selected(self, item):
        self.info_list.clearSelection()
        self.catSelected.emit(self._extract(item.text()))
    
    def _extract(self, ftext):
        return '('.join(ftext.split('(')[:-1]).strip()
        

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
        self.log_view.setObjectName("LogOutputPanel")
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont('Arial', 10))
        main_layout.addWidget(self.log_view)
        
        filter = QLineEdit()
        filter.setObjectName("LogSearchBar")
        filter.setPlaceholderText('Filter...')
        filter.setClearButtonEnabled(True)
        filter.findChild(QAction, "_q_qlineeditclearaction").setIcon(QIcon("resources/icons/cancel.svg"))
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
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
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
                item.setSelected(False)
            
        self.changed_item.emit(filters)
    
    @pyqtSlot(QTreeWidgetItem, int)
    def item_doubleclick(self, item: QTreeWidgetItem, column: int):
        # if is a top level category
        if self.currentItem().childCount() != 0:
            self.currentItem().setSelected(False)
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if self.indexAt(event.pos()).data() == None:
            self.clearSelection()
        return super().mouseDoubleClickEvent(event)
    

class FilterTab(QWidget):    
    def __init__(self):
        super().__init__()
        
        layout  = QVBoxLayout()
        self.setLayout(layout)
        
        data = {
            'Torrents' : [
                ('Active', 'resources/icons/active.svg'),
                ('Inactive', 'resources/icons/inactive.svg'),
                ('Downloading', 'resources/icons/downloading.svg'),
                ('Leeching', 'resources/icons/leeching.svg'),
                ('Seeding', 'resources/icons/seeding.svg'),
                ('Overseeding', 'resources/icons/overseeding.svg'),
                ('Stalling', 'resources/icons/stalling.svg'),
                ('Download Stalling', 'resources/icons/stalling_download.svg'),
                ('Upload Stalling', 'resources/icons/stalling_upload.svg')
            ],
            'Trackers': [
                ('Working', 'resources/icons/working.svg'),
                ('Unreachable', 'resources/icons/unreachable.svg'),
                ('Warning', 'resources/icons/warning.svg'),
                ('Error', 'resources/icons/error.svg')
            ],
            'File Mode': [
                ('Single File', 'resources/icons/file.svg'),
                ('Multi File', 'resources/icons/multifile.svg')
            ],
            'Peer Discovery': [
                ('Centralized', 'resources/icons/centralized.svg'),
                ('Decentralized', 'resources/icons/decentralized.svg'),
                ('Mixed', 'resources/icons/mixed.svg')
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
        
        self.setMovable(True)
        self.setUpdatesEnabled(True)
        self.setObjectName('SidePanel')
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        tab1 = FilterTab()
        tab2 = CategoryTab()
        tab3 = LogTab()
        
        self.tabs = list()
        self.tabs.append([tab1, QIcon('resources/icons/filter.svg'), self.tr("Filters")])
        self.tabs.append([tab2, QIcon('resources/icons/category.svg'), self.tr("Categorys")])
        self.tabs.append([tab3, QIcon('resources/icons/log.svg'), self.tr("Logs")])
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