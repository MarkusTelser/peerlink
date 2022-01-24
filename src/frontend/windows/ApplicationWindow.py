from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QHBoxLayout,
    QWidget,
    QStackedLayout
)
from PyQt6.QtGui import QGuiApplication, QIcon, QAction, QCloseEvent, QDesktopServices
from PyQt6.QtCore import QRegularExpression, QSize, Qt, QModelIndex, pyqtSlot, QUrl
from os.path import join, exists, dirname, isdir, expanduser
from threading import Thread
from time import sleep
import subprocess
import sys

from src.frontend.ConfigLoader import ConfigLoader
from src.frontend.widgets.StatisticsPanel import StatisticsPanel
from src.frontend.widgets.dialogs import DeleteDialog, FileDialog, MagnetLinkDialog
from src.frontend.widgets.bars import MenuBar, StatusBar, ToolBar
from src.frontend.models.SortFilterProcxyModel import SortFilterProxyModel
from src.frontend.widgets.SidePanel import SidePanel
from src.frontend.widgets.dialogs.AboutDialog import AboutDialog
from src.frontend.windows.PreviewWindow import PreviewWindow

from src.backend.metadata.TorrentParser import TorrentParser
from src.frontend.models.TorrentListModel import TorrentListModel
from src.frontend.views.TorrentListView import TorrentListView
from src.frontend.views.TorrentDetailView import TorrentDetailView
from src.backend.swarm import Swarm

class ApplicationWindow(QMainWindow):
    DONATE_LINK = 'www.google.com'
    BUG_LINK = 'www.google.com'
    THANKS_LINK = 'https://saythanks.io/to/MarkusTelser'
    
    def __init__(self, config_loader):
        super(ApplicationWindow, self).__init__()
        
        self.config_loader = config_loader
        self.current_torrent = None
        self.default_path = join(expanduser('~'), 'Downloads')
        
        self.setWindowTitle("FastPeer - Application Window")
        self.setWindowIcon(QIcon('resources/logo.svg'))
        self.setObjectName('window')
        
        # set screen size
        min_size = QSize(750, 550)
        self.resize(config_loader.win_size)
        self.setMinimumSize(QSize(min_size))
        
        # center in the middle of screen
        if config_loader.win_loc != None:
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
        
        self.update_thread = Thread(target=self._update).start()
        self.show()
        self.load_settings()
    
    def show(self, data=None):
        super().show()
        if data:
            self.appendRowEnd(data)
    
    def addWidgets(self):
        self.menuBar = MenuBar()
        self.setMenuBar(self.menuBar)
        
        self.toolBar = ToolBar()
        self.addToolBar(self.toolBar)
        
        self.statusBar = StatusBar()
        self.setStatusBar(self.statusBar)
        
        self.hori_splitter = QSplitter()
        self.hori_splitter.setOrientation(Qt.Orientation.Horizontal)
        
        self.main_widget = QWidget()
        self.stacked_layout = QStackedLayout()
        self.main_widget.setLayout(self.stacked_layout)
        self.stacked_layout.insertWidget(0, self.hori_splitter)
        self.main_layout.addWidget(self.main_widget)
        
        self.side_panel = SidePanel()
        self.hori_splitter.addWidget(self.side_panel)
        self.side_panel.set_tabspos(self.config_loader.side_tabs)
        
        # vertical splitter for main table, info table
        self.vert_splitter = QSplitter()
        self.vert_splitter.setOrientation(Qt.Orientation.Vertical)
        
        self.hori_splitter.addWidget(self.vert_splitter)
        self.hori_splitter.setCollapsible(1, False)
        
        # add main torrent table model / view
        self.table_model = TorrentListModel()
        self.filter_model = SortFilterProxyModel(self.table_model)
        self.table_view = TorrentListView(self.filter_model)
        self.vert_splitter.addWidget(self.table_view)
        
        # bottom info panel
        self.detail_view = TorrentDetailView()
        self.vert_splitter.addWidget(self.detail_view)
        
        # general statistics
        self.statistics = StatisticsPanel()
        self.stacked_layout.insertWidget(1, self.statistics)
        
        self.hori_splitter.setSizes(self.config_loader.hori_splitter)
        self.vert_splitter.setSizes(self.config_loader.vert_splitter)
        
        # connect signals to controller slots
        self.menuBar.open_file.triggered.connect(self.open_file)
        self.menuBar.open_link.triggered.connect(self.open_magnetlink)
        self.menuBar.create_torrent.triggered.connect(self.create_torrent)
        self.menuBar.import_torrent.triggered.connect(self.import_torrent)
        self.menuBar.exit.triggered.connect(self.close)
        self.menuBar.resume.triggered.connect(self.start_torrent)
        self.menuBar.pause.triggered.connect(self.pause_torrent)
        self.menuBar.move_torrent.triggered.connect(self.move_torrent)
        self.menuBar.open_explorer.triggered.connect(self.open_explorer)
        self.menuBar.remove.triggered.connect(self.delete_torrent)
        self.menuBar.view_menu.aboutToShow.connect(self.update_viewmenu)
        self.menuBar.show_toolbar.triggered.connect(lambda b: self.toolBar.setVisible(b))
        self.menuBar.show_statusbar.triggered.connect(lambda b: self.statusBar.setVisible(b))
        self.menuBar.show_preview.triggered.connect(self.set_open_view)
        self.menuBar.show_panel.triggered.connect(self.show_sidepanel)
        self.menuBar.show_detail.triggered.connect(self.show_detailpanel)
        self.menuBar.panel_tabs.triggered.connect(self.update_paneltabs)
        self.menuBar.detail_tabs.triggered.connect(self.update_detailtabs)
        self.menuBar.help_donate.triggered.connect(lambda: self.open_link(self.DONATE_LINK))
        self.menuBar.help_bug.triggered.connect(lambda: self.open_link(self.BUG_LINK))
        self.menuBar.help_thanks.triggered.connect(lambda: self.open_link(self.THANKS_LINK))
        self.menuBar.help_about.triggered.connect(self.open_aboutdialog)
        
        self.toolBar.open_file.clicked.connect(self.open_file)
        self.toolBar.open_link.clicked.connect(self.open_magnetlink)
        self.toolBar.resume.clicked.connect(self.start_torrent)
        self.toolBar.remove.clicked.connect(self.delete_torrent)
        self.toolBar.remove_all.clicked.connect(self.delete_alltorrents)
        self.toolBar.search_bar.textChanged.connect(self.search_torrents)
        
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
        self.statusBar.speed.clicked.connect(self.open_statistics)
    
    def appendRowEnd(self, dt):
        # dont't add if info_hash is same as in list
        if dt['data'].info_hash in [x.data.info_hash for x in self.table_model.torrent_list]:
            self.show_errorwin("torrent already in list")
            return
        
        s = Swarm(dt['data'], dt['path'])
        self.table_model.torrent_list.append(s)
        
        #'strategy': strategy,
        #'check_hash' : check_hash,
        
        if dt['pad_files']:
            Thread(target=s.file_handler.padd_files).start()
        if dt['start']:
            print('started torrent')
            s.start_thread = Thread(target=s.start)
            s.start_thread.start()
        
        self.open_view = not dt['not_again']
        
        torrent_name = dt['data'].files.name
        readable_len = self.convert_bits(dt['data'].files.length)
        
        self.table_model.data.append([torrent_name, readable_len])
        self.table_model.updatedData.emit()
    
    def convert_bits(self, bits: int):
        if bits < 1000:
            return f"{bits} B"
        if bits / 1024 < 1000:
            return f"{int(round(bits / 1024, 0))} KiB"
        elif bits / (1024 ** 2) < 1000:
            return f"{round(bits / (1024 ** 2), 1)} MiB"
        elif bits  / (1024 ** 3) < 1000:
            return f"{round(bits / (1024 ** 3), 2)} GiB"
        elif bits / (1024 ** 4) < 1000: 
            return f"{round(bits / (1024 ** 4), 2)} TiB"
        elif bits / (1024 ** 5) < 1000:
            return f"{round(bits / (1024 ** 5), 3)} PiB"    
    
    def load_settings(self):
        self.open_view = self.config_loader.open_view
        self.toolBar.setVisible(self.config_loader.show_toolbar)
        self.statusBar.setVisible(self.config_loader.show_statusbar)
    
    def closeEvent(self, event: QCloseEvent):
        # general
        self.config_loader.settings.setValue('win_size', self.size())
        self.config_loader.settings.setValue('win_loc', self.pos())
        self.config_loader.settings.setValue('hori_splitter', self.hori_splitter.sizes())
        self.config_loader.settings.setValue('vert_splitter', self.vert_splitter.sizes())
        self.config_loader.settings.setValue('show_toolbar', str(self.toolBar.isVisible()))
        self.config_loader.settings.setValue('show_statusbar', str(self.statusBar.isVisible()))
        
        # tabs
        self.config_loader.settings.setValue('side_tabs', self.side_panel.tabspos())
        self.config_loader.settings.setValue('open_view', self.open_view)
        
        event.accept()
    
    def show_errorwin(self, error_txt):
        error_msg = QMessageBox(self)
        error_msg.setWindowIcon(QIcon('resources/warning.svg'))
        error_msg.setWindowTitle("Error")
        error_msg.setText(error_txt)
        error_msg.show()
    
    @pyqtSlot(QModelIndex)
    def select_torrent(self, index: QModelIndex):
        data = self.table_model.torrent_list[index.row()]
        self.detail_view._update(data)
    
    @pyqtSlot()
    def start_torrent(self):
        pass
    
    @pyqtSlot()
    def pause_torrent(self):
        pass
    
    @pyqtSlot()
    def move_torrent(self):
        pass
    
    @pyqtSlot()
    def open_link(self, link):
        QDesktopServices.openUrl(QUrl(link))
    
    @pyqtSlot(bool)
    def set_open_view(self, status: bool):
        self.open_view = status
    
    @pyqtSlot()
    def open_file(self):
        dialog = FileDialog()
        
        print(self.open_view)
        if dialog.exec():
            file_paths = dialog.selectedFiles()
            for file_path in file_paths:
                data = TorrentParser.parse_filepath(file_path)
                if self.open_view:
                    window = PreviewWindow(self)
                    window.add_data.connect(self.appendRowEnd)
                    window.show(data)
                else:
                    data = {
                        'path': self.default_path,
                        'strategy': 'rarest-first',
                        'start': False,
                        'check_hash' : True,
                        'pad_files' : False,
                        'not_again' : True,
                        'data' : data
                    }
                    self.appendRowEnd(data)
    
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
    def open_statistics(self):
        if self.stacked_layout.currentIndex() == 0:
            self.stacked_layout.setCurrentIndex(1)
        else:
            self.stacked_layout.setCurrentIndex(0)
    
    @pyqtSlot(bool)
    def show_sidepanel(self, checked: bool):
        if not checked:
            self.hori_splitter.setSizes([0, -1])
        elif self.hori_splitter.sizes()[0] == 0:
            print('update panel')
            min_width = self.side_panel.sizeHint().width()
            fwidth = self.hori_splitter.width()
            print(self.hori_splitter.sizes())
            self.hori_splitter.setSizes([min_width, fwidth - min_width])
    
    @pyqtSlot(bool)
    def show_detailpanel(self, checked: bool):
        if not checked:
            self.vert_splitter.setSizes([-1, 0])
        elif self.vert_splitter.sizes()[1] == 0:
            fsize = self.vert_splitter.size().height()
            self.vert_splitter.setSizes([int(fsize * 0.7),int(fsize * 0.3)])
    
    @pyqtSlot()
    def update_viewmenu(self):
        self.menuBar.show_toolbar.setChecked(self.toolBar.isVisible())
        self.menuBar.show_statusbar.setChecked(self.statusBar.isVisible())
        self.menuBar.show_preview.setChecked(self.open_view)
        
        panel_state = self.hori_splitter.sizes()[0] != 0
        self.menuBar.show_panel.setChecked(panel_state)
        detail_state = self.vert_splitter.sizes()[1] != 0 
        self.menuBar.show_detail.setChecked(detail_state)
        
        self.menuBar.panel_tabs.clear()
        for i in range(self.side_panel.count()):
            action = self.menuBar.panel_tabs.addAction(self.side_panel.tabText(i))
            action.setCheckable(True)
            action.setChecked(self.side_panel.isTabVisible(i))
        
        self.menuBar.detail_tabs.clear()
        for i in range(self.detail_view.count()):
            action = self.menuBar.detail_tabs.addAction(self.detail_view.tabText(i))
            action.setCheckable(True)
            action.setChecked(self.detail_view.isTabVisible(i))
        
        self.menuBar.repaint()
    
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
            data = self.table_model.torrent_list[index.row()]
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
        
        index = indexes[0].row()
        txt = self.table_model.torrent_list[index].data.files.name
        clipboard = QApplication.clipboard()
        clipboard.clear(mode=clipboard.Mode.Clipboard)
        clipboard.setText(txt ,mode=clipboard.Mode.Clipboard)
    
    @pyqtSlot()
    def copy_hash(self):
        indexes = self.table_view.selectedIndexes()
        if len(indexes) == 0:
            return
        
        index = indexes[0].row()
        txt = self.table_model.torrent_list[index].data.info_hash_hex
        clipboard = QApplication.clipboard()
        clipboard.clear(mode=clipboard.Mode.Clipboard)
        clipboard.setText(txt ,mode=clipboard.Mode.Clipboard)
    
    @pyqtSlot()
    def copy_path(self):
        indexes = self.table_view.selectedIndexes()
        if len(indexes) == 0:
            return
        
        index = indexes[0].row()
        root_path = self.table_model.torrent_list[index].data.files.name
        txt = join(self.table_model.torrent_list[index].path, root_path) 
        clipboard = QApplication.clipboard()
        clipboard.clear(mode=clipboard.Mode.Clipboard)
        clipboard.setText(txt ,mode=clipboard.Mode.Clipboard)
    
    @pyqtSlot()
    def open_explorer(self):
        indexes = self.table_view.selectedIndexes()
        if len(indexes) == 0:
            full_path = self.default_path
        else:
            index = indexes[0].row()
            rel_path = self.table_model.torrent_list[index].data.files.name
            full_path = join(self.table_model.torrent_list[index].path, rel_path)
            if not isdir(full_path):
                full_path = dirname(full_path)
        
        if not exists(full_path):
            self.show_errorwin("path doesn't exist")
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
    
    @pyqtSlot()
    def delete_torrent(self):
        indexes = self.table_view.selectedIndexes()
        if len(indexes) == 0:
            self.show_errorwin("no torrent selected")
            return  

        dialog = DeleteDialog()
        if dialog.exec():
            index = indexes[0]
            if dialog.checkbox.isChecked():
                self.table_model.torrent_list[index.row()].file_handler.remove_files()
            
            del self.table_model.torrent_list[index.row()]
            del self.table_model.data[index.row()]
            self.table_model.updatedData.emit()
            self._update()
    
    @pyqtSlot()
    def delete_alltorrents(self):
        if self.table_model.rowCount() == 0:
            self.show_errorwin("torrent list is empty")
            return
        
        dialog = DeleteDialog(all_torrents=True)
        if dialog.exec():
            if dialog.checkbox.isChecked():
                for row in range(self.table_model.rowCount()):
                    self.table_model.torrent_list[row].file_handler.remove_files()
                
                self.table_model.torrent_list = list()
                self.table_model.data = list()
                self.table_model.updatedData.emit()
                self.detail_view._clear()
                
    @pyqtSlot(str)
    def search_torrents(self, search: str):
        reg = QRegularExpression(search, QRegularExpression.PatternOption.CaseInsensitiveOption)
        self.filter_model.setFilterRegularExpression(reg)
    
    @pyqtSlot(list)
    def filter_torrents(self, filters: list):
        self.filter_model.filters = filters
        self.filter_model.invalidateFilter()
    
    def _update(self):
        # update detail window, if it is open
        if self.vert_splitter.sizes()[1] > 0:
            indexes = self.table_view.selectedIndexes()
            if len(indexes) == 0:
                self.detail_view._clear()
            else:
                data = self.table_model.torrent_list[indexes[0]]
                self.detail_view._update(data)
        
        sleep(1)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    conf = ConfigLoader()
    
    window = ApplicationWindow(conf)
    window.show()

    sys.exit(app.exec())