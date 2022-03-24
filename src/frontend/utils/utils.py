from PyQt6.QtWidgets import QMessageBox

def convert_bits(bits: int):
    if bits < 1000:
        return f"{bits} B"
    if bits / 1024 < 1000:
        return f"{int(round(bits / 1024, 0))} KiB"
    elif bits / (1024 ** 2) < 1000:
        return f"{round(bits / (1024 ** 2), 1)} MiB"
    elif bits  / (1024 ** 3) < 1000:
        return f"{round(bits / (1024 ** 3), 2)} GiB"
    elif bits / (1024 ** 4) < 1000: 
        return f"{round(bits / (1024 ** 4), 2)} TiB"
    elif bits / (1024 ** 5) < 1000:
        return f"{round(bits / (1024 ** 5), 3)} PiB"

def convert_bitsps(bits: int):
    if bits < 1000:
        return f"{int(bits)} B/s"
    if bits / 1024 < 1000:
        return f"{int(round(bits / 1024, 0))} KiB/s"
    elif bits / (1024 ** 2) < 1000:
        return f"{round(bits / (1024 ** 2), 1)} MiB/s"
    elif bits  / (1024 ** 3) < 1000:
        return f"{round(bits / (1024 ** 3), 2)} GiB/s"
    elif bits / (1024 ** 4) < 1000: 
        return f"{round(bits / (1024 ** 4), 2)} TiB/s"
    elif bits / (1024 ** 5) < 1000:
        return f"{round(bits / (1024 ** 5), 3)} PiB/s"

def convert_seconds(seconds: int):
    if seconds < 60:
        return f"{seconds} s"
    elif seconds < 3600:
        return f"{int(seconds / 60)} min"
    elif seconds < 86400:
        return f"{round(seconds / 3600, 2)} h"
    else:
        return f"{round(seconds / 86400, 1)} d"

def showError(error, parent=None):
    error_window = QMessageBox(parent)
    error_window.setIcon(QMessageBox.Icon.Critical)
    error_window.setText(error)
    error_window.setWindowTitle("Error - PeerLink")
    error_window.show()
    