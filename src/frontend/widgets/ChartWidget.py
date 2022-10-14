from PyQt6.QtCore import pyqtSlot, Qt, QDateTime, QEasingCurve, QPointF
from PyQt6.QtGui import QBrush, QColor, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSizePolicy, QCheckBox
from PyQt6.QtCharts import QChart, QChartView, QSplineSeries, QValueAxis, QDateTimeAxis, QValueAxis

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

        checkbox = QCheckBox("show legend")
        checkbox.clicked.connect(self.change_checkbox)
        sub_layout.addWidget(checkbox)

        sub_layout.addStretch()

        main_layout.addWidget(sub_widget)

        current_m = QDateTime.currentDateTime()
        m = QDateTime.currentDateTime()

        self.series = QSplineSeries()
        self.series.setName("Download")
        
        self.chart = QChart()
        self.chart.setAnimationEasingCurve(QEasingCurve.Type.Linear)
        self.chart.addSeries(self.series)
        self.chart.layout().setContentsMargins(0, 0, 0, 0)
        self.chart.setTheme(QChart.ChartTheme.ChartThemeDark)
        self.chart.setBackgroundRoundness(0)
        self.chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)
        self.chart.legend().hide()
        
        self.time_axis = QDateTimeAxis()
        self.time_axis.setTickCount(8)
        self.time_axis.setFormat("hh:mm:ss")
        self.time_axis.setTitleText("time axis")
        self.time_axis.setRange(current_m.addSecs(-60), QDateTime.currentDateTime())
        self.chart.addAxis(self.time_axis, Qt.AlignmentFlag.AlignBottom)
        self.series.attachAxis(self.time_axis)

        self.speed_axis = QValueAxis()
        self.speed_axis.setTickCount(4)
        self.speed_axis.setLabelFormat("%i B/s")
        self.speed_axis.setTitleText("speed axis")
        self.chart.addAxis(self.speed_axis, Qt.AlignmentFlag.AlignLeft)
        self.series.attachAxis(self.speed_axis)

        print(self.speed_axis.min(), self.speed_axis.max())
        
        chart_view = QChartView(self.chart)
        chart_view.chart().setBackgroundBrush(QBrush(QColor("transparent")))
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        main_layout.addWidget(chart_view)

    @pyqtSlot(bool)
    def change_checkbox(self, state):
        if state:
            self.chart.legend().show()
        else:
            self.chart.legend().hide()

    @pyqtSlot(str)
    def combobox_select(self, text: str):
        secs = to_seconds(self.combo_box.currentText())

        if secs > 600:
            self.time_axis.setFormat("hh:mm")
        else:
            self.time_axis.setFormat("hh:mm:ss")

        self._update(self._chart)

    
    def _update(self, chart):
        self._chart = chart
        now = QDateTime.currentDateTime()
        index = self.combo_box.currentIndex()
        
        self.series.clear()
        for i in range(1, len(chart.data[index]) + 1):
            time = now.addSecs(-2 * i).toMSecsSinceEpoch()
            self.series.append([QPointF(time, chart.data[index][-i])])

        # set time and speed axis range
        secs = to_seconds(self.combo_box.currentText())
        self.time_axis.setRange(now.addSecs(-secs), now)
        self.speed_axis.setRange(0, max(chart.data[index] or [0]) * 1.10)
    
    def _clear(self):
        self.series.clear()
