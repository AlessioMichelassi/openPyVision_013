from PyQt6.QtCore import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *


class GraphicViewOverride(QGraphicsView):
    _currentScale = 0.36
    currentItem = None
    _isPanning = False
    _lastMiddleMousePosition = QPoint()
    currentScaleChange = pyqtSignal(float, name="currentScale")

    def __init__(self, _scene, parent=None):
        super().__init__(_scene, parent)
        self.initRenderHints()

    def initRenderHints(self):
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

    def turnOnOpenGL(self, _bool):
        if _bool:
            self.setViewport(QOpenGLWidget(self))
        else:
            self.setViewport(QWidget(self))

    def mousePressEvent(self, event, _QMouseEvent=None):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.MiddleButton:
            self.mouseMiddlePressEvent(event)

    def mouseMoveEvent(self, event, _QMouseEvent=None):
        super().mouseMoveEvent(event)
        if self._isPanning:
            self.panTheScene(event)

    def mouseReleaseEvent(self, event, _QMouseEvent=None):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.MiddleButton:
            self.mouseMiddleReleaseEvent(event)

    # -------------------------- mouse events --------------------------

    def mouseMiddlePressEvent(self, event):
        self._isPanning = True
        self._lastMiddleMousePosition = event.pos()
        self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMiddleReleaseEvent(self, event):
        self._isPanning = False
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def panTheScene(self, event):
        currentPosition = event.pos()
        deltaPosition = currentPosition - self._lastMiddleMousePosition
        self._lastMiddleMousePosition = currentPosition
        hsBarValue = self.horizontalScrollBar().value()
        self.horizontalScrollBar().setValue(int(hsBarValue - deltaPosition.x()))
        vsBarValue = self.verticalScrollBar().value()
        self.verticalScrollBar().setValue(int(vsBarValue - deltaPosition.y()))
        event.accept()

    def wheelEvent(self, event, _QMouseEvent=None):
        self.scaleTheScene(1.1 if event.angleDelta().y() > 0 else 0.9)

    def scaleTheScene(self, scaleFactor):
        currentScale = self.transform().m11()
        if 0.13 < currentScale < 15:
            self.scale(scaleFactor, scaleFactor)
        elif currentScale <= 0.4:
            self.scale(0.5 / currentScale, 0.5 / currentScale)
        else:
            self.scale(0.8, 0.8)

        self.currentScaleChange.emit(self.transform().m11())

    def fitInView(self, rect=None, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio):
        if rect is None:
            rect = self.sceneRect()
        self.setSceneRect(rect)
        unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
        self.scale(1 / unity.width(), 1 / unity.height())
        viewRect = self.viewport().rect()
        sceneRect = self.transform().mapRect(rect)
        factor = min(viewRect.width() / sceneRect.width(), viewRect.height() / sceneRect.height())
        self.scale(factor, factor)
        self.centerOn(rect.center())
        self.currentScaleChange.emit(self.transform().m11())


if __name__ == "__main__":
    app = QApplication([])
    scene = QGraphicsScene()
    scene.setBackgroundBrush(QColor(19, 19, 19))
    view = GraphicViewOverride(scene)
    view.initRenderHints()

    source = QGraphicsPixmapItem(QPixmap(r"C:\pythonCode\openPyVision_013\testImage"))
    scene.addItem(source)
    view.show()
    app.exec()
