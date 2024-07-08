from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


class SelectableProxyWidget(QGraphicsProxyWidget):
    def __init__(self, widget, parent=None):
        super().__init__(parent)
        self.setWidget(widget)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setAcceptHoverEvents(True)
        self.selectionRect = None

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        if self.isSelected():
            pen = QPen(QColor('red'), 2)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def hoverEnterEvent(self, event):
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.update()
        super().hoverLeaveEvent(event)
