from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QTabWidget, QTableView, QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtGui import QColor, QIcon, QPainter, QStandardItem, QStandardItemModel, QBrush
from PyQt6.QtCharts import QChart, QChartView, QSplineSeries, QValueAxis
from src.backend.metadata.TorrentData import TorrentFile
from src.backend.swarm import Swarm
from src.frontend.models.TorrentTreeModel import TorrentTreeModel
from src.frontend.views.TorrentTreeView import TorrentTreeView

class GeneralTab(QWidget):
    def __init__(self):
        super().__init__()
 
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
        
        #self.table_widget.verticalHeader().hide()
        self.table_widget.setSortingEnabled(True)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        main_layout.addWidget(self.table_widget)
        
        self._clear()
    
    def _update(self, tracker_list: list = []):
        self._clear()
        for tracker in tracker_list:
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
    def __init__(self):
        super().__init__()
        
        self.general_tab = GeneralTab()
        self.chart_tab = ChartTab()
        self.trackers_tab = TrackersTab()
        self.peers_tab = PeersTab()
        self.files_tab = FilesTab()
        
        self.addTab(self.general_tab, QIcon('resources/general.svg'), "General")
        self.addTab(self.trackers_tab, QIcon('resources/trackers.svg'), "Trackers")
        self.addTab(self.peers_tab, QIcon('resources/peer.svg'), "Peers")
        self.addTab(self.chart_tab, QIcon('resources/chart.svg'), "Chart")
        self.addTab(self.files_tab, QIcon('resources/files.svg'), "Files")
        
        self.setMinimumWidth(self.tabBar().sizeHint().width() + 30)
        #self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.tabBar().setUsesScrollButtons(False)
        
    
    def _update(self, dt: Swarm):
        self.trackers_tab._update(dt.tracker_list)
        self.peers_tab._update(dt.peer_list)
        self.files_tab._update(dt.data.files)
    
    def _clear(self):
        self.trackers_tab._clear()
        self.peers_tab._clear()
        self.files_tab._clear()