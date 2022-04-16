import sys
import time
from threading import Thread
from PyQt6.QtWidgets import QProgressBar, QApplication, QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QToolTip
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPaintEvent, QBrush, QResizeEvent, QKeyEvent, QMouseEvent, QCursor
from PyQt6.QtCore import Qt, pyqtSlot, QRect, QSize, QEvent

from src.backend.peer_protocol.PieceManager import Piece

class ToolTip(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("PartProgressToolTip")
        self.setWindowFlag(Qt.WindowType.ToolTip)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.label = QLabel("shows which pieces have been downloaded")
        layout.addWidget(self.label)

    def setText(self, id: str):
        if id != None:
            self.label.setText(f"Piece with {id}")
        else:
            self.label.setText("shows which pieces have been downloaded")

class _Progress(QWidget):
    MARGIN = 2
    BORDER_COLOR = QColor(0, 0, 0)
    FONT_COLOR = QColor(255, 255, 255)
    STARTED_COLOR = QColor(255,215,0)
    FINISHED_COLOR = QColor(50,205,50)

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._tooltip = ToolTip(self)
        self._values = list()
        self._progress = 0
        self._range = (0, 100)
    
    def currentId(self):
        x_cor = self.mapFromGlobal(QCursor.pos()).x()
        part_width = (self.width() - 2 * self.MARGIN) / self._range[1]
        if x_cor < self.MARGIN or self.width() - self.MARGIN < x_cor:
            return None 
        return int((x_cor - self.MARGIN) / part_width) + 1

    @pyqtSlot(QPaintEvent)
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        
        # draw progress or health bars in fittig color
        if len(self._values) != 0 and type(self._values[0]) == int:
            self._iter_int_values(painter)
        elif len(self._values) != 0 and type(self._values[0]) == Piece:
            self._iter_piece_values(painter)
        
        # draw progress text in the middle of the screen
        painter.setPen(self.FONT_COLOR)
        painter.setBrush(self.FONT_COLOR)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{self._progress}%")

        # draw the border of the progress bar
        pen = QPen(self.BORDER_COLOR, self.MARGIN)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(QColor(0, 0, 0, 0))
        painter.drawRect(int(self.MARGIN / 2), int(self.MARGIN / 2), self.width() - self.MARGIN, self.height() - self.MARGIN)

        painter.end()
        super().paintEvent(event)

    def _iter_int_values(self, painter):
        part_width = (self.width() - 2 * self.MARGIN) / self._range[1]
        painter.setPen(self.FINISHED_COLOR)
        painter.setBrush(self.FINISHED_COLOR)
        for value in self._values:
            if self._range[0] <= value and value < self._range[1]:
                painter.drawRect(int(part_width * value + self.MARGIN), self.MARGIN, int(part_width), self.height() - (2 * self.MARGIN))

    def _iter_piece_values(self, painter):
        part_width = (self.width() - 2 * self.MARGIN) / self._range[1]
        for value in self._values:
            if self._range[0] > value.index or value.index > self._range[1]:
                continue
            if value.status == 'PENDING':
                continue
            
            if value.status == 'STARTED':
                painter.setPen(self.STARTED_COLOR)
                painter.setBrush(self.STARTED_COLOR)
            elif value.status == 'FINISHED':
                painter.setPen(self.FINISHED_COLOR)
                painter.setBrush(self.FINISHED_COLOR)
            
            painter.drawRect(int(part_width * value.index + self.MARGIN), self.MARGIN, int(part_width), self.height() - (2 * self.MARGIN))

    @pyqtSlot(QEvent)
    def event(self, event: QEvent):
        if event.type() == QEvent.Type.FocusOut:
            cursor_pos = self.mapFromGlobal(QCursor.pos())
            if not self.rect().contains(cursor_pos):
                self._tooltip.hide()
        if event.type() == QEvent.Type.ToolTip:
            self._tooltip.setText(self.currentId())
            self._tooltip.move(event.globalX(), event.globalY())
            self._tooltip.show()
        return super().event(event)

    @pyqtSlot(QKeyEvent)
    def keyPressEvent(self, event: QKeyEvent):
        print('KEYY')
        if event.key() == Qt.Key.Key_Shift:
            print('SHIFT')
        super().keyPressEvent(event)

    @pyqtSlot(QEvent)
    def enterEvent(self, event: QEvent):
        self.setFocus(Qt.FocusReason.OtherFocusReason)
        super().enterEvent(event)

    @pyqtSlot(QEvent)
    def leaveEvent(self, event: QEvent):
        self.clearFocus()
        super().leaveEvent(event)
    

class PartProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setToolTip('')
        self.setObjectName("PartProgress")
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumHeight(30)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        self.progress = _Progress(self)
        layout.addWidget(self.progress)
    
    def clear(self):
        self.progress._values = list()
        self.repaint()

    def setValues(self, progress, values):
        self.progress._progress = progress
        self.progress._values = values
        self.repaint()

    def setRange(self, start, end):
        self.progress._range = (start, end)
        self.repaint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    
    main_widget = QWidget()
    
    layout = QVBoxLayout()
    main_widget.setLayout(layout)
    window.setCentralWidget(main_widget)
    
    part = PartProgress()
    l = [0, 1, 2, 3 ,4, 50, 52, 60, 99, 100]
    p = [Piece(x, 0, 1, 'FINISHED') for x in l]
    p2 = [Piece(0, 0, 1, 'FINISHED'), Piece(1, 0, 1, 'STARTED'), Piece(2, 0, 1, 'FINISHED'), Piece(3, 0, 1, 'STARTED'), Piece(4, 0, 1, 'FINISHED')]
    part.setValues(len(p) / 138, p2)
    part.setBaseSize(1000, 200)
    layout.addWidget(part)

    bar = QProgressBar()
    bar.setValue(50)
    layout.addWidget(bar)
    
    window.show()

    sys.exit(app.exec())