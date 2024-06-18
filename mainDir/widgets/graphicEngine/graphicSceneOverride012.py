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

        # Buffer circolare per i frame
        self.buffer_size = buffer_size
        self.frame_buffer = [None] * buffer_size
        self.buffer_head = 0
        self.buffer_tail = 0
        self.buffer_full = False

    def setResolution(self, size: QSize):
        self._resolution = size

    def setFps(self, value):
        self._fps = value

    def add_frame_to_buffer(self, frame):
        self.frame_buffer[self.buffer_head] = frame
        if self.buffer_full:
            self.buffer_tail = (self.buffer_tail + 1) % self.buffer_size
        self.buffer_head = (self.buffer_head + 1) % self.buffer_size
        self.buffer_full = self.buffer_head == self.buffer_tail

    def get_latest_frame_from_buffer(self):
        if self.buffer_full or self.buffer_head != self.buffer_tail:
            return self.frame_buffer[(self.buffer_head - 1) % self.buffer_size]
        else:
            return None

    def getDirtyFrameOLD(self):
        image = QImage(self._resolution, QImage.Format.Format_BGR888)
        painter = QPainter(image)
        self.advance()
        self.render(painter)
        painter.end()

        ptr = image.bits()
        ptr.setsize(image.byteCount())
        frame = np.array(ptr).reshape(image.height(), image.width(), 3)

        # Aggiungi il frame al buffer circolare
        self.add_frame_to_buffer(frame)

        # Restituisci il frame corrente
        return frame

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
        ptr.setsize(image.byteCount())
        frame = np.array(ptr).reshape(image.height(), image.width(), 3)

        # Aggiungi il frame al buffer circolare (se esiste)
        self.add_frame_to_buffer(frame)

        # Restituisce il frame corrente come matrice NumPy
        return frame

    def getBufferedFrame(self):
        # Restituisci l'ultimo frame dal buffer circolare
        frame = self.get_latest_frame_from_buffer()
        if frame is not None:
            return frame
        else:
            return np.zeros((self._resolution.height(), self._resolution.width(), 3), dtype=np.uint8)
