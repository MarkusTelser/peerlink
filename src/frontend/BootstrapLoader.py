from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from src.frontend.ArgParser import args_parser
from src.frontend.windows.StartWindow import StartWindow
from src.frontend.windows.ApplicationWindow import ApplicationWindow
from src.frontend.ConfigLoader import ConfigLoader
import sys


def run():
    app = QApplication(sys.argv)
    app.setApplicationName('peerlink')
    app.setOrganizationName('peerlink')
    app.setApplicationVersion('0.1')
    
    args = args_parser()
    
    #app.setStyleSheet(open('resources/themes/gradienttheme.qss').read())
    
    if args['p'] != None or args['m'] != None:
        # received file-path in args, open MainWindow
        if args['p'] != None:
            print('filepath', args['p'])
        # received magnet-link in args, open MainWindow
        if args['m'] != None:
            print('magnet link', args['m'])
    
        sys.exit(app.exec())
    
    
    conf = ConfigLoader()
    
    # decide which window to load depending on settings
    window = ApplicationWindow(conf)
    window.show()

    sys.exit(app.exec())