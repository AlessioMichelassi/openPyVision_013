import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class GraphicSceneOverride012(QGraphicsScene):
    _resolution = QSize(1920, 1080)
    _fps = 60
    _index = 0

    def __init__(self, buffer_size=10, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QColor(19, 19, 19))
        self.setSceneRect(0, 0, self._resolution.width(), self._resolution.height())

    def setResolution(self, size: QSize):
        self._resolution = size

    def setFps(self, value):
        self._fps = value

    def getDirtyFrame(self):
        # Creazione dell'immagine con la risoluzione specificata
        image = QImage(self._resolution, QImage.Format.Format_BGR888)

        # Utilizzo di QPainter per disegnare sulla QImage
        painter = QPainter(image)
        self.advance()
        self.render(painter)
        painter.end()

        # Conversione della QImage in una matrice NumPy
        ptr = image.bits()
        ptr.setsize(image.sizeInBytes())
        frame = np.array(ptr).reshape(image.height(), image.width(), 3)

        # Restituisce il frame corrente come matrice NumPy
        return frame
