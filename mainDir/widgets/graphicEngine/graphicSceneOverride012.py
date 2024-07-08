import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class GraphicSceneOverride012(QGraphicsScene):
    _resolution = QSize(1920, 1080)
    _fps = 60
    _index = 0
    _showGrid = False
    _showResolutionGuide = False

    colorBackground: QColor = QColor(39, 39, 39, 255)
    greyLighter: QColor = QColor(47, 47, 47, 255)
    greyDarker: QColor = QColor(29, 29, 29, 255)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBackgroundBrush(QColor(19, 19, 19))
        self.setSceneRect(0, 0, self._resolution.width(), self._resolution.height())

        # set the grid Size
        self.smallGridSize = 10
        self.bigGridSize = 50

        # set the color of the scene
        self.setBackgroundBrush(self.colorBackground)
        self._penLight = QPen(self.greyLighter)
        self._penLight.setWidth(1)
        self._penDark = QPen(self.greyDarker)
        self._penDark.setWidth(2)
        self._penResolutionGuide = QPen(QColor(255, 0, 0, 180), 4)

    def setResolution(self, size: QSize):
        self._resolution = size
        self.setSceneRect(0, 0, self._resolution.width(), self._resolution.height())

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:
        if self._showResolutionGuide:
            self.drawResolutionGuide(painter)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        if self._showGrid:
            self.drawGrid(painter, rect)

    def addImage(self, item):
        self.addItem(item)
        item.setPos(0, 0)  # Posiziona l'immagine in (0, 0)
        return item

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

    def showGrid(self, show=True):
        self._showGrid = show
        self.update()

    def showResolutionGuide(self, show=True):
        self._showResolutionGuide = show
        self.update()

    def drawGrid(self, painter, rect):
        _left = int(rect.left())
        _right = int(rect.right())
        _top = int(rect.top())
        _bottom = int(rect.bottom())
        lightGreyLines, darkGreyLines = [], []
        firstVerticalLine = _left - (_left % self.smallGridSize) - 20
        firstHorizontalLine = _top - (_top % self.smallGridSize) - 20

        for x in range(firstVerticalLine, _right, self.smallGridSize):
            if x % self.bigGridSize == 0:
                darkGreyLines.append(QLine(x, _top, x, _bottom))
            else:
                lightGreyLines.append(QLine(x, _top, x, _bottom))

        for y in range(firstHorizontalLine, _bottom, self.smallGridSize):
            if y % self.bigGridSize == 0:
                darkGreyLines.append(QLine(_left, y, _right, y))
            else:
                lightGreyLines.append(QLine(_left, y, _right, y))
        painter.setPen(self._penLight)
        painter.drawLines(*lightGreyLines)
        painter.setPen(self._penDark)
        if darkGreyLines:
            painter.drawLines(*darkGreyLines)

    def drawResolutionGuide(self, painter):
        painter.setPen(self._penResolutionGuide)
        painter.drawRect(0, 0, self._resolution.width(), self._resolution.height())

    def snapToGrid(self, x, y):
        return [self.smallGridSize * round(x / self.smallGridSize), self.smallGridSize * round(y / self.smallGridSize)]
