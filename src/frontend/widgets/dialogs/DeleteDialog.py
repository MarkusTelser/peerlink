from PyQt6.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QLabel, QVBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSlot


class DeleteDialog(QDialog):
    def __init__(self, all_torrents=False):
        super().__init__()
        
        self.setBaseSize(300, 300)
        self.setWindowTitle(self.tr("Delete Torrent - PeerLink"))
        self.setWindowIcon(QIcon("resources/icons/logo.svg"))
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        if not all_torrents:
            affirm_txt = QLabel(self.tr("Are you sure you want to delete this torrent?"))
            self.checkbox = QCheckBox(self.tr("delete files too"))
        else:
            affirm_txt = QLabel(self.tr("Are you sure you want to delete all torrents?"))
            self.checkbox = QCheckBox(self.tr("delete all files too"))
        self.checkbox.setChecked(True)
        main_layout.addWidget(affirm_txt)
        main_layout.addWidget(self.checkbox)
        
        buttonBox = QDialogButtonBox()
        buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)
        buttonBox.addButton(QDialogButtonBox.StandardButton.Ok)
        buttonBox.layout().setAlignment(Qt.AlignmentFlag.AlignRight)
        buttonBox.rejected.connect(self.button_reject)
        buttonBox.accepted.connect(self.button_accept)
        main_layout.addWidget(buttonBox)

    @pyqtSlot()
    def button_accept(self):
        self.accept()
        self.close()
        
    @pyqtSlot()
    def button_reject(self):
        self.reject()
        self.close()