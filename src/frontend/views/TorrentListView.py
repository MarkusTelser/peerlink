from PyQt6.QtWidgets import (
    QCheckBox, 
    QHeaderView, 
    QTableView, 
    QAbstractItemView, 
    QMenu, 
    QVBoxLayout, 
    QSizePolicy,
)
from PyQt6.QtGui import QAction, QMouseEvent, QIcon
from PyQt6.QtCore import QPoint, Qt, pyqtSlot


class TorrentListView(QTableView):
    def __init__(self, model, column_state):
        super().__init__()
        
        self.model = model
        self.setModel(model)
        
        # generic settings
        self.setSortingEnabled(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        # vertical & horizontal header settings
        self.horizontalHeader().restoreState(column_state)
        self.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setSectionsClickable(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionsMovable(True)
        self.verticalHeader().hide()
        
        # connect model signals to gui
        self.horizontalHeader().customContextMenuRequested.connect(self.show_columnselect)
        
        # create context menu
        self.menu = QMenu(self)
        self.menu.setContentsMargins(0, 0, 0, 0)
        self.menu_resume = QAction('Resume')
        self.menu_resume.setIcon(QIcon('resources/icons/resume.svg'))
        self.menu_pause = QAction('Pause')
        self.menu_pause.setIcon(QIcon('resources/icons/pause.svg'))
        self.menu_stop = QAction('Stop')
        self.menu_stop.setIcon(QIcon('resources/icons/stop.svg'))
        self.menu.addAction(self.menu_resume)
        self.menu.addAction(self.menu_pause)
        self.menu.addAction(self.menu_stop)
        self.menu.addSeparator()
        self.menu_copyname = QAction('Copy name')
        self.menu_copyname.setIcon(QIcon('resources/icons/copy.svg'))
        self.menu_copyhash = QAction('Copy hash')
        self.menu_copyhash.setIcon(QIcon('resources/icons/copy.svg'))
        self.menu_copypath = QAction('Copy path')
        self.menu_copypath.setIcon(QIcon('resources/icons/copy.svg'))
        self.menu.addAction(self.menu_copyname)
        self.menu.addAction(self.menu_copyhash)
        self.menu.addAction(self.menu_copypath)
        self.menu.addSeparator()
        self.menu_open = QAction('Open in file explorer')
        self.menu_open.setIcon(QIcon('resources/icons/files.svg'))
        self.menu_move = QAction('Move')
        self.menu_move.setIcon(QIcon('resources/icons/move.svg'))
        self.menu_delete = QAction('Delete')
        self.menu_delete.setIcon(QIcon('resources/icons/remove.svg'))
        self.menu.addAction(self.menu_open)
        self.menu.addAction(self.menu_move)
        self.menu.addAction(self.menu_delete)
        
        
        # create select column menu
        self.select_menu = QMenu(self)
        menu_layout = QVBoxLayout()
        menu_layout.setSpacing(0)
        self.select_menu.setLayout(menu_layout)
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            if self.rowAt(event.pos().y()) == -1 or len(self.selectedIndexes()) == 0:
                self.menu_resume.setDisabled(True)
                self.menu_pause.setDisabled(True)
                self.menu_stop.setDisabled(True)
                self.menu_move.setDisabled(True)
                self.menu_copyname.setDisabled(True)
                self.menu_copyhash.setDisabled(True)
                self.menu_copypath.setDisabled(True)
                self.menu_delete.setDisabled(True)
            else:
                self.menu_resume.setEnabled(True)
                self.menu_pause.setEnabled(True)
                self.menu_stop.setEnabled(True)
                self.menu_move.setEnabled(True)
                self.menu_copyname.setEnabled(True)
                self.menu_copyhash.setEnabled(True)
                self.menu_copypath.setEnabled(True)
                self.menu_delete.setEnabled(True)
                
            self.menu.popup(self.viewport().mapToGlobal(event.pos()))
            self.menu.exec()
        elif self.rowAt(event.pos().y()) == -1:
            self.clearSelection()
            self.clearFocus()
        else:
            return super().mousePressEvent(event)
    
    
    @pyqtSlot(QPoint)
    def show_columnselect(self, point: QPoint):
        # update select menu, uncheck if column is hidden
        for i in range(self.horizontalHeader().count()):
            column_name = self.model.source_model.headerData(i, Qt.Orientation.Horizontal)
            
            if self.select_menu.layout().itemAt(i) == None:
                check_box = QCheckBox(column_name)
                check_box.setChecked(not self.isColumnHidden(i))
                check_box.clicked.connect(self.update_column)
                if i == 0:
                    check_box.setDisabled(True)
                self.select_menu.layout().addWidget(check_box)
            else:
                state = not self.isColumnHidden(i)
                self.select_menu.layout().itemAt(i).widget().setChecked(state)
        
        self.select_menu.popup(self.viewport().mapToGlobal(point))
        self.select_menu.exec()
        
    @pyqtSlot()
    def update_column(self):
        i = 0
        for child in self.select_menu.children():
            if type(child) == QCheckBox:
                if not child.isChecked() and i != 0:
                    self.hideColumn(i)
                else:
                    self.showColumn(i)
                i += 1

    
    def _update(self, swarm_list):
        indexes = self.selectedIndexes()
        self.model.source_model._update(swarm_list)
        if len(indexes):
            self.selectRow(indexes[0].row())
