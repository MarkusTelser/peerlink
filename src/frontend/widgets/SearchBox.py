from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QLineEdit


class SearchBar(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setObjectName('SearchBar')
        self.setMinimumWidth(100) 
        self.setPlaceholderText('Search...')
        self.addAction(QIcon('resources/search.svg'), QLineEdit.ActionPosition.LeadingPosition)
        self.setClearButtonEnabled(True)
        self.findChild(QAction, "_q_qlineeditclearaction").setIcon(QIcon("resources/cancel.svg"))
        