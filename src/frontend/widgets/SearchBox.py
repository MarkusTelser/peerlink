from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QLineEdit

class SearchBar(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.addAction(QIcon('resources/search.svg'), QLineEdit.ActionPosition.LeadingPosition)
        
        self.setMinimumWidth(100) 
        self.setClearButtonEnabled(True)
        self.findChild(QAction, "_q_qlineeditclearaction").setIcon(
            QIcon("resources/cancel.svg")
        )
        self.setStyleSheet("border-radius: 2px; margin: 3px; padding: 2px; border:1px solid gray")
        self.setPlaceholderText('Search...')