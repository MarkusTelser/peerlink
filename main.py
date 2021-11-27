from PyQt6.QtWidgets import QApplication
from src.frontend import StartWindow
import sys

app = QApplication(sys.argv)

window = StartWindow()
window.show()

sys.exit(app.exec())