from PyQt6.QtWidgets import (
    QHeaderView, 
    QTabWidget, 
    QTableView, 
    QWidget, 
    QVBoxLayout, 
    QProgressBar, 
    QGroupBox,
    QLabel,
    QGridLayout,
    QScrollArea,
    QAbstractItemView
)
from PyQt6.QtGui import (
    QColor, 
    QIcon, 
    QPainter, 
    QStandardItem, 
    QStandardItemModel, 
    QBrush
)
from PyQt6.QtCharts import QChart, QChartView, QSplineSeries, QValueAxis
from PyQt6.QtCore import Qt
from datetime import datetime
from psutil import disk_usage

from src.backend.swarm import Swarm
from src.backend.metadata.TorrentData import TorrentFile
from src.frontend.models.TorrentTreeModel import TorrentTreeModel
from src.frontend.widgets.PartProgress import PartProgress
from src.frontend.views.TorrentTreeView import TorrentTreeView
from src.frontend.utils.utils import convert_bits


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
        information_box.setTitle('Information')
        information_layout = QGridLayout()
        information_box.setLayout(information_layout)
        
        self.leechers = QLabel("Leecher: ")
        self.seeders = QLabel("Seeder: ")
        self.downloaded = QLabel("Downloaded: ")
        self.uploaded = QLabel("Uploaded: ")
        self.share_ratio = QLabel("Share ratio: ")
        self.progress = QLabel("Progress: ")
        self.download_speed = QLabel("Download speed: ")
        self.upload_speed = QLabel("Upload speed: ")
        self.pieces = QLabel("Pieces: ")
        self.eta = QLabel("ETA: ")
        self.health = QLabel("Health: ")
        self.availability = QLabel("Availability: ")
        self.time_active = QLabel("Time active: ")
        self.reannounce_in = QLabel("Reaannounce in: ")
        
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
        torrent_box.setTitle('Torrent')
        torrent_layout = QGridLayout()
        torrent_box.setLayout(torrent_layout)
        
        self.info_hash = QLabel("Info Hash: ")
        self.save_path = QLabel("Save Path: ")
        self.size = QLabel("Size: ")
        self.created_by = QLabel("Created by: ")
        self.creation_date = QLabel("Creation date: ")
        self.start_date = QLabel("Start date: ")
        self.comment = QLabel("Comment: ")
        self.finish_date = QLabel("Finish date: ")
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
        self.progress_bar.setRange(0, swarm.data.pieces_count)
        self.progress_bar.setValues(int(swarm.piece_manager.downloaded_percent), [x for x in swarm.piece_manager.pieces])
        self.health_bar.setValues(int(swarm.piece_manager.health), [x.index for x in swarm.piece_manager.pieces if x.count_peers != 0])

        free_space = convert_bits(disk_usage('/').free)
        torrent_size = convert_bits(swarm.data.files.length)
        piece_size = convert_bits(swarm.data.piece_length)
        start_date = datetime.fromisoformat(swarm.start_date).strftime("%Y-%m-%d %H:%M:%S") if  len(swarm.start_date) else "not yet" 
        finish_date = datetime.fromisoformat(swarm.finish_date).strftime("%Y-%m-%d %H:%M:%S") if  len(swarm.finish_date) else "not yet" 
        
        # update General Information fields
        self.leechers.setText(f"Leechers: {swarm.leechers}")
        self.seeders.setText(f"Seeders: {swarm.seeders}")
        self.downloaded.setText(f"Downloaded: {convert_bits(swarm.piece_manager.downloaded_bytes)}")
        #self.uploaded = QLabel("Uploaded: ")
        #self.share_ratio = QLabel("Share ratio: ")
        self.progress.setText(f"Progress: {swarm.piece_manager.downloaded_percent}%")
        self.download_speed.setText(f"Download speed: {swarm.speed_measurer.avg_down_speed}")
        #self.upload_speed = QLabel("Upload speed: ")
        self.pieces.setText(f"Pieces: {swarm.data.pieces_count} x {piece_size} (have {swarm.piece_manager.finished_pieces})")
        #self.eta = QLabel("ETA: ")
        self.health.setText(f"Health: {swarm.piece_manager.health}%")
        self.availability.setText(f"Availability: {swarm.piece_manager.availability}")
        #self.time_active = QLabel("Time active: ")
        #self.reannounce_in = QLabel("Reaannounce in: ")
        
        # update Torrent Information fields
        self.info_hash.setText(f"Info hash: {swarm.data.info_hash_hex}")
        self.save_path.setText(f"Save Path: {swarm.path}")
        self.size.setText(f"Size: {torrent_size} (of {free_space} on local disk)")
        self.created_by.setText(f"Created by: {swarm.data.created_by}")
        self.creation_date.setText(f"Creation date: {swarm.data.creation_date}")
        self.start_date.setText(f"Start date: {start_date}")
        self.comment.setText(f"Comment: {swarm.data.comment}")
        self.finish_date.setText(f"Finish date: {finish_date}")
    
    def _clear(self):
        self.leechers.setText("Leecher: ")
        self.seeders.setText("Seeder: ")
        self.downloaded.setText("Downloaded: ")
        self.uploaded.setText("Uploaded: ")
        self.share_ratio.setText("Share ratio: ")
        self.progress.setText("Progress: ")
        self.download_speed.setText("Download speed: ")
        self.upload_speed.setText("Upload speed: ")
        self.pieces.setText("Pieces: ")
        self.eta.setText("ETA: ")
        self.health.setText("Health: ")
        self.availability.setText("Availability: ")
        self.time_active.setText("Time active: ")
        self.reannounce_in.setText("Reaannounce in: ")
        self.info_hash.setText("Info hash: ")
        self.save_path.setText("Save Path: ")
        self.size.setText("Size: ")
        self.created_by.setText("Created by: ")
        self.creation_date.setText("Creation date: ")
        self.start_date.setText("Start date: ")
        self.comment.setText("Comment: ")
        self.finish_date.setText("Finish date: ")
 
class ChartTab(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        series = QSplineSeries()
        series.append(10, 1)
        series.append(5, 3)
        series.append(8, 4)
        series.append(9, 6)
        series.append(2, 9)
        
        chart = QChart()
        chart.legend().hide()
        chart.createDefaultAxes()
        chart.layout().setContentsMargins(0, 0, 0, 0)
        chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        chart.setBackgroundRoundness(0)
        chart.addSeries(series)
        
        speed_axis = QValueAxis()
        speed_axis.setRange(0, 10)
        speed_axis.setTickCount(5)
        speed_axis.setTitleText("speed axis")
        chart.addAxis(speed_axis, Qt.AlignmentFlag.AlignLeft)
        
        time_axis = QValueAxis()
        time_axis.setRange(0, 10)
        time_axis.setTickCount(0)
        time_axis.setTitleText("time axis")
        chart.addAxis(time_axis, Qt.AlignmentFlag.AlignBottom)
        
        chart_view = QChartView(chart)
        chart_view.chart().setBackgroundBrush(QBrush(QColor("transparent")))
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        main_layout.addWidget(chart_view)
 
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
                states = ['no contact', 'connecting...', 'finished', 'stopped with error']
                colors = [QColor('black'), QColor('yellow'), QColor('green'), QColor('red')]
                status = QStandardItem(states[tracker.status.value])
                status.setForeground(colors[tracker.status.value])
                error = QStandardItem(tracker.error)
                peers = QStandardItem(str(len(tracker.peers)))
                leechers = QStandardItem(str(tracker.leechers))
                seeders = QStandardItem(str(tracker.seeders))
                self.model.appendRow([addr, status, peers, leechers, seeders, error])
        self.model.endResetModel()
        
        if len(indexes):
            self.table_widget.selectRow(indexes[0].row())
        else:
            self.table_widget.selectRow(0)
        self.table_widget.verticalScrollBar().setValue(scroll)
       
    
    def _clear(self):
        self.model.clear()
        headers = ["address", "status", "peers", "leechers", "seeders", "error"]
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
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        main_layout.addWidget(self.table_widget)
        
        self._clear()
    
    def _update(self, peer_list: list = []):
        indexes = self.table_widget.selectedIndexes()
        scroll = self.table_widget.verticalScrollBar().value()
        
        self._clear()
        for peer in peer_list:
            ip = QStandardItem(peer.address[0])
            port = QStandardItem(peer.address[1])
            con_type = QStandardItem('')
            status = QStandardItem('connecting...')
            ip.setEditable(False)
            port.setEditable(False)
            con_type.setEditable(False)
            status.setEditable(False)
            self.model.appendRow([ip, port, con_type, status])

        if len(indexes) != 0:
            self.table_widget.selectRow(indexes[0].row())
        else:
            self.table_widget.selectRow(0) # so scroll gets udated, otherwise is not already set
        self.table_widget.verticalScrollBar().setValue(scroll)
    
    def _clear(self):
        self.model.clear()
        headers = ["ip", "port", "connection type", "status"]
        self.model.setHorizontalHeaderLabels(headers)
    
class FilesTab(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        self.model = TorrentTreeModel()
        self.tree_view = TorrentTreeView(self.model)
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
        
        self.tabs.append([self.general_tab, QIcon('resources/general.svg'), "General"])
        self.tabs.append([self.trackers_tab, QIcon('resources/trackers.svg'), "Trackers"])
        self.tabs.append([self.peers_tab, QIcon('resources/peer.svg'), "Peers"])
        self.tabs.append([self.chart_tab, QIcon('resources/chart.svg'), "Chart"])
        self.tabs.append([self.files_tab, QIcon('resources/files.svg'), "Files"])
        
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
        self.peers_tab._update(dt.peer_list)
        self.files_tab._update(dt.data.files)
    
    def _clear(self):
        self.general_tab._clear()
        self.trackers_tab._clear()
        self.peers_tab._clear()
        self.files_tab._clear()