from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGroupBox, QLabel
from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtCore import Qt
from datetime import datetime

from src.frontend.utils.utils import convert_detail_sec, convert_bits


class StatisticsWindow(QMainWindow):
    def __init__(self, stats, parent):
        super(StatisticsWindow, self).__init__(parent=parent)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 0, 10, 10)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.resize(400, 650)
        self.setWindowTitle(self.tr("Statistics - PeerLink"))
        self.setWindowIcon(QIcon("resources/icons/logo.svg"))
        
        # center in the middle of screen
        qtRectangle = self.frameGeometry()
        qtRectangle.moveCenter(parent.frameGeometry().center())
        self.move(qtRectangle.topLeft())

        group_box = QGroupBox()
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(50, 50, 50, 50)
        group_box.setLayout(group_layout)
        main_layout.addWidget(group_box)
        
        label1 = QLabel(self.tr("Total Downloaded: {}").format(convert_bits(stats.total_downloaded)))
        label2 = QLabel(self.tr("Total Uploaded: {}").format(convert_bits(stats.total_uploaded)))
        group_layout.addWidget(label1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        group_layout.addWidget(label2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        group_layout.addStretch(1)

        label1 = QLabel(self.tr("Session Downloaded: {}").format(convert_bits(stats.session_downloaded)))
        label2 = QLabel(self.tr("Session Uploaded: {}").format(convert_bits(stats.session_uploaded)))
        group_layout.addWidget(label1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        group_layout.addWidget(label2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        group_layout.addStretch(1)

        label1 = QLabel(self.tr("Total Share Ratio: {}").format(stats.total_ratio))
        label2 = QLabel(self.tr("Session Share Ratio: {}").format(stats.session_ratio))
        group_layout.addWidget(label1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        group_layout.addWidget(label2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        group_layout.addStretch(1)
        
        label1 = QLabel(self.tr("Total Time Running: {}").format(convert_detail_sec(stats.total_time_running)))
        label2 = QLabel(self.tr("Session Time Running: {}").format(convert_detail_sec(stats.session_time_running)))
        group_layout.addWidget(label1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        group_layout.addWidget(label2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        group_layout.addStretch(1)

        frm_date = datetime.fromisoformat(stats.program_running_since).strftime("%Y-%m-%d")
        days_since = (datetime.now() - datetime.fromisoformat(stats.program_running_since)).days
        label1 = QLabel(self.tr("Program Opened: {} times").format(stats.program_opened))
        label2 = QLabel(self.tr("Running Since: {} ({} days)").format(frm_date, days_since))
        group_layout.addWidget(label1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        group_layout.addWidget(label2, 1, alignment=Qt.AlignmentFlag.AlignCenter)