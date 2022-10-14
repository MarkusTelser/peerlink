from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit, QSpinBox
from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtCore import Qt
import sys

class SpeedLimitWindow(QMainWindow):
    def __init__(self, parent):
        super(SpeedLimitWindow, self).__init__(parent=parent)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.resize(450, 380)
        self.setObjectName("SpeedLimitWindow")
        self.setWindowTitle("Speed Limit - PeerLink")
        self.setWindowIcon(QIcon('resources/icons/logo.svg'))
        
        # center in the middle of screen
        qtRectangle = self.frameGeometry()
        qtRectangle.moveCenter(parent.frameGeometry().center())
        self.move(qtRectangle.topLeft())

        global_box = QGroupBox("Global Speed Limit")
        global_layout = QFormLayout()
        global_layout.setVerticalSpacing(10)
        global_layout.setContentsMargins(10, 15, 10, 10)
        global_box.setLayout(global_layout)
        main_layout.addWidget(global_box)

        spin_box1 = QSpinBox()
        spin_box1.setMaximum(2 ** 31 - 1)
        spin_box1.setSuffix(" KiB/s")
        spin_box2 = QSpinBox()
        spin_box2.setMaximum(2 ** 31 - 1)
        spin_box2.setSuffix(" KiB/s")
        global_layout.addRow("Download Speed Limit: ", spin_box1)
        global_layout.addRow("Upload Speed Limit: ", spin_box2)

        individual_box = QGroupBox("Individual Speed Limit")
        individual_layout = QFormLayout()
        individual_layout.setVerticalSpacing(10)
        individual_layout.setContentsMargins(10, 15, 10, 10)
        individual_box.setLayout(individual_layout)
        main_layout.addWidget(individual_box)

        spin_box1 = QSpinBox()
        spin_box1.setMaximum(2 ** 31 - 1)
        spin_box1.setSuffix(" KiB/s")
        spin_box2 = QSpinBox()
        spin_box2.setMaximum(2 ** 31 - 1)
        spin_box2.setSuffix(" KiB/s")
        individual_layout.addRow("Download Speed Limit: ", spin_box1)
        individual_layout.addRow("Upload Speed Limit: ", spin_box2)

        connection_box = QGroupBox("Connection Limit")
        connection_layout = QFormLayout()
        connection_layout.setVerticalSpacing(10)
        connection_layout.setContentsMargins(10, 15, 10, 10)
        connection_box.setLayout(connection_layout)
        main_layout.addWidget(connection_box)

        spin_box1 = QSpinBox()
        spin_box1.setMaximum(2 ** 31 - 1)
        spin_box2 = QSpinBox()
        spin_box2.setMaximum(2 ** 31 - 1)
        connection_layout.addRow("Global Outgoing Connections: ", spin_box1)
        connection_layout.addRow("Global Incoming Connections: ", spin_box2)
