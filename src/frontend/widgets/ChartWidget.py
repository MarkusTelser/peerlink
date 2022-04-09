from PyQt6.QtCore import pyqtSlot, Qt, QDateTime, QEasingCurve
from PyQt6.QtGui import QBrush, QColor, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSizePolicy
from PyQt6.QtCharts import QChart, QChartView, QSplineSeries, QValueAxis, QDateTimeAxis

from src.frontend.utils.utils import to_seconds

class ChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        sub_widget = QWidget()
        sub_layout = QHBoxLayout()
        sub_widget.setLayout(sub_layout)

        label = QLabel('Period:')
        sub_layout.addWidget(label)

        self.combo_box = QComboBox()
        self.combo_box.addItems(['1 min', '10 min', '30 min', '1 h', '6 h', '12 h', '24 h'])
        self.combo_box.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.combo_box.currentTextChanged.connect(self.combobox_select)
        sub_layout.addWidget(self.combo_box, Qt.AlignmentFlag.AlignLeft)
        sub_layout.addStretch()

        main_layout.addWidget(sub_widget)

        current_m = QDateTime.currentDateTime()
        m = QDateTime.currentDateTime()

        self.series = QSplineSeries()
        self.series.append(m.addSecs(-50).toMSecsSinceEpoch() , 1)
        self.series.append(m.addSecs(-40).toMSecsSinceEpoch(), 20)
        self.series.append(m.addSecs(-30).toMSecsSinceEpoch(), 1)
        
        chart = QChart()
        chart.setAnimationEasingCurve(QEasingCurve.Type.Linear)
        chart.addSeries(self.series)
        chart.layout().setContentsMargins(0, 0, 0, 0)
        chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        chart.setBackgroundRoundness(0)
        chart.legend().hide()
        
        self.time_axis = QDateTimeAxis()
        self.time_axis.setTickCount(10)
        self.time_axis.setFormat("hh:mm:ss")
        self.time_axis.setTitleText("time axis")
        self.time_axis.setRange(current_m.addSecs(-60), QDateTime.currentDateTime())
        chart.addAxis(self.time_axis, Qt.AlignmentFlag.AlignBottom)
        self.series.attachAxis(self.time_axis)

        self.speed_axis = QValueAxis()
        self.speed_axis.setRange(0, 30)
        self.speed_axis.setTickCount(5)
        self.speed_axis.setTitleText("speed axis")
        chart.addAxis(self.speed_axis, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(self.speed_axis)
        
        chart_view = QChartView(chart)
        chart_view.chart().setBackgroundBrush(QBrush(QColor("transparent")))
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        main_layout.addWidget(chart_view)
    
    @pyqtSlot(str)
    def combobox_select(self, text: str):
        secs = to_seconds(self.combo_box.currentText())
        current_date = QDateTime.currentDateTime()
        self.time_axis.setRange(current_date.addSecs(-secs), current_date)

        if secs > 600:
            self.time_axis.setFormat("hh:mm")
        else:
            self.time_axis.setFormat("hh:mm:ss")