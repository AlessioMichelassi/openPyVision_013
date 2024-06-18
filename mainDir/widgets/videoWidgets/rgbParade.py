import cv2
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.widgets.videoWidgets.pixmapBaseClass import PixmapBaseClass


class RGBParade(PixmapBaseClass):
    image_rgb = None
    _pixmap: QPixmap = None

    def __init__(self, source, _resolution=QSize(1920, 1080), _video_input=None):
        super().__init__(_resolution, _video_input)
        self.name = "utilitySignal"
        self.source = source
        self.setOpacity(0.5)
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(1000 // 10)

    def __del__(self):
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
        if self.pixmap.isNull():
            return QRectF(0, 0, 1920, 1080)
        return QRectF(0, 0, self.pixmap.width(), self.pixmap.height())

    def createHistogram(self, channel, color, height=300, width=1920):
        avg_values = channel.mean(axis=0)
        max_height = height - 10  # Margin
        scale = max_height / 255.0

        # Creazione dell'immagine per il singolo canale
        channel_image = QImage(width, height, QImage.Format.Format_RGB888)
        channel_image.fill(Qt.GlobalColor.black)
        channel_painter = QPainter(channel_image)
        channel_painter.setPen(color)

        for x, val in enumerate(avg_values):
            if x < width:  # Evita di disegnare fuori dai confini
                y = int(val * scale)
                channel_painter.drawLine(x, height - 5, x, height - y - 5)

        # Disegna la griglia per ogni sezione
        pen = QPen(Qt.GlobalColor.white)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setWidth(1)
        channel_painter.setPen(pen)
        channel_painter.setOpacity(0.5)

        num_lines = 10  # Aumenta il numero di linee della griglia per una rappresentazione più precisa
        for j in range(num_lines + 1):
            y = int(height - 5 - j * max_height / num_lines)
            channel_painter.drawLine(0, y, width, y)
            channel_painter.drawText(5, y - 2, f"{int(255 - j * 255 / num_lines)}")

        channel_painter.end()

        return channel_image

    def createParadePixmap(self):
        R, G, B = cv2.split(self.image_rgb)
        width, height = 1920, 300  # Dimensioni della QImage per il RGB Parade
        parade_image = QImage(width, height * 3, QImage.Format.Format_RGB888)

        painter = QPainter(parade_image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        channels = [R, G, B]
        colors = [Qt.GlobalColor.red, Qt.GlobalColor.green, Qt.GlobalColor.blue]

        for i, (channel, color) in enumerate(zip(channels, colors)):
            channel_image = self.createHistogram(channel, color, height, width)
            painter.drawImage(0, i * height, channel_image)

        painter.end()
        return QPixmap.fromImage(parade_image)

    def updateFrame(self):
        self.image_rgb = cv2.cvtColor(self.source, cv2.COLOR_BGR2RGB)
        self.pixmap = self.createParadePixmap()
        self.update()

    def paint(self, painter, _QPainter=None, *args, **kwargs):
        if self.pixmap is not None:
            srcRect = QRectF(0, 0, self.pixmap.width(), self.pixmap.height())
            destRect = self.boundingRect()
            painter.drawPixmap(destRect, self.pixmap, srcRect)
