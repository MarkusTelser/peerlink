from PyQt6.QtWidgets import QMessageBox, QInputDialog
from PyQt6.QtCore import QCoreApplication

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

def convert_detail_sec(seconds: int):
    sec_str = ""
    if seconds >= 86400:
        sec_str += f"{round(seconds / 86400, 1)} d"
    if seconds >= 3600:
        sec_str += f" {round(seconds / 3600, 2)} h"
    if seconds >= 60:
        sec_str += f" {int(seconds / 60)} min"
    sec_str += f"  {seconds % 60} s"
    return sec_str
    

def to_seconds(time: str):
    index = ['s', 'min', 'h', 'd']
    units = [1, 60, 3600, 86400]
    count, unit = time.split(' ')
    return int(count) * units[index.index(unit)]

def showError(error, parent):
    error_window = QMessageBox(parent)
    error_window.geometry().moveCenter(parent.geometry().center())
    error_window.setIcon(QMessageBox.Icon.Critical)
    error_window.setText(error)
    error_window.setWindowTitle(QCoreApplication.translate("ErrorDialog", "Error - PeerLink"))
    error_window.show()
    
def showInput(text, parent):
    input_dialog = QInputDialog()
    input_dialog.geometry().moveCenter(parent.geometry().center())
    input_dialog.setWindowTitle(QCoreApplication.translate("InputDialog", "Input - Peerlink"))
    input_dialog.setLabelText(text)
    return input_dialog