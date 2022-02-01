import sys
from PyQt6.QtWidgets import QApplication

from src.frontend.windows.LaunchWindow import LaunchWindow
from src.frontend.windows.ApplicationWindow import ApplicationWindow
from src.frontend.utils.ArgParser import args_parser
from src.frontend.utils.ConfigLoader import ConfigLoader
from src.frontend.utils.AppDataLoader import AppDataLoader


def run():
    app = QApplication(sys.argv)
    app.setApplicationName('peerlink')
    app.setApplicationVersion('0.1')
    app.setStyleSheet(open('resources/themes/custom.qss').read())
    
    args = args_parser()
    conf = ConfigLoader()
    app_data  = AppDataLoader()
    torrent_list = app_data.load_torrents()
    
    if args['p'] != None or args['m'] != None:
        # received file-path in args, open MainWindow
        if args['p'] != None:
            print('filepath', args['p'])
        # received magnet-link in args, open MainWindow
        if args['m'] != None:
            print('magnet link', args['m'])
    
        sys.exit(app.exec())
    # decide which window to load depending on settings
    elif conf.show_launch and len(torrent_list) == 0:
        window = LaunchWindow(conf)
    else:
        window = ApplicationWindow(conf)
        window.load_torrents(torrent_list)
    
    window.show()

    sys.exit(app.exec())
    
if __name__ == '__main__':
    run()