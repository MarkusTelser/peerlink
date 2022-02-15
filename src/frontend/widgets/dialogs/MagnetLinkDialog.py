from PyQt6.QtWidgets import (
    QVBoxLayout,
    QDialog,
    QApplication,
    QLabel,
    QLineEdit,
    QDialogButtonBox,
    QPushButton,
    QBoxLayout
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from src.frontend.utils.utils import showError


class MagnetLinkDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.setFixedSize(600, 120)
        self.setWindowIcon(QIcon('resources/logo.svg'))
        self.setWindowTitle('Add Magnet Link - PeerLink')
        
        message = QLabel("Enter magnet link:")
        self.layout.addWidget(message)

        self.text_box = QLineEdit()
        self.insert_clipboard()
        self.layout.addWidget(self.text_box)

        # button box with add and cancel
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)
        add_button = QPushButton(QIcon('resources/add.svg'), ' Add', self)
        buttonBox.addButton(add_button, QDialogButtonBox.ButtonRole.AcceptRole)
        buttonBox.layout().setDirection(QBoxLayout.Direction.LeftToRight)
        buttonBox.layout().setAlignment(Qt.AlignmentFlag.AlignRight)
        buttonBox.rejected.connect(self.reject)
        buttonBox.accepted.connect(self.accept)
        self.layout.addWidget(buttonBox)
        
        QApplication.clipboard().dataChanged.connect(self.insert_clipboard)

    def insert_clipboard(self):
        clipboard = QApplication.clipboard().text()
        if clipboard.startswith('magnet:?'):
            self.text_box.setText(clipboard)
    
    def accept(self):
        if self.text_box.text():
            return super().accept()
        else:
            showError('No magnet link inserted!', self)