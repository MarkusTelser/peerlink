from PyQt6.QtWidgets import (
    QDialog,
    QTextEdit,  
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QTabWidget,
    QWidget,
    QDialogButtonBox,
    QPlainTextEdit,
    QApplication
)
from PyQt6.QtGui import QIcon, QFont, QPixmap, QTextDocument
from PyQt6.QtCore import QSize, Qt


class GeneralTab(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        wrapper_label = QLabel('image')
        pixmap = QPixmap('resources/icons/logo.svg')
        wrapper_label.setPixmap(pixmap)
        main_layout.addWidget(wrapper_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        temp_widget = QWidget()
        temp_layout = QFormLayout()
        temp_widget.setLayout(temp_layout)

        temp_layout.addRow(QLabel(self._cst_bld('Author:')), QLabel('Markus Telser'))
        temp_layout.addRow(QLabel(self._cst_bld('License:')), QLabel('GPL v3.0'))
        temp_layout.addRow(QLabel(self._cst_bld('Repository:')), self._cst_url('https://www.github.com/markustelser/peerlink'))
        temp_layout.addRow(QLabel(self._cst_bld('Donate To:')), self._cst_url('https://www.paypal.com'))
        temp_layout.addRow(QLabel(self._cst_bld('Email To:')), self._cst_url('markus.telser99@gmail.com', True))

        main_layout.addWidget(temp_widget, alignment=Qt.AlignmentFlag.AlignCenter)    
    
    def _cst_url(self, url: str, email=False):
        label = QLabel(f"<a href='{'mailto:' if email else ''}{url}'>{url}</a>")
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        label.setOpenExternalLinks(True)
        return label

    def _cst_bld(self, txt: str):
        return f"<font color='#FFFFFF' font_size=20><big>{txt}</big></font>"

class ManualTab(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        license = open('README.md', 'r').read()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.document().setMarkdown(license, QTextDocument.MarkdownFeature.MarkdownDialectGitHub	)

        main_layout.addWidget(text_edit)

class LicenseTab(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        license = open('LICENSE.txt', 'r').read()
        text_edit = QPlainTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(license)
        main_layout.addWidget(text_edit)
        

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        
        self.resize(QSize(750, 500))
        self.setWindowTitle('About - PeerLink')
        self.setWindowIcon(QIcon('resources/logo.svg'))
        self.setObjectName('AboutWindow')
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        client = QLabel(f"PeerLink v{QApplication.applicationVersion()}")
        client.setFont(QFont('Arial', 20))
        main_layout.addWidget(client)

        description = QLabel("bittorrent client from scratch for linux, mac, win")
        description.setContentsMargins(0, 0, 0, 20)
        main_layout.addWidget(description)
        
        tab_widget = QTabWidget()
        
        tab_widget.addTab(GeneralTab(), 'General')
        tab_widget.addTab(ManualTab(), 'Manual')
        tab_widget.addTab(LicenseTab(), 'License')
        
        main_layout.addWidget(tab_widget)
        
        button_box = QDialogButtonBox()
        button_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        button_box.rejected.connect(self.close)
        main_layout.addWidget(button_box)
    
    def resizeEvent(self, a0):
        print(a0.size())    