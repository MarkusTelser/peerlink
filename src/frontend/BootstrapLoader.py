import sys
from os import chdir
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTranslator, QLocale, QLibraryInfo

from __version__ import __version__
from src.frontend.windows.LaunchWindow import LaunchWindow
from src.frontend.windows.ApplicationWindow import ApplicationWindow
from src.frontend.utils.ArgParser import args_parser, args_torrent, args_magnet
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

    # load the system translations provided by qt
    qtTranslator = QTranslator()
    qtTranslator.load("qt_de", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath))
    app.installTranslator(qtTranslator)

    # load custom translations for this application
    translator = QTranslator()
    translator.load(QLocale(), 'resources/languages/qt_de.qm')
    app.installTranslator(translator)
    
    args = args_parser()
    conf = ConfigLoader()
    app_data  = AppDataLoader()
    torrent_list = app_data.load_torrents()
    arg_torrents = args_torrent(args)
    arg_magnets = args_magnet(args)

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
                window.appendTorrent(torrent, extras)

        # load console argument magnet links
        if len(arg_magnets) != 0:
            for magnet, extras in arg_magnets:
                window.appendTorrent(magnet, extras)
    
    window.show()

    sys.exit(app.exec())
    
if __name__ == '__main__':
    run()