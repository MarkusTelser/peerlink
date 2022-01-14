from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtCore import Qt
from PyQt6.QtCharts import QSplineSeries, QChart, QValueAxis, QChartView
from pip import main

class StatisticsPanel(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
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