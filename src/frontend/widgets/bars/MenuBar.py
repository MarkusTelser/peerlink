from PyQt6.QtGui import QIcon, QKeySequence, QAction
from PyQt6.QtWidgets import QMenuBar, QMenu


class MenuBar(QMenuBar):
    def __init__(self):
        super().__init__()
        
         # file menu
        fileMenu = QMenu("&File", self)
        
        action_icon = QIcon("resources/icons/file.svg")
        action_name = self.tr("Open File")
        action_shortcut = QKeySequence("Ctrl+T")
        self.open_file = fileMenu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        action_icon = QIcon("resources/icons/link.svg")
        action_name = self.tr("Open Magnet Link")
        action_shortcut = QKeySequence("Ctrl+O")
        self.open_link = fileMenu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        fileMenu.addSeparator()
        
        action_icon = QIcon("resources/icons/new.svg")
        action_name = self.tr("Create Torrent File")
        action_shortcut = QKeySequence("Ctrl+N")
        self.create_torrent = fileMenu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        action_icon = QIcon("resources/icons/import.svg")
        action_name = self.tr("Import Torrent")
        action_shortcut = QKeySequence("Ctrl+I")
        self.import_torrent = fileMenu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        fileMenu.addSeparator()
        
        action_icon = QIcon("resources/icons/quit.svg")
        action_name = self.tr("Exit")
        action_shortcut = QKeySequence("Ctrl+Q")
        self.exit = fileMenu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        self.addMenu(fileMenu)
        
        # edit menu
        self.edit_menu = QMenu("&Edit", self)
        
        action_icon = QIcon("resources/icons/resume.svg")
        action_name = self.tr("Resume")
        action_shortcut = QKeySequence("Ctrl+S")
        self.edit_resume = self.edit_menu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        action_icon = QIcon("resources/icons/pause.svg")
        action_name = self.tr("Pause")
        action_shortcut = QKeySequence("Ctrl+P")
        self.edit_pause = self.edit_menu.addAction(action_icon, action_name, lambda: None, action_shortcut)

        action_icon = QIcon("resources/icons/stop.svg")
        action_name = self.tr("Stop")
        action_shortcut = QKeySequence("Ctrl+B")
        self.edit_stop = self.edit_menu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        self.edit_menu.addSeparator()
        
        action_icon = QIcon("resources/icons/copy.svg")
        action_name = self.tr("Copy name")
        action_shortcut = QKeySequence("Ctrl+C")
        self.edit_copy_name = self.edit_menu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        action_icon = QIcon("resources/icons/copy.svg")
        action_name = self.tr("Copy hash")
        action_shortcut = QKeySequence("Ctrl+Shift+C")
        self.edit_copy_hash = self.edit_menu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        action_icon = QIcon("resources/icons/copy.svg")
        action_name = self.tr("Copy path")
        action_shortcut = QKeySequence("Ctrl+Shift+P")
        self.edit_copy_path = self.edit_menu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        self.edit_menu.addSeparator()
        
        action_icon = QIcon("resources/icons/files.svg")
        action_name = self.tr("Open in file explorer")
        action_shortcut = QKeySequence("Ctrl+E")
        self.edit_open = self.edit_menu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        action_icon = QIcon("resources/icons/move.svg")
        action_name = self.tr("Move")
        action_shortcut = QKeySequence("Ctrl+M")
        self.edit_move = self.edit_menu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        action_icon = QIcon("resources/icons/remove.svg")
        action_name = self.tr("Remove")
        action_shortcut = QKeySequence("Ctrl+R")
        self.edit_remove = self.edit_menu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        self.addMenu(self.edit_menu)
        
        # settings menu
        self.view_menu = QMenu("&View", self)
        
        self.show_toolbar = QAction(self.tr("Show ToolBar"))
        self.show_statusbar = QAction(self.tr("Show StatusBar"))
        self.show_toolbar.setCheckable(True)
        self.show_statusbar.setCheckable(True)
        self.view_menu.addAction(self.show_toolbar)
        self.view_menu.addAction(self.show_statusbar)
        self.view_menu.addSeparator()
        
        self.show_panel = QAction(self.tr("Show Side Panel"))
        self.panel_tabs = QMenu(self.tr("Select Side Panel Tabs"))
        self.show_panel.setCheckable(True)
        self.view_menu.addAction(self.show_panel)
        self.view_menu.addMenu(self.panel_tabs)
        self.view_menu.addSeparator()
        
        self.detail_tabs = QMenu(self.tr("Select Detail Panel Tabs"))
        self.show_detail = QAction(self.tr("Show Detail Panel"))
        self.show_detail.setCheckable(True)
        self.view_menu.addAction(self.show_detail)
        self.view_menu.addMenu(self.detail_tabs)
        self.view_menu.addSeparator()
        
        self.show_launch = QAction(self.tr("Show Launch Window"))
        self.show_launch.setCheckable(True)
        self.view_menu.addAction(self.show_launch)
        
        self.show_preview = QAction(self.tr("Show Preview Window"))
        self.show_preview.setCheckable(True)
        self.view_menu.addAction(self.show_preview)
        
        self.addMenu(self.view_menu)

        # settings menu
        settingsMenu = QMenu("&Settings", self)
        self.addMenu(settingsMenu)
        
        # settings menu
        self.tools_menu = QMenu("&Tools", self)
        self.addMenu(self.tools_menu)
        
        self.tools_filter = QAction(self.tr("Ip Filter"))
        self.tools_filter.setIcon(QIcon('resources/icons/filter.svg'))
        self.tools_filter.setShortcut("Ctrl+F")
        self.tools_menu.addAction(self.tools_filter)
        
        self.tools_limit = QAction(self.tr("Speed Limit"))
        self.tools_limit.setShortcut("Ctrl+L")
        self.tools_limit.setIcon(QIcon('resources/icons/limit.svg'))
        self.tools_menu.addAction(self.tools_limit)
        
        self.tools_speed = QAction(self.tr("Diagram"))
        self.tools_speed.setShortcut("Ctrl+D")
        self.tools_speed.setIcon(QIcon('resources/icons/chart.svg'))
        self.tools_menu.addAction(self.tools_speed) 
        
        self.tools_statistics = QAction(self.tr("Statistics"))
        self.tools_statistics.setIcon(QIcon('resources/icons/stats.svg'))
        self.tools_statistics.setShortcut("Ctrl+I")
        self.tools_menu.addAction(self.tools_statistics)
        
        # help menu
        helpMenu = QMenu("&Help", self)
        
        action_icon = QIcon("resources/icons/donate.svg")
        self.help_donate = helpMenu.addAction(action_icon, self.tr("Donate"))
        
        action_icon = QIcon("resources/icons/bug.svg")
        self.help_bug = helpMenu.addAction(action_icon, self.tr("Report Bug"))
        
        action_icon = QIcon("resources/icons/thanks.svg")
        self.help_thanks = helpMenu.addAction(action_icon, self.tr("Say Thanks"))
        
        action_icon = QIcon("resources/icons/about.svg")
        self.help_about = helpMenu.addAction(action_icon, self.tr("About peerlink"))
        
        self.addMenu(helpMenu)