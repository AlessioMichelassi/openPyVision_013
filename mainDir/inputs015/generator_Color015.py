from PyQt6.QtCore import *
from PyQt6.QtGui import *

from mainDir.inputs015.baseClass015 import BaseClass015


class ColorGenerator015(BaseClass015):
    _color = QColor(250, 0, 0)  # Colore iniziale: rosso

    def __init__(self, synchObject, resolution=QSize(1920, 1080)):
        super().__init__(synchObject, resolution)
        self.setColor(self._color)  # Inizializza l'immagine con il colore specificato

    def setColor(self, color: QColor):
        self._color = color
        self._frame[:, :] = [color.blue(), color.green(), color.red()]

    def captureFrame(self):
        super().captureFrame()

    def getFrame(self):
        return super().getFrame()


