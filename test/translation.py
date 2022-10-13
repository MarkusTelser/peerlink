from PyQt6.QtCore import QTranslator, QCoreApplication, QLocale, QCoreApplication
from PyQt6.QtWidgets import QApplication, QPushButton
import sys

app = QApplication(sys.argv)

def tr(text: str):
    return QCoreApplication.translate('', text)

translator = QTranslator()
if translator.load("hellotr_la", "/home/carlos/Code/Python/peerlink"):
    QCoreApplication.installTranslator(translator)
else:
    print('not loaded')

print(QPushButton.tr('Hello world!'))
print(QTranslator.tr('Hello world!'))
print(QApplication.tr('Hello world!'))
print(QCoreApplication.tr('Hello world!'))
print(QCoreApplication.translate('QPushButton','Hello world!'))
print(QCoreApplication.translate('','Hello world!'))
print(tr('Hello world!'))

sys.exit(app.exec())