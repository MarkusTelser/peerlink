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
from PyQt6.QtCore import Qt, pyqtSlot

from src.frontend.utils.utils import showError


class MagnetLinkDialog(QDialog):
    def __init__(self, parent):
        super(MagnetLinkDialog, self).__init__(parent=parent)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        self.setFixedSize(600, 120)
        self.setObjectName("MagnetLinkDialog")
        self.setWindowIcon(QIcon("resources/icons/logo.svg"))
        self.setWindowTitle(self.tr("Add Magnet Link - PeerLink"))

        # center in the middle of screen
        qtRectangle = self.frameGeometry()
        qtRectangle.moveCenter(parent.frameGeometry().center())
        self.move(qtRectangle.topLeft())
        
        message = QLabel(self.tr("Enter magnet link:"))
        main_layout.addWidget(message)

        self.text_box = QLineEdit()
        main_layout.addWidget(self.text_box)
        self.insert_clipboard()

        # button box with add and cancel
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)
        add_button = QPushButton(QIcon("resources/icons/add.svg"), self.tr("Add"), self)
        buttonBox.addButton(add_button, QDialogButtonBox.ButtonRole.AcceptRole)
        buttonBox.layout().setDirection(QBoxLayout.Direction.LeftToRight)
        buttonBox.layout().setAlignment(Qt.AlignmentFlag.AlignRight)
        buttonBox.rejected.connect(self.reject)
        buttonBox.accepted.connect(self.accept)
        main_layout.addWidget(buttonBox)
        
        QApplication.clipboard().dataChanged.connect(self.insert_clipboard)


    @pyqtSlot()
    def insert_clipboard(self):
        clipboard = QApplication.clipboard().text()
        if clipboard.startswith("magnet:?"):
            self.text_box.setText(clipboard)
    

    @pyqtSlot()
    def accept(self):
        if self.text_box.text():
            return super().accept()
        showError(self.tr("No magnet link inserted!"), self)
