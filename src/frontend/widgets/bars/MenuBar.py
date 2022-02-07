from PyQt6.QtGui import QIcon, QKeySequence, QAction
from PyQt6.QtWidgets import QMenuBar, QMenu


class MenuBar(QMenuBar):
    def __init__(self):
        super().__init__()
        
         # file menu
        fileMenu = QMenu("&File", self)
        
        action_icon = QIcon("resources/file.svg")
        action_name = "Open File"
        action_shortcut = QKeySequence("Ctrl+O")
        self.open_file = fileMenu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        action_icon = QIcon("resources/link.svg")
        action_name = "Open Magnet Link"
        action_shortcut = QKeySequence("Ctrl+L")
        self.open_link = fileMenu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        fileMenu.addSeparator()
        
        action_icon = QIcon("resources/new.svg")
        action_name = "Create Torrent File"
        action_shortcut = QKeySequence("Ctrl+N")
        self.create_torrent = fileMenu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        action_icon = QIcon("resources/import.svg")
        action_name = "Import Torrent"
        action_shortcut = QKeySequence("Ctrl+I")
        self.import_torrent = fileMenu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        fileMenu.addSeparator()
        
        action_icon = QIcon("resources/quit.svg")
        action_name = "Exit"
        action_shortcut = QKeySequence("Ctrl+Q")
        self.exit = fileMenu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        self.addMenu(fileMenu)
        
        # edit menu
        self.edit_menu = QMenu("&Edit", self)
        
        action_icon = QIcon("resources/resume.svg")
        action_name = "Resume"
        action_shortcut = QKeySequence("Ctrl+S")
        self.edit_resume = self.edit_menu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        action_icon = QIcon("resources/pause.svg")
        action_name = "Pause"
        action_shortcut = QKeySequence("Ctrl+P")
        self.edit_pause = self.edit_menu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        action_icon = QIcon("resources/move.svg")
        action_name = "Move"
        action_shortcut = QKeySequence("Ctrl+M")
        self.edit_move = self.edit_menu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        self.edit_menu.addSeparator()
        
        action_icon = QIcon("resources/copy.svg")
        action_name = "Copy name"
        action_shortcut = QKeySequence("Ctrl+C")
        self.edit_copy_name = self.edit_menu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        action_icon = QIcon("resources/copy.svg")
        action_name = "Copy hash"
        action_shortcut = QKeySequence("Ctrl+Shift+C")
        self.edit_copy_hash = self.edit_menu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        action_icon = QIcon("resources/copy.svg")
        action_name = "Copy path"
        action_shortcut = QKeySequence("Ctrl+Shift+P")
        self.edit_copy_path = self.edit_menu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        self.edit_menu.addSeparator()
        
        action_icon = QIcon("resources/files.svg")
        action_name = "Open in file explorer"
        action_shortcut = QKeySequence("Ctrl+E")
        self.edit_open = self.edit_menu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        action_icon = QIcon("resources/remove.svg")
        action_name = "Remove"
        action_shortcut = QKeySequence("Ctrl+D")
        self.edit_remove = self.edit_menu.addAction(action_icon, action_name, lambda: None, action_shortcut)
        
        self.addMenu(self.edit_menu)
        
        # settings menu
        self.view_menu = QMenu("&View", self)
        
        self.show_toolbar = QAction("Show ToolBar")
        self.show_statusbar = QAction("Show StatusBar")
        self.show_toolbar.setCheckable(True)
        self.show_statusbar.setCheckable(True)
        self.view_menu.addAction(self.show_toolbar)
        self.view_menu.addAction(self.show_statusbar)
        self.view_menu.addSeparator()
        
        self.show_panel = QAction("Show Side Panel")
        self.panel_tabs = QMenu("Select Side Panel Tabs")
        self.show_panel.setCheckable(True)
        self.view_menu.addAction(self.show_panel)
        self.view_menu.addMenu(self.panel_tabs)
        self.view_menu.addSeparator()
        
        self.detail_tabs = QMenu("Select Detail Panel Tabs")
        self.show_detail = QAction("Show Detail Panel")
        self.show_detail.setCheckable(True)
        self.view_menu.addAction(self.show_detail)
        self.view_menu.addMenu(self.detail_tabs)
        self.view_menu.addSeparator()
        
        self.show_launch = QAction("Show Launch Window")
        self.show_launch.setCheckable(True)
        self.view_menu.addAction(self.show_launch)
        
        self.show_preview = QAction("Show Preview Window")
        self.show_preview.setCheckable(True)
        self.view_menu.addAction(self.show_preview)
        
        self.addMenu(self.view_menu)

        # settings menu
        settingsMenu = QMenu("&Settings", self)
        self.addMenu(settingsMenu)
        
        # settings menu
        self.tools_menu = QMenu("&Tools", self)
        self.addMenu(self.tools_menu)
        
        self.tools_filter = QAction("Ip Filter")
        self.tools_filter.setIcon(QIcon('resources/filter.svg'))
        self.tools_menu.addAction(self.tools_filter)
        
        self.tools_limit = QAction("Speed Limit")
        self.tools_limit.setIcon(QIcon('resources/limit.svg'))
        self.tools_menu.addAction(self.tools_limit)
        
        self.tools_speed = QAction("Diagram")
        self.tools_speed.setIcon(QIcon('resources/chart.svg'))
        self.tools_menu.addAction(self.tools_speed) 
        
        self.tools_statistics = QAction("Statistics")
        self.tools_statistics.setIcon(QIcon('resources/stats.svg'))
        self.tools_menu.addAction(self.tools_statistics)
        
        # help menu
        helpMenu = QMenu("&Help", self)
        
        action_icon = QIcon("resources/donate.svg")
        self.help_donate = helpMenu.addAction(action_icon,  "Donate")
        
        action_icon = QIcon("resources/bug.svg")
        self.help_bug = helpMenu.addAction(action_icon, "Report Bug")
        
        action_icon = QIcon("resources/thanks.svg")
        self.help_thanks = helpMenu.addAction(action_icon, "Say Thanks")
        
        action_icon = QIcon("resources/about.svg")
        self.help_about = helpMenu.addAction(action_icon, "About peerlink")
        
        self.addMenu(helpMenu)