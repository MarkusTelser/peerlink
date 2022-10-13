from PyQt6.QtWidgets import (
    QHeaderView, 
    QTabWidget, 
    QTableView, 
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout,
    QProgressBar, 
    QGroupBox,
    QLabel,
    QGridLayout,
    QScrollArea,
    QAbstractItemView,
    QComboBox,
    QSizePolicy
)
from PyQt6.QtGui import (
    QColor, 
    QIcon, 
    QPainter, 
    QStandardItem, 
    QStandardItemModel, 
    QBrush,
    QPalette
)
from PyQt6.QtCore import Qt, pyqtSlot, QDateTime,QPointF, QEasingCurve
from datetime import datetime
from psutil import disk_usage

from src.backend.swarm import Swarm
from src.backend.metadata.TorrentData import TorrentFile
from src.frontend.models.FileTreeModel import FileTreeModel
from src.frontend.widgets.PartProgress import PartProgress
from src.frontend.widgets.ChartWidget import ChartWidget
from src.frontend.views.FileTreeView import FileTreeView
from src.frontend.utils.utils import convert_bits, convert_seconds, to_seconds
import random

class GeneralTab(QWidget):
    def __init__(self):
        super().__init__()
        
        central_layout = QVBoxLayout()
        self.setLayout(central_layout)
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setGeometry(central_widget.geometry())
        scroll_area.setWidget(central_widget)
        central_layout.addWidget(scroll_area)
        
        self.progress_bar = PartProgress()
        main_layout.addWidget(self.progress_bar)
        
        self.health_bar = PartProgress()
        main_layout.addWidget(self.health_bar)
        
        information_box = QGroupBox()
        information_box.setTitle(self.tr("Information"))
        information_layout = QGridLayout()
        information_box.setLayout(information_layout)
        
        self.leechers = QLabel(self.tr("Leecher: {}").format(""))
        self.seeders = QLabel(self.tr("Seeder: {}").format(""))
        self.downloaded = QLabel(self.tr("Downloaded: {}").format(""))
        self.uploaded = QLabel(self.tr("Uploaded: {}").format(""))
        self.share_ratio = QLabel(self.tr("Share ratio: {}").format(""))
        self.progress = QLabel(self.tr("Progress: {}").format(""))
        self.download_speed = QLabel(self.tr("Download speed: {}").format(""))
        self.upload_speed = QLabel(self.tr("Upload speed: {}").format(""))
        self.pieces = QLabel(self.tr("Pieces: {}").format(""))
        self.eta = QLabel(self.tr("ETA: {}").format(""))
        self.health = QLabel(self.tr("Health: {}").format(""))
        self.availability = QLabel(self.tr("Availability: {}").format(""))
        self.time_active = QLabel(self.tr("Time active: {}").format(""))
        self.reannounce_in = QLabel(self.tr("Reannounce in: {}").format(""))
        
        information_layout.addWidget(self.leechers, 0, 0)
        information_layout.addWidget(self.seeders, 0, 1)
        information_layout.addWidget(self.downloaded, 1, 0)
        information_layout.addWidget(self.uploaded, 1, 1)
        information_layout.addWidget(self.share_ratio, 2, 0)
        information_layout.addWidget(self.progress, 2, 1)
        information_layout.addWidget(self.download_speed, 3, 0)
        information_layout.addWidget(self.upload_speed, 3, 1)
        information_layout.addWidget(self.pieces, 4, 0)
        information_layout.addWidget(self.eta, 4, 1)
        information_layout.addWidget(self.health, 5, 0)
        information_layout.addWidget(self.availability, 5, 1)
        information_layout.addWidget(self.time_active, 6, 0)
        information_layout.addWidget(self.reannounce_in, 6, 1)
        main_layout.addWidget(information_box)

        torrent_box = QGroupBox()
        torrent_box.setTitle(self.tr("Torrent"))
        torrent_layout = QGridLayout()
        torrent_box.setLayout(torrent_layout)
        
        self.info_hash = QLabel(self.tr("Info Hash: {}").format(""))
        self.save_path = QLabel(self.tr("Save Path: {}").format(""))
        self.size = QLabel(self.tr("Size: {}").format(""))
        self.created_by = QLabel(self.tr("Created by: {}").format(""))
        self.creation_date = QLabel(self.tr("Creation date: {}").format(""))
        self.start_date = QLabel(self.tr("Start date: {}").format(""))
        self.comment = QLabel(self.tr("Comment: {}").format(""))
        self.finish_date = QLabel(self.tr("Finish date: {}").format(""))
        self.comment.setWordWrap(True)
        
        torrent_layout.addWidget(self.info_hash, 0, 0)
        torrent_layout.addWidget(self.save_path, 0, 1)
        torrent_layout.addWidget(self.size, 1, 0)
        torrent_layout.addWidget(self.created_by, 1, 1)
        torrent_layout.addWidget(self.creation_date, 2, 0)
        torrent_layout.addWidget(self.start_date, 2, 1)
        torrent_layout.addWidget(self.comment, 3, 0)
        torrent_layout.addWidget(self.finish_date, 3, 1)
        main_layout.addWidget(torrent_box)
        main_layout.addStretch()
    
    def _update(self, swarm):
        print('update detail')
        self.progress_bar.setRange(0, swarm.data.pieces_count)
        self.progress_bar.setValues(int(swarm.piece_manager.downloaded_percent), [x for x in swarm.piece_manager.pieces])
        self.health_bar.setValues(int(swarm.piece_manager.health), [x.index for x in swarm.piece_manager.pieces if x.count_peers != 0])

        free_space = convert_bits(disk_usage('/').free)
        torrent_size = convert_bits(swarm.data.files.length)
        piece_size = convert_bits(swarm.data.piece_length)
        start_date = datetime.fromisoformat(swarm.start_date).strftime("%Y-%m-%d %H:%M:%S") if  len(swarm.start_date) else "not yet" 
        finish_date = datetime.fromisoformat(swarm.finish_date).strftime("%Y-%m-%d %H:%M:%S") if  len(swarm.finish_date) else "not yet" 
        
        # update General Information fields
        self.leechers.setText(self.tr("Leechers: {}").format(swarm.leechers))
        self.seeders.setText(self.tr("Seeders: {}").format(swarm.seeders))
        self.downloaded.setText(self.tr("Downloaded: {}").format(convert_bits(swarm.piece_manager.downloaded_bytes)))
        #self.uploaded = QLabel("Uploaded: ")
        #self.share_ratio = QLabel("Share ratio: ")
        self.progress.setText(self.tr("Progress: {}").format(str(swarm.piece_manager.downloaded_percent) + "%"))
        self.download_speed.setText(self.tr("Download speed: {}").format(swarm.speed_measurer.avg_down_speed))
        #self.upload_speed = QLabel("Upload speed: ")
        self.pieces.setText(self.tr("Pieces: {} x {} (have {})").format(swarm.data.pieces_count, piece_size, swarm.piece_manager.finished_pieces))
        self.eta.setText(self.tr("ETA: {}").format(chr(0x221E) if swarm.speed_measurer.eta == -1 else convert_seconds(swarm.speed_measurer.eta)))
        self.health.setText(self.tr("Health: {}").format(str(swarm.piece_manager.health) + "%"))
        self.availability.setText(self.tr("Availability: {}").format(swarm.piece_manager.availability))
        self.time_active.setText(self.tr("Time active: {}").format(convert_seconds(swarm.time_active)))
        #self.reannounce_in = QLabel("Reaannounce in: ")
        
        # update Torrent Information fields
        self.info_hash.setText(self.tr("Info hash: {}").format(swarm.data.info_hash_hex))
        self.save_path.setText(self.tr("Save Path: {}").format(swarm.path))
        self.size.setText(self.tr("Size: {} (of {} on local disk)").format(torrent_size, free_space))
        self.created_by.setText(self.tr("Created by: {}").format(swarm.data.created_by))
        self.creation_date.setText(self.tr("Creation date: {}").format(swarm.data.creation_date))
        self.start_date.setText(self.tr("Start date: {}").format(start_date))
        self.comment.setText(self.tr("Comment: {}").format(swarm.data.comment))
        self.finish_date.setText(self.tr("Finish date: {}").format(finish_date))
    
    def _clear(self):
        self.progress_bar.setValues(0, [])
        self.health_bar.setValues(0, [])

        self.leechers = QLabel(self.tr("Leecher: {}").format(""))
        self.seeders = QLabel(self.tr("Seeder: {}").format(""))
        self.downloaded = QLabel(self.tr("Downloaded: {}").format(""))
        self.uploaded = QLabel(self.tr("Uploaded: {}").format(""))
        self.share_ratio = QLabel(self.tr("Share ratio: {}").format(""))
        self.progress = QLabel(self.tr("Progress: {}").format(""))
        self.download_speed = QLabel(self.tr("Download speed: {}").format(""))
        self.upload_speed = QLabel(self.tr("Upload speed: {}").format(""))
        self.pieces = QLabel(self.tr("Pieces: {}").format(""))
        self.eta = QLabel(self.tr("ETA: {}").format(""))
        self.health = QLabel(self.tr("Health: {}").format(""))
        self.availability = QLabel(self.tr("Availability: {}").format(""))
        self.time_active = QLabel(self.tr("Time active: {}").format(""))
        self.reannounce_in = QLabel(self.tr("Reannounce in: {}").format(""))
        self.info_hash = QLabel(self.tr("Info Hash: {}").format(""))
        self.save_path = QLabel(self.tr("Save Path: {}").format(""))
        self.size = QLabel(self.tr("Size: {}").format(""))
        self.created_by = QLabel(self.tr("Created by: {}").format(""))
        self.creation_date = QLabel(self.tr("Creation date: {}").format(""))
        self.start_date = QLabel(self.tr("Start date: {}").format(""))
        self.comment = QLabel(self.tr("Comment: {}").format(""))
        self.finish_date = QLabel(self.tr("Finish date: {}").format(""))
 
class ChartTab(ChartWidget):
    def __init__(self, parent=None):
        super(ChartTab, self).__init__()
 
class TrackersTab(QWidget):
    def __init__(self):
        super().__init__()    
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        self.table_widget = QTableView()
        self.model = QStandardItemModel()
        self.table_widget.setModel(self.model)
        
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.verticalHeader().hide()
        self.table_widget.setSortingEnabled(True)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        main_layout.addWidget(self.table_widget)
        
        self._clear()
    
    def _update(self, tracker_list: list = []):
        scroll = self.table_widget.verticalScrollBar().value()
        indexes = self.table_widget.selectedIndexes()
        
        self.model.beginResetModel()
        self._clear()
        for tracker in tracker_list:
            if tracker:
                a = tracker.address if type(tracker.address) == str else f'{tracker.address[0]}:{tracker.address[1]}'
                addr = QStandardItem(a)
                states = ['not contacted', 'connecting...', 'finished', 'stopped with error']
                states = [self.tr(item) for item in states]
                colors = [None, QColor('yellow'), QColor('green'), QColor('red')]
                status = QStandardItem(states[tracker.status.value])
                if tracker.status.value != 0:
                    status.setForeground(colors[tracker.status.value])
                peers = QStandardItem(str(len(tracker.peers)))
                leechers = QStandardItem(str(tracker.leechers))
                seeders = QStandardItem(str(tracker.seeders))
                interval = QStandardItem(convert_seconds(tracker.interval))
                error = QStandardItem(tracker.error)
                self.model.appendRow([addr, status, peers, leechers, seeders, interval, error])
        self.model.endResetModel()
        
        if len(indexes):
            self.table_widget.selectRow(indexes[0].row())
        else:
            self.table_widget.selectRow(0)
        self.table_widget.verticalScrollBar().setValue(scroll)
       
    
    def _clear(self):
        self.model.clear()
        headers = ["address", "status", "peers", "leechers", "seeders", "interval", "error"]
        headers = [self.tr(item) for item in headers]
        self.model.setHorizontalHeaderLabels(headers)
    
class PeersTab(QWidget):
    def __init__(self):
        super().__init__()   
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        self.table_widget = QTableView()
        self.model = QStandardItemModel()
        self.table_widget.setModel(self.model)
        
        self.table_widget.setSortingEnabled(True)
        self.table_widget.verticalHeader().hide()
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        main_layout.addWidget(self.table_widget)
        
        self._clear()
    
    def _update(self, peer_list: list = []):
        indexes = self.table_widget.selectedIndexes()
        scroll = self.table_widget.verticalScrollBar().value()
        
        self._clear()
        for peer in peer_list:
            ip = QStandardItem(peer.address[0])
            port = QStandardItem(str(peer.address[1]))
            client = QStandardItem(peer.client)
            conn = QStandardItem('default')
            flags = QStandardItem(peer.flags)
            sources = QStandardItem(peer.sources)
            entirety = QStandardItem(f"{peer.entirety}%")
            self.model.appendRow([ip, port, client, conn, flags, sources, entirety])

        if len(indexes) != 0:
            self.table_widget.selectRow(indexes[0].row())
        else:
            self.table_widget.selectRow(0) # so scroll gets udated, otherwise is not already set
        self.table_widget.verticalScrollBar().setValue(scroll)
    
    def _clear(self):
        self.model.clear()
        headers = ["ip", "port", "client", "connection", "flags", "sources", "entirety"]
        headers = [self.tr(item) for item in headers]
        self.model.setHorizontalHeaderLabels(headers)
    
class FilesTab(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        self.model = FileTreeModel()
        self.tree_view = FileTreeView(self.model)
        self.tree_view.setModel(self.model)
        main_layout.addWidget(self.tree_view)
        
    def _update(self, data: TorrentFile = None):
        self.model.update(data)
    
    def _clear(self):
        self.model.removeRow(0)
        self.tree_view.reevaluate()

class TorrentDetailView(QTabWidget):
    def __init__(self, tabs_pos):
        super().__init__()
        
        self.tabs = list()
        
        self.general_tab = GeneralTab()
        self.chart_tab = ChartTab()
        self.trackers_tab = TrackersTab()
        self.peers_tab = PeersTab()
        self.files_tab = FilesTab()
        
        self.tabs.append([self.general_tab, QIcon('resources/icons/general.svg'), self.tr("General")])
        self.tabs.append([self.trackers_tab, QIcon('resources/icons/trackers.svg'), self.tr("Trackers")])
        self.tabs.append([self.peers_tab, QIcon('resources/icons/peer.svg'), self.tr("Peers")])
        self.tabs.append([self.chart_tab, QIcon('resources/icons/chart.svg'), self.tr("Chart")])
        self.tabs.append([self.files_tab, QIcon('resources/icons/files.svg'), self.tr("Files")])
        
        self.setMovable(True)
        self.setMinimumHeight(300)
        self.setMinimumWidth(self.tabBar().sizeHint().width() + 30)
        self.tabBar().setUsesScrollButtons(False)
        
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
    
    def _update(self, dt: Swarm):
        self.general_tab._update(dt)
        self.trackers_tab._update(dt.tracker_list)
        self.peers_tab._update(dt.active_peers)
        self.chart_tab._update(dt.chart)
        self.files_tab._update(dt.data.files)
    
    def _clear(self):
        self.general_tab._clear()
        self.trackers_tab._clear()
        self.peers_tab._clear()
        self.chart_tab._clear()
        self.files_tab._clear()