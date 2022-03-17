from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSplitter,
    QHBoxLayout,
    QWidget
)
from PyQt6.QtGui import (
    QGuiApplication, 
    QIcon, 
    QAction,
    QCloseEvent, 
    QDesktopServices, 
    QDragEnterEvent, 
    QDropEvent,
    QKeySequence
)
from PyQt6.QtCore import (
    QRegularExpression, 
    QSize, 
    Qt, 
    QModelIndex, 
    pyqtSlot, 
    QUrl, 
    QTimer
)
from os.path import join, exists, dirname, isdir
from threading import Thread
import subprocess
import sys

from src.frontend.models.TorrentListModel import TorrentListModel
from src.frontend.utils.utils import showError
from src.frontend.views.TorrentListView import TorrentListView
from src.frontend.views.TorrentDetailView import TorrentDetailView
from src.frontend.utils.AppDataLoader import AppDataLoader
from src.frontend.utils.ConfigLoader import ConfigLoader
from src.frontend.widgets.dialogs import DeleteDialog, FileDialog, MagnetLinkDialog
from src.frontend.widgets.bars import MenuBar, StatusBar, ToolBar
from src.frontend.models.SortFilterProcxyModel import SortFilterProxyModel
from src.frontend.widgets.SidePanel import SidePanel
from src.frontend.widgets.dialogs.AboutDialog import AboutDialog
from src.frontend.windows.DiagramWindow import DiagramWindow
from src.frontend.windows.IpFilterWindow import IpFilterWindow
from src.frontend.windows.PreviewWindow import PreviewWindow

from src.backend.swarm import Swarm
from src.backend.Session import Session
from src.backend.metadata.Bencoder import bencode
from src.backend.metadata import TorrentParser, MagnetParser
from src.frontend.windows.SpeedLimitWindow import SpeedLimitWindow
from src.frontend.windows.StatisticsWindow import StatisticsWindow


class ApplicationWindow(QMainWindow):
    UPDATE_DELAY = 1500
    DONATE_LINK = 'www.google.com'
    BUG_LINK = 'https://github.com/MarkusTelser/peerlink/issues'
    THANKS_LINK = 'https://saythanks.io/to/MarkusTelser'
    
    def __init__(self, config_loader):
        super(ApplicationWindow, self).__init__()
        
        self.session = Session()
        self.config_loader = config_loader
        self.appdata_loader = AppDataLoader()
        self.show_launch = self.config_loader.show_launch
        self.open_preview = self.config_loader.open_preview
        self.current_torrent = None
        
        self.setAcceptDrops(True)
        self.setWindowTitle("Application Window - PeerLink")
        self.setWindowIcon(QIcon('resources/logo.svg'))
        self.setObjectName('window')
        
        # set screen size
        min_size = QSize(800, 600)
        self.resize(config_loader.win_size)
        self.setMinimumSize(QSize(min_size))
        
        # center in the middle of screen
        if not config_loader.win_loc.isNull():
            self.move(config_loader.win_loc)
        else:
            qtRectangle = self.frameGeometry()
            centerPoint = QGuiApplication.primaryScreen().availableGeometry().center()
            qtRectangle.moveCenter(centerPoint)
            self.move(qtRectangle.topLeft())
        
        self.central_widget = QWidget()
        self.main_layout = QHBoxLayout()
        
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.addWidgets()
        
        timer = QTimer(self)
        timer.timeout.connect(self._update)
        timer.start(self.UPDATE_DELAY)
        
        super().show()
    
    def addWidgets(self):
        self.menu_bar = MenuBar()
        self.setMenuBar(self.menu_bar)
        
        self.tool_bar = ToolBar()
        self.tool_bar.setVisible(self.config_loader.show_toolbar)
        self.addToolBar(self.tool_bar)
        
        self.status_bar = StatusBar()
        self.status_bar.setVisible(self.config_loader.show_statusbar)
        self.setStatusBar(self.status_bar)
        
        self.hori_splitter = QSplitter()
        self.hori_splitter.setOrientation(Qt.Orientation.Horizontal)
        
        
        self.main_layout.addWidget(self.hori_splitter)
        
        self.side_panel = SidePanel(self.config_loader.side_tabs)
        if self.side_panel.count() > 0:
            self.side_panel.setCurrentIndex(self.config_loader.side_current)
        self.side_panel.tabs[1][0].setCategorys(self.config_loader.categorys)
        self.hori_splitter.addWidget(self.side_panel)
        
        # vertical splitter for main table, info table
        self.vert_splitter = QSplitter()
        self.vert_splitter.setOrientation(Qt.Orientation.Vertical)
        
        self.hori_splitter.addWidget(self.vert_splitter)
        self.hori_splitter.setCollapsible(1, False)
        
        # add main torrent table model / view
        self.table_model = TorrentListModel()
        self.filter_model = SortFilterProxyModel(self.table_model, self.session)
        self.table_view = TorrentListView(self.filter_model, self.config_loader.table_tabs)
        self.vert_splitter.addWidget(self.table_view)
        
        # bottom info panel
        self.detail_view = TorrentDetailView(self.config_loader.detail_tabs)
        if self.detail_view.count() > 0:
            self.detail_view.setCurrentIndex(self.config_loader.detail_current)
        self.vert_splitter.addWidget(self.detail_view)
        
        self.vert_splitter.setSizes(self.config_loader.vert_splitter)
        self.hori_splitter.setSizes(self.config_loader.hori_splitter)
        
        # connect signals to controller slots
        self.menu_bar.open_file.triggered.connect(self.open_file)
        self.menu_bar.open_link.triggered.connect(self.open_magnetlink)
        self.menu_bar.create_torrent.triggered.connect(self.create_torrent)
        self.menu_bar.import_torrent.triggered.connect(self.import_torrent)
        self.menu_bar.exit.triggered.connect(self.close)
        self.menu_bar.edit_resume.triggered.connect(self.start_torrent)
        self.menu_bar.edit_pause.triggered.connect(self.pause_torrent)
        self.menu_bar.edit_move.triggered.connect(self.move_torrent)
        self.menu_bar.edit_copy_name.triggered.connect(self.copy_name)
        self.menu_bar.edit_copy_hash.triggered.connect(self.copy_hash)
        self.menu_bar.edit_copy_path.triggered.connect(self.copy_path)
        self.menu_bar.edit_open.triggered.connect(self.open_explorer)
        self.menu_bar.edit_remove.triggered.connect(self.delete_torrent)
        self.menu_bar.show_toolbar.triggered.connect(lambda b: self.tool_bar.setVisible(b))
        self.menu_bar.show_statusbar.triggered.connect(lambda b: self.status_bar.setVisible(b))
        self.menu_bar.show_launch.triggered.connect(lambda b: self.set_openlaunch(b))
        self.menu_bar.show_preview.triggered.connect(lambda b: self.set_openpreview(b))
        self.menu_bar.show_panel.triggered.connect(self.show_sidepanel)
        self.menu_bar.show_detail.triggered.connect(self.show_detailpanel)
        self.menu_bar.panel_tabs.triggered.connect(self.update_paneltabs)
        self.menu_bar.detail_tabs.triggered.connect(self.update_detailtabs)
        self.menu_bar.tools_speed.triggered.connect(self.open_diagram)
        self.menu_bar.tools_statistics.triggered.connect(self.open_statistics)
        self.menu_bar.tools_filter.triggered.connect(self.open_ipfilter)
        self.menu_bar.tools_limit.triggered.connect(self.open_speedlimit)
        self.menu_bar.help_donate.triggered.connect(lambda: self.open_link(self.DONATE_LINK))
        self.menu_bar.help_bug.triggered.connect(lambda: self.open_link(self.BUG_LINK))
        self.menu_bar.help_thanks.triggered.connect(lambda: self.open_link(self.THANKS_LINK))
        self.menu_bar.help_about.triggered.connect(self.open_aboutdialog)
        self.menu_bar.edit_menu.aboutToShow.connect(self.update_editmenu)
        self.menu_bar.view_menu.aboutToShow.connect(self.update_viewmenu)

        self.tool_bar.open_file.clicked.connect(self.open_file)
        self.tool_bar.open_link.clicked.connect(self.open_magnetlink)
        self.tool_bar.resume.clicked.connect(self.start_torrent)
        self.tool_bar.remove.clicked.connect(self.delete_torrent)
        self.tool_bar.remove_all.clicked.connect(self.delete_alltorrents)
        self.tool_bar.search_bar.textChanged.connect(self.search_torrents)
        
        self.table_view.clicked.connect(self.select_torrent)
        self.table_view.doubleClicked.connect(self.doubleclick_torrent)
        self.table_view.menu_resume.triggered.connect(self.start_torrent)
        self.table_view.menu_pause.triggered.connect(self.pause_torrent)
        self.table_view.menu_move.triggered.connect(self.move_torrent)
        self.table_view.menu_copyname.triggered.connect(self.copy_name)
        self.table_view.menu_copyhash.triggered.connect(self.copy_hash)
        self.table_view.menu_copypath.triggered.connect(self.copy_path)
        self.table_view.menu_open.triggered.connect(self.open_explorer)
        self.table_view.menu_delete.triggered.connect(self.delete_torrent)
        
        self.side_panel.tabs[0][0].filter_tree.changed_item.connect(self.filter_torrents)
        self.side_panel.tabs[1][0].infoSelected.connect(self.filter_infocat)
        self.side_panel.tabs[1][0].catSelected.connect(self.filter_category)
        self.side_panel.tabs[1][0].newCategory.connect(self.add_category)
        self.side_panel.tabs[1][0].renameCategory.connect(self.rename_category)
        self.side_panel.tabs[1][0].deleteCategory.connect(self.delete_category)
        
        self.status_bar.speed.clicked.connect(self.open_diagram)
        self.status_bar.statistics.clicked.connect(self.open_statistics)
    
    def show(self, data=None):
        if data:
            self.appendRowEnd(data) 
    
    @pyqtSlot(QModelIndex)
    def select_torrent(self, index: QModelIndex):
        real_index = index.siblingAtColumn(0).data(Qt.ItemDataRole.InitialSortOrderRole + 69)
        data = self.session.swarm_list[real_index] # self.table_model.torrent_list[real_index]
        self.detail_view._update(data)
    
    @pyqtSlot()
    def start_torrent(self):
        indexes = self.table_view.selectedIndexes()
        if len(indexes) == 0:
            return
        real_index = indexes[0].siblingAtColumn(0).data(Qt.ItemDataRole.InitialSortOrderRole + 69)
        self.session.resume(real_index) #Thread(target=self.table_model.torrent_list[real_index].start).start()
    
    @pyqtSlot()
    def pause_torrent(self):
        indexes = self.table_view.selectedIndexes()
        if len(indexes) == 0:
            return
        real_index = indexes[0].siblingAtColumn(0).data(Qt.ItemDataRole.InitialSortOrderRole + 69)
        self.session.stop(real_index) #self.table_model.torrent_list[real_index].pause()
    
    @pyqtSlot()
    def move_torrent(self):
        pass
    
    @pyqtSlot()
    def open_link(self, link):
        QDesktopServices.openUrl(QUrl(link))
    
    @pyqtSlot(bool)
    def set_openpreview(self, b):
        self.open_preview = b
    
    @pyqtSlot(bool)
    def set_openlaunch(self, b):
        self.show_launch = b
    
    @pyqtSlot()
    def open_file(self):
        dialog = FileDialog(self)
        
        if dialog.exec():
            file_paths = dialog.selectedFiles()
            self._open_file(file_paths)
    
    @pyqtSlot()
    def open_magnetlink(self):
        dialog = MagnetLinkDialog()
        
        if dialog.exec():
            magnet_link = dialog.text_box.text()
    
    @pyqtSlot()
    def open_aboutdialog(self):
        dialog = AboutDialog()
        dialog.exec()
    
    @pyqtSlot()
    def create_torrent(self):
        pass
    
    @pyqtSlot()
    def import_torrent(self):
        pass
    
    @pyqtSlot()
    def open_ipfilter(self):
        window = IpFilterWindow(self)
        window.show()
    
    @pyqtSlot()
    def open_speedlimit(self):
        window = SpeedLimitWindow(self)
        window.show()
    
    @pyqtSlot()
    def open_diagram(self):
        window = DiagramWindow(self)
        window.show()
        
    @pyqtSlot()
    def open_statistics(self):
        window = StatisticsWindow(self)
        window.show()
    
    @pyqtSlot(bool)
    def show_sidepanel(self, checked: bool):
        if not checked:
            self.hori_splitter.setSizes([0, -1])
        elif self.hori_splitter.sizes()[0] == 0:
            min_width = self.side_panel.sizeHint().width()
            fwidth = self.hori_splitter.width()
            self.hori_splitter.setSizes([min_width, fwidth - min_width])
    
    @pyqtSlot(bool)
    def show_detailpanel(self, checked: bool):
        if not checked:
            self.vert_splitter.setSizes([-1, 0])
        elif self.vert_splitter.sizes()[1] == 0:
            fsize = self.vert_splitter.size().height()
            self.vert_splitter.setSizes([int(fsize * 0.7),int(fsize * 0.3)])
    
    @pyqtSlot()
    def update_editmenu(self):
        if len(self.table_view.selectedIndexes()) == 0:
            self.menu_bar.edit_resume.setDisabled(True)
            self.menu_bar.edit_pause.setDisabled(True)
            self.menu_bar.edit_move.setDisabled(True)
            self.menu_bar.edit_copy_name.setDisabled(True)
            self.menu_bar.edit_copy_hash.setDisabled(True)
            self.menu_bar.edit_copy_path.setDisabled(True)
            self.menu_bar.edit_remove.setDisabled(True)
        else:
            self.menu_bar.edit_resume.setEnabled(True)
            self.menu_bar.edit_pause.setEnabled(True)
            self.menu_bar.edit_move.setEnabled(True)
            self.menu_bar.edit_copy_name.setEnabled(True)
            self.menu_bar.edit_copy_hash.setEnabled(True)
            self.menu_bar.edit_copy_path.setEnabled(True)
            self.menu_bar.edit_remove.setEnabled(True)
    
    @pyqtSlot()
    def update_viewmenu(self):
        self.menu_bar.show_toolbar.setChecked(self.tool_bar.isVisible())
        self.menu_bar.show_statusbar.setChecked(self.status_bar.isVisible())
        self.menu_bar.show_launch.setChecked(self.show_launch)
        self.menu_bar.show_preview.setChecked(self.open_preview)
        
        panel_state = self.hori_splitter.sizes()[0] != 0
        self.menu_bar.show_panel.setChecked(panel_state)
        detail_state = self.vert_splitter.sizes()[1] != 0 
        self.menu_bar.show_detail.setChecked(detail_state)
        
        self.menu_bar.panel_tabs.clear()
        for i in range(self.side_panel.count()):
            action = self.menu_bar.panel_tabs.addAction(self.side_panel.tabText(i))
            action.setCheckable(True)
            action.setChecked(self.side_panel.isTabVisible(i))
        
        self.menu_bar.detail_tabs.clear()
        for i in range(self.detail_view.count()):
            action = self.menu_bar.detail_tabs.addAction(self.detail_view.tabText(i))
            action.setCheckable(True)
            action.setChecked(self.detail_view.isTabVisible(i))
        
        self.menu_bar.repaint()
    
    @pyqtSlot(QAction)
    def update_paneltabs(self, action: QAction):
        for i in range(self.side_panel.count()):
            if self.side_panel.tabText(i) == action.text():
                self.side_panel.setTabVisible(i, action.isChecked())
    
    @pyqtSlot(QAction)
    def update_detailtabs(self, action: QAction):
        for i in range(self.detail_view.count()):
            if self.detail_view.tabText(i) == action.text():
                self.detail_view.setTabVisible(i, action.isChecked())
    
    @pyqtSlot(QModelIndex)
    def doubleclick_torrent(self, index: QModelIndex):
        if self.vert_splitter.sizes()[1] == 0:
            data = self.session.swarm_list[index.row()] #self.table_model.torrent_list[index.row()]
            self.detail_view._update(data)
            fsize = self.vert_splitter.size().height()
            self.vert_splitter.setSizes([int(fsize * 0.7),int(fsize * 0.3)])
        elif self.current_torrent == index.row():
            self.vert_splitter.setSizes([1,0])
        self.current_torrent = index.row()
    
    @pyqtSlot()
    def copy_name(self):
        indexes = self.table_view.selectedIndexes()
        if len(indexes) == 0:
            return
        index = indexes[0].siblingAtColumn(0).data(Qt.ItemDataRole.InitialSortOrderRole + 69)
        
        txt = self.session.swarm_list[index].data.files.name #self.table_model.torrent_list[index].data.files.name
        clipboard = QApplication.clipboard()
        clipboard.clear(mode=clipboard.Mode.Clipboard)
        clipboard.setText(txt ,mode=clipboard.Mode.Clipboard)
    
    @pyqtSlot()
    def copy_hash(self):
        indexes = self.table_view.selectedIndexes()
        if len(indexes) == 0:
            return
        index = indexes[0].siblingAtColumn(0).data(Qt.ItemDataRole.InitialSortOrderRole + 69)
        
        txt = self.session.swarm_list[index].data.info_hash_hex #self.table_model.torrent_list[index].data.info_hash_hex
        clipboard = QApplication.clipboard()
        clipboard.clear(mode=clipboard.Mode.Clipboard)
        clipboard.setText(txt ,mode=clipboard.Mode.Clipboard)
    
    @pyqtSlot()
    def copy_path(self):
        indexes = self.table_view.selectedIndexes()
        if len(indexes) == 0:
            return
        index = indexes[0].siblingAtColumn(0).data(Qt.ItemDataRole.InitialSortOrderRole + 69)
        
        root_path = self.session.swarm_list[index].data.files.name #self.table_model.torrent_list[index].data.files.name
        txt = join(self.session.swarm_list[index].path, root_path) #self.table_model.torrent_list[index].path
        clipboard = QApplication.clipboard()
        clipboard.clear(mode=clipboard.Mode.Clipboard)
        clipboard.setText(txt ,mode=clipboard.Mode.Clipboard)
    
    @pyqtSlot()
    def open_explorer(self):
        indexes = self.table_view.selectedIndexes()
        if len(indexes) == 0:
            full_path = self.config_loader.default_path
        else:
            index = indexes[0].siblingAtColumn(0).data(Qt.ItemDataRole.InitialSortOrderRole + 69)
            rel_path = self.session.swarm_list[index].data.files.name #self.table_model.torrent_list[index].data.files.name
            full_path = join(self.session.swarm_list[index].path, rel_path) #self.table_model.torrent_list[index].path
            if not isdir(full_path):
                full_path = dirname(full_path)
        
        if not exists(full_path):
            showError('Path doesnt exist!', self)
            return
        
        if not isdir(full_path):
            full_path = dirname(full_path)
        if sys.platform == 'darwin':
            subprocess.check_call(['open', '--', full_path])
        elif sys.platform == 'linux2':
            subprocess.check_call(['xdg-open', '--', full_path])
        elif sys.platform == 'linux':
            subprocess.check_call(['xdg-open', full_path])
        elif sys.platform == 'win32':
            subprocess.check_call(['explorer', full_path])
        else:
            pass
            # TODO log other platforms that are not supported
    
    def _delete_torrent(self, index, remove_files):
        if remove_files:
            self.session.swarm_list[index].file_handler.remove_files() #self.table_model.torrent_list[index].file_handler.remove_files()
        
        # remove backed up meta files
        backup_name = self.session.swarm_list[index].backup_name #self.table_model.torrent_list[index].backup_name
        self.appdata_loader.remove_torrent(backup_name)
        
        # remove from category
        category_name = self.session.swarm_list[index].category #self.table_model.torrent_list[index].category
        self.side_panel.tabs[1][0].remove(category_name)
        
        del self.session.swarm_list[index] 
        self.table_model.remove(index)
        self.table_model._update(self.session.swarm_list)

    
    @pyqtSlot()
    def delete_torrent(self):
        indexes = self.table_view.selectedIndexes()
        if len(indexes) == 0:
            ('Error', 'No torrent selected', self)
            return  
        
        dialog = DeleteDialog()
        if dialog.exec():
            real_index = indexes[0].siblingAtColumn(0).data(Qt.ItemDataRole.InitialSortOrderRole + 69)
            print(indexes[0].siblingAtColumn(0).data())
            self._delete_torrent(real_index, dialog.checkbox.isChecked())
            self._update()
    
    @pyqtSlot()
    def delete_alltorrents(self):
        if len(self.session.swarm_list) == 0: #self.table_model.rowCount() == 0:
            showError('Torrent list is empty', self)
            return
        
        dialog = DeleteDialog(all_torrents=True)
        if dialog.exec():
            if dialog.checkbox.isChecked():
                for row in reversed(range(len(self.session.swarm_list))): # self.table_model.rowCount()
                    self._delete_torrent(row, dialog.checkbox.isChecked())
                self._update()
                
    @pyqtSlot(str)
    def search_torrents(self, search: str):
        reg = QRegularExpression(search, QRegularExpression.PatternOption.CaseInsensitiveOption)
        self.filter_model.setFilterRegularExpression(reg)
    
    @pyqtSlot(str)
    def filter_infocat(self, filter: str):
        self.filter_model.cat_filter = ''
        self.filter_model.cat_info = filter
        self.filter_model.invalidateFilter()
    
    @pyqtSlot(str)
    def filter_category(self, filter: str):
        self.filter_model.cat_info = ''
        self.filter_model.cat_filter = filter
        self.filter_model.invalidateFilter()
    
    @pyqtSlot(list)
    def filter_torrents(self, filters: list):
        self.filter_model.filters = filters
        self.filter_model.invalidateFilter()
    
    @pyqtSlot(str)
    def add_category(self, category):
        self.config_loader.categorys.append(category)
    
    @pyqtSlot(str, str)
    def rename_category(self, old_cat, new_cat):
        self.config_loader.categorys.remove(old_cat)
        self.config_loader.categorys.append(new_cat)
        for torrent in self.session.swarm_list: #self.table_model.torrent_list:
            if torrent.category == old_cat:
                torrent.category = new_cat
    
    @pyqtSlot(str)
    def delete_category(self, category):
        self.config_loader.categorys.remove(category)
        for torrent in self.session.swarm_list: #self.table_model.torrent_list:
            if torrent.category == category:
                torrent.category = ''
    

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Paste):
            try:
                magnet_link = QApplication.clipboard().text()
                magnet = MagnetParser.parse(magnet_link)
                window = PreviewWindow(self.config_loader, self)
                window.add_data.connect(self.appendRowEnd)
                window.show(magnet)
            except Exception as e:
                pass
        super(ApplicationWindow, self).keyPressEvent(event)

    def appendRowEnd(self, data, extras={}):
        # dont't add if info_hash is same as in list
        if data.info_hash in [x.data.info_hash for x in self.session.swarm_list]: # self.table_model.torrent_list
            showError('Torrent is already in list', self)
            return
        
        # save data to config
        if 'start' in extras:
            self.config_loader.auto_start = extras['start']
        if 'check_hashes' in extras:
            self.config_loader.check_hashes = extras['check_hash']
        if 'pad_files' in extras:
            self.config_loader.padd_files = extras['pad_files']
        if 'size' in extras:
            self.config_loader.preview_size = extras['size']
        if 'location' in extras:
            self.config_loader.preview_location = extras['location']
        if 'default_path' in extras:
            self.config_loader.default_path = extras['path']
        if 'category' in extras and len(extras['category']) > 0 and extras['category'] not in self.config_loader.categorys:
            self.config_loader.categorys.append(extras['category'])
        if 'default_category' in extras and extras['default_category']:
            self.config_loader.default_category = extras['category']
        if 'not_again' in extras:
            self.open_preview = extras['not_again']
        
        # set default values if not in extras
        if 'start' not in extras:
            extras['start'] = self.config_loader.auto_start
        if 'path' not in extras:
            extras['path'] = self.config_loader.default_path
        if 'category' not in extras:
            extras['category'] = self.config_loader.default_category
        if 'startegy' not in extras:
            pass
        if 'check_hash' not in extras:
            extras['check_hash'] = self.config_loader.check_hashes
        if 'pad_files' not in extras:
            extras['pad_files'] = self.config_loader.padd_files
        
        swarm = Swarm()
        swarm.set_meta_data(data, extras['path'])

        # add into backup files
        swarm.category = extras['category']
        swarm.backup_name = self.appdata_loader.backup_torrent(data.raw_data)
        
        # actions if key true
        if extras['start']:
            swarm.start()
        """
        if extras['startegy']:
            pass
        """
        if extras['check_hash']:
            pass
        if extras['pad_files']:
            Thread(target=swarm.file_handler.padd_files).start()
        
        self.session.swarm_list.append(swarm) #self.table_model.append(swarm)
        self.side_panel.tabs[1][0].append(swarm)
        self.table_model.append(swarm)
    
    def load_torrents(self, torrent_list):
        for torrent_data, extras in torrent_list:        
            swarm = Swarm()
            swarm.set_meta_data(torrent_data, extras['save_path'])
            swarm.category = extras['category']
            swarm.backup_name = extras['backup_name']
            swarm.start_date = extras['start_date']
            swarm.finish_date = extras['finish_date']
            
            self.session.swarm_list.append(swarm) #self.table_model.append(swarm)
            self.side_panel.tabs[1][0].append(swarm)
            self.table_model.append(swarm)
    
    def save_torrents(self):
        for torrent in self.session.swarm_list: #self.table_model.torrent_list:
            save_data = {
                'save_path': torrent.path,
                'category': torrent.category,
                'backup_name': torrent.backup_name,
                'start_date': torrent.start_date   ,
                'finish_date': torrent.finish_date
            }
            bdata = bencode(save_data)
            f = open(join(f'/home/carlos/.local/share/peerlink/torrents/{torrent.backup_name}.ben'), 'wb')
            f.write(bdata)
            f.close()
            
    def dragEnterEvent(self, event: QDragEnterEvent):
        for url in event.mimeData().urls():
            if url.isLocalFile() and url.path().endswith('.torrent'):
                event.accept()
                return
    
    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            if url.isLocalFile() and url.path().endswith('.torrent'):
                self._open_file([url.path()])
    
    def closeEvent(self, event: QCloseEvent):
        # general
        self.config_loader.settings.setValue('win_size', self.size())
        self.config_loader.settings.setValue('win_loc', self.pos())
        self.config_loader.settings.setValue('hori_splitter', self.hori_splitter.sizes())
        self.config_loader.settings.setValue('vert_splitter', self.vert_splitter.sizes())
        self.config_loader.settings.setValue('show_toolbar', self.tool_bar.isVisible())
        self.config_loader.settings.setValue('show_statusbar', self.status_bar.isVisible())
        self.config_loader.settings.setValue('side_current', self.side_panel.currentIndex())
        self.config_loader.settings.setValue('side_tabs', self.side_panel.tabspos())
        self.config_loader.settings.setValue('detail_current', self.detail_view.currentIndex())
        self.config_loader.settings.setValue('detail_tabs', self.detail_view.tabspos())
        self.config_loader.settings.setValue('table_tabs', self.table_view.horizontalHeader().saveState())
        self.config_loader.settings.setValue('show_launch', self.show_launch)
        
        # Preview Window
        self.config_loader.settings.beginGroup('PreviewWindow')
        self.config_loader.settings.setValue('preview_size', self.config_loader.preview_size)
        self.config_loader.settings.setValue('preview_location', self.config_loader.preview_location)
        self.config_loader.settings.setValue('open_preview', self.open_preview)
        self.config_loader.settings.setValue('default_path', self.config_loader.default_path)
        self.config_loader.settings.setValue('categorys', self.config_loader.categorys)
        self.config_loader.settings.setValue('default_category', self.config_loader.default_category)
        self.config_loader.settings.setValue('auto_start', self.config_loader.auto_start)
        self.config_loader.settings.setValue('check_hashes', self.config_loader.check_hashes)
        self.config_loader.settings.setValue('padd_files', self.config_loader.padd_files)
        self.config_loader.settings.endGroup()
        
        self.save_torrents()
        
        event.accept()
    
    def _open_file(self, file_paths):
        for file_path in file_paths:
            data = TorrentParser.parse_filepath(file_path)
            if self.open_preview:
                window = PreviewWindow(self.config_loader, self)
                window.add_data.connect(self.appendRowEnd)
                window.show(data)
            else:
                self.appendRowEnd(data)
    
    def _update(self):
        # update detail window, if it is open
        if self.vert_splitter.sizes()[1] > 0:
            indexes = self.table_view.selectedIndexes()
            if len(indexes) == 0:
                self.detail_view._clear()
            else:
                real_index = indexes[0].siblingAtColumn(0).data(Qt.ItemDataRole.InitialSortOrderRole + 69)
                data = self.session.swarm_list[real_index] #self.table_model.torrent_list[real_index]
                self.detail_view._update(data)
        
        self.table_view._update(self.session.swarm_list)
        self.status_bar._update(self.session)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    conf = ConfigLoader()
    
    window = ApplicationWindow(conf)
    window.show()

    sys.exit(app.exec())