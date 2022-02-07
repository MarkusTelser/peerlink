from PyQt6.QtWidgets import (
    QDialog,
    QTextEdit,
    QVBoxLayout,
    QLabel,
    QTabWidget,
    QWidget,
    QDialogButtonBox,
    QPlainTextEdit
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize


class GeneralTab(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        about = open('src/frontend/utils/about.md', 'r').read()
        text_edit = QTextEdit()
        text_edit.setMarkdown(about)
        text_edit.setReadOnly(True)
        main_layout.addWidget(text_edit)

class ManualTab(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        license = open('README.md', 'r').read()
        text_edit = QTextEdit()
        text_edit.setMarkdown(license)
        main_layout.addWidget(text_edit)

class LicenseTab(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        license = open('LICENSE.txt', 'r').read()
        text_edit = QPlainTextEdit()
        text_edit.setPlainText(license)
        main_layout.addWidget(text_edit)
        

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        
        self.resize(QSize(600, 600))
        self.setWindowTitle('About - PeerLink')
        self.setWindowIcon(QIcon('resources/logo.svg'))
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        ver_label = QLabel('peerlink 0.1')
        main_layout.addWidget(ver_label)
        
        tab_widget = QTabWidget()
        
        tab_widget.addTab(GeneralTab(), 'General')
        tab_widget.addTab(ManualTab(), 'Manual')
        tab_widget.addTab(LicenseTab(), 'License')
        
        main_layout.addWidget(tab_widget)
        
        button_box = QDialogButtonBox()
        button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        button_box.rejected.connect(self.close)
        main_layout.addWidget(button_box)