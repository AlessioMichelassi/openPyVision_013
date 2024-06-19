from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class ColorLabel(QLabel):
    deviceChanged = pyqtSignal(dict, name="colorLabelChanged")

    def __init__(self, startColor=QColor(255, 0, 0), parent=None):
        super().__init__(parent)
        self.setMinimumWidth(30)
        self.setStyleSheet(f"background-color: rgb({startColor.red()}, {startColor.green()}, {startColor.blue()})")
        self.setFrameShape(QFrame.Shape.Panel)
        self._colorDictionary = {"color": {"r": startColor.red(), "g": startColor.green(), "b": startColor.blue()}}

    def mouseDoubleClickEvent(self, event):
        color = QColorDialog.getColor()
        if color.isValid():
            self.setStyleSheet(f"background-color: {color.name()}")
            self.colorDictionary = {"color": {"r": color.red(), "g": color.green(), "b": color.blue()}}
            self.deviceChanged.emit(self.colorDictionary)

    @property
    def colorDictionary(self):
        return self._colorDictionary

    @colorDictionary.setter
    def colorDictionary(self, value):
        self._colorDictionary = value
        self.setStyleSheet(
            f"background-color: rgb({value['color']['r']}, {value['color']['g']}, {value['color']['b']})")