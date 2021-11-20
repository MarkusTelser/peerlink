from PyQt6.QtWidgets import QMainWindow

class LoadWindow(QMainWindow):
    def __init__(self, parent=None):
        super(LoadWindow, self).__init__(parent)
        self.setWindowTitle("FastPeer - LoadPage")

        