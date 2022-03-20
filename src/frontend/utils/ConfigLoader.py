from PyQt6.QtCore import QSettings, QSize, QPoint, QByteArray
from PyQt6.QtWidgets import QApplication
from os.path import join, expanduser


class ConfigLoader():
    def __init__(self):
        self.settings = QSettings(QApplication.applicationName(), QApplication.applicationName())
        
        self.win_size = self.settings.value('win_size', QSize(900, 700), QSize)
        self.win_loc = self.settings.value('win_loc', None, QPoint)
        self.show_toolbar = self.settings.value('show_toolbar', True, bool)
        self.show_statusbar = self.settings.value('show_statusbar', True, bool)
        self.hori_splitter = [int(x) for x in self.settings.value('hori_splitter', [300, 700], list)]
        self.vert_splitter = [int(x) for x in self.settings.value('vert_splitter', [1, 0], list)]
        
        self.side_current = self.settings.value('side_current', 0, int)
        self.side_tabs = self.settings.value('side_tabs', [], list)
        self.detail_current = self.settings.value('detail_current', 0, int)
        self.detail_tabs = self.settings.value('detail_tabs', [], list)
        self.table_tabs = self.settings.value('table_tabs', QByteArray(), QByteArray)
        self.show_launch = self.settings.value('show_launch', True, bool)
        
        # Preview Window
        self.settings.beginGroup('PreviewWindow')
        self.preview_size = self.settings.value('preview_size', QSize(900, 700), QSize)
        self.preview_location = self.settings.value('preview_location', None, QPoint)
        self.open_preview = self.settings.value('open_preview', True, bool)
        self.default_path = self.settings.value('default_path', join(expanduser('~'), 'Downloads'), str)
        self.categorys = self.settings.value('categorys', [], list)
        self.default_category = self.settings.value('default_category', '', str)
        self.auto_start = self.settings.value('auto_start', True, bool)
        self.check_hashes = self.settings.value('check_hashes', True, bool)
        self.padd_files = self.settings.value('padd_files', False, bool)
        
        self.settings.endGroup()
    
    def saveSettings(self):
        pass