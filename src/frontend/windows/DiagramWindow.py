from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtGui import QColor, QPainter, QIcon, QGuiApplication
from PyQt6.QtCharts import QSplineSeries, QChart, QValueAxis, QChartView
from PyQt6.QtCore import Qt


class DiagramWindow(QMainWindow):
    def __init__(self, parent=None):
        super(DiagramWindow, self).__init__(parent=parent)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.resize(600, 600)
        self.setWindowTitle("Diagram - PeerLink")
        self.setWindowIcon(QIcon('resources/logo.svg'))
        
        # center in the middle of screen
        qtRectangle = self.frameGeometry()
        centerPoint = QGuiApplication.primaryScreen().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        
        series = QSplineSeries()
        #series.append(10, 1)
        #series.append(5, 3)
        #series.append(8, 4)
        #series.append(9, 6)
        #series.append(2, 9)
        
        chart = QChart()
        chart.legend().hide()
        chart.createDefaultAxes()
        chart.setTheme(QChart.ChartTheme.ChartThemeBlueIcy)
        chart.layout().setContentsMargins(0, 0, 0, 0)
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
        chart_view.setBackgroundBrush(QColor("red"))
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        main_layout.addWidget(chart_view)