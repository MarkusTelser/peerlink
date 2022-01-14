from PyQt6.QtWidgets import QApplication
from src.frontend.windows.StartWindow import StartWindow
import sys
 
app = QApplication(sys.argv)

window = StartWindow()
window.show()

sys.exit(app.exec())