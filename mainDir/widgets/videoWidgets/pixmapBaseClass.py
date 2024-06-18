from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class PixmapBaseClass(QGraphicsPixmapItem):
    _resolution: QSize = QSize(1920, 1080)
    _fps = 60
    _video_input = 4
    _limitCapture = 1
    _frameNp = None
    _alpha = 1

    def __init__(self, _resolution=QSize(1920, 1080), _video_input=4):
        super().__init__()
        self._resolution = _resolution
        self._video_input = _video_input

    def updatePixmap(self):
        raise NotImplementedError

    def video_input(self):
        return self._video_input

    def setVideoInput(self, value):
        self._video_input = value

    @property
    def qImage(self):
        raise NotImplementedError

    def paint(self, painter, _QPainter=None, *args, **kwargs):
        raise NotImplementedError

    @property
    def opacity(self):
        return self._alpha

    @opacity.setter
    def opacity(self, value):
        if 0 <= value <= 1:
            self._alpha = value
            self.update()
