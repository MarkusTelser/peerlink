import sys
from PyQt6.QtWidgets import QApplication

from src.frontend.windows.StartWindow import StartWindow
from src.frontend.windows.ApplicationWindow import ApplicationWindow
from src.frontend.utils.ArgParser import args_parser
from src.frontend.utils.ConfigLoader import ConfigLoader
from src.frontend.utils.AppDataLoader import AppDataLoader


def run():
    app = QApplication(sys.argv)
    app.setApplicationName('peerlink')
    #app.setOrganizationName('peerlink')
    app.setApplicationVersion('0.1')
    app.setStyleSheet(open('resources/themes/custom.qss').read())
    
    args = args_parser()
    
    if args['p'] != None or args['m'] != None:
        # received file-path in args, open MainWindow
        if args['p'] != None:
            print('filepath', args['p'])
        # received magnet-link in args, open MainWindow
        if args['m'] != None:
            print('magnet link', args['m'])
    
        sys.exit(app.exec())
    
    
    conf = ConfigLoader()
    app_data  = AppDataLoader()
    torrent_list = app_data.load_torrents()
    
    # decide which window to load depending on settings
    if len(torrent_list) != 0:  
        window = ApplicationWindow(conf)
        #window.appendRowEnd(torrent_list)
    else:
        window = StartWindow(conf)
    window.show()

    sys.exit(app.exec())
    
if __name__ == '__main__':
    run()