from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from src.frontend.windows.StartWindow import StartWindow
from src.frontend.windows.ApplicationWindow import ApplicationWindow
from src.frontend.ConfigLoader import ConfigLoader
import sys


app = QApplication(sys.argv)
app.setApplicationName('peerlink')
app.setOrganizationName('peerlink')
app.setApplicationVersion('0.1')

conf = ConfigLoader()

# decide which window to load depending on settings
window = ApplicationWindow(conf)
window.show()

sys.exit(app.exec())