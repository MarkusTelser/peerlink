import sys
from os import chdir
from PyQt6.QtWidgets import QApplication

from __version__ import __version__
from src.frontend.windows.LaunchWindow import LaunchWindow
from src.frontend.windows.ApplicationWindow import ApplicationWindow
from src.frontend.utils.ArgParser import args_parser, args_torrent
from src.frontend.utils.ConfigLoader import ConfigLoader
from src.frontend.utils.AppDataLoader import AppDataLoader


def run():
    if hasattr(sys, '_MEIPASS'):
        chdir(sys._MEIPASS)
        print(sys._MEIPASS)

    app = QApplication(sys.argv)
    app.setApplicationName('peerlink')
    app.setApplicationVersion(__version__)
    app.setStyleSheet(open('resources/themes/MainTheme.qss').read())
    
    args = args_parser()
    conf = ConfigLoader()
    app_data  = AppDataLoader()
    torrent_list = app_data.load_torrents()
    arg_torrents = args_torrent(args)
    
    
    # decide which window to load depending on settings
    if conf.show_launch and len(torrent_list) == 0 and len(arg_torrents) == 0:
        window = LaunchWindow(conf)
    else:
        window = ApplicationWindow(conf)
        
        # load app data torrents from previous sessions
        window.load_torrents(torrent_list)
        
        # load console argument torrents
        if len(arg_torrents) != 0:
            for torrent, extras in arg_torrents:
                window.appendRowEnd(torrent, extras)
    
    window.show()

    sys.exit(app.exec())
    
if __name__ == '__main__':
    run()