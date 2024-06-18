import cv2
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.widgets.videoWidgets.pixmapBaseClass import PixmapBaseClass


class WaveForm(PixmapBaseClass):
    image_rgb = None
    _pixmap: QPixmap = None

    def __init__(self, source, _resolution=QSize(640, 360), _video_input=4, _limitCapture=1):
        super().__init__(_resolution, _video_input)
        self.name = "utilitySignal"
        self.source = source
        self.resolution = _resolution
        self.setOpacity(0.5)
        self.fps = 30
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(1000 // self.fps)

    def __del__(self):
        self.timer.stop()

    def start(self):
        self.timer.start(1000 // self.fps)

    def stop(self):
        self.timer.stop()

    @property
    def pixmap(self):
        if self._pixmap is None:
            self.updateFrame()
        return self._pixmap

    @pixmap.setter
    def pixmap(self, value):
        self._pixmap = value
        self.prepareGeometryChange()
        self.update()

    def boundingRect(self):
        if self.pixmap is None:
            return QRectF(0, 0, 1920, 1080)
        return QRectF(0, 0, self.pixmap.width(), self.pixmap.height())

    def createWaveformPixmap(self):
        self.image_rgb = cv2.cvtColor(self.image_rgb, cv2.COLOR_BGR2GRAY)
        height, width = self.resolution.height(), self.resolution.width()
        waveform_image = QImage(width, height, QImage.Format.Format_RGB888)
        waveform_image.fill(Qt.GlobalColor.black)

        painter = QPainter(waveform_image)
        painter.setPen(Qt.GlobalColor.white)

        for x in range(width):
            column_data = self.image_rgb[:, x]
            average_luminance = np.mean(column_data)
            y = int((average_luminance / 255) * height)
            painter.drawLine(x, height, x, height - y)

        painter.end()
        return QPixmap.fromImage(waveform_image)

    def updateFrame(self):
        self.image_rgb = cv2.cvtColor(self.source.frameNp, cv2.COLOR_BGR2RGB)
        self.pixmap = self.createWaveformPixmap()
        self.update()

    def paint(self, painter, _QPainter=None, *args, **kwargs):
        if self.pixmap:
            srcRect = QRectF(0, 0, self.pixmap.width(), self.pixmap.height())
            destRect = self.boundingRect()
            painter.drawPixmap(destRect, self.pixmap, srcRect)
