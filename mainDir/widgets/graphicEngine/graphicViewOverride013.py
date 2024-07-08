from enum import Enum
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import *

from mainDir.widgets.graphicEngine.graphicSceneOverride012 import GraphicSceneOverride012


class viewportUpdateMode(Enum):
    FullViewportUpdate = QGraphicsView.ViewportUpdateMode.FullViewportUpdate
    MinimalViewportUpdate = QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate
    SmartViewportUpdate = QGraphicsView.ViewportUpdateMode.SmartViewportUpdate
    NoViewportUpdate = QGraphicsView.ViewportUpdateMode.NoViewportUpdate

class GraphicViewOverride013(QGraphicsView):
    _currentScale = 0.36
    currentItem = None
    _isPanning = False
    _lastMiddleMousePosition = QPoint()
    currentScaleChange = pyqtSignal(float, name="currentScale")
    shiftPressed = False
    ctrlPressed = False
    lastPos: QPointF = None
    deltaPos: QPointF = None
    snapThreshold = 50  # Threshold for snapping

    def __init__(self, _scene, parent=None):
        super().__init__(_scene, parent)
        self.initRenderHints()
        self.isEditorModality = False

    def initRenderHints(self):
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

    def setSmoothPixmapTransform(self, _bool):
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, _bool)

    def setAntialiasing(self, _bool):
        self.setRenderHint(QPainter.RenderHint.Antialiasing, _bool)

    def setViewportUpdate(self, mode: viewportUpdateMode):
        self.setViewportUpdateMode(mode.value)

    def setDontSavePainterState(self, _bool):
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontSavePainterState, _bool)

    def turnOnOpenGL(self, _bool):
        if _bool:
            self.setViewport(QOpenGLWidget(self))
        else:
            self.setViewport(QWidget(self))

    def setEditorModality(self, _bool):
        self.isEditorModality = _bool
        self.shiftPressed = False
        self.ctrlPressed = False
        if _bool:
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.setMouseTracking(True)
            self.setSmoothPixmapTransform(True)
            self.setAntialiasing(True)
            self.setViewportUpdate(viewportUpdateMode.FullViewportUpdate)
            #setCacheMode
            self.setCacheMode(QGraphicsView.CacheModeFlag.CacheBackground)
            self.turnOnOpenGL(True)
        else:
            self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.setMouseTracking(False)
            self.setSmoothPixmapTransform(False)
            self.setAntialiasing(False)
            self.setViewportUpdate(viewportUpdateMode.MinimalViewportUpdate)
            self.setDontSavePainterState(False)
            self.turnOnOpenGL(False)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.MiddleButton:
            self.mouseMiddlePressEvent(event)
        elif event.button() == Qt.MouseButton.LeftButton and self.isEditorModality:
            self.currentItem = self.itemAt(event.pos())
            if self.currentItem:
                self.lastPos = self.mapToScene(event.pos())
                self.deltaPos = self.currentItem.pos() - self.lastPos

    def mouseMoveEvent(self, event):
        if self._isPanning and event.buttons() & Qt.MouseButton.MiddleButton:
            self.panTheScene(event)
        elif self.isEditorModality and self.currentItem and self.lastPos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            currentPos = self.mapToScene(event.pos()) + self.deltaPos
            newPos = self.applySnapping(currentPos)
            self.currentItem.setPos(newPos)
        super().mouseMoveEvent(event)

    def applySnapping(self, pos):
        snapPoint = QPointF(1920, 1080)
        if abs(pos.x() - snapPoint.x()) < self.snapThreshold:
            pos.setX(snapPoint.x())
        if abs(pos.y() - snapPoint.y()) < self.snapThreshold:
            pos.setY(snapPoint.y())
        return pos

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.MiddleButton:
            self.mouseMiddleReleaseEvent(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.currentItem = None
            self.lastPos = None
            self.deltaPos = None

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
        vsBarValue = self.verticalScrollBar().value()
        self.horizontalScrollBar().setValue(hsBarValue - deltaPosition.x())
        self.verticalScrollBar().setValue(vsBarValue - deltaPosition.y())

    def wheelEvent(self, event):
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

    def keyPressEvent(self, event):
        if self.isEditorModality:
            if event.key() == Qt.Key.Key_Shift:
                self.shiftPressed = True
                print("Shift pressed")
            elif event.key() == Qt.Key.Key_Control:
                self.ctrlPressed = True
                print("Ctrl pressed")
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if self.isEditorModality:
            if event.key() == Qt.Key.Key_Shift:
                print("Shift released")
                self.shiftPressed = False
            elif event.key() == Qt.Key.Key_Control:
                print("Ctrl released")
                self.ctrlPressed = False
        super().keyReleaseEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.scene = GraphicSceneOverride012()
        self.view = GraphicViewOverride013(self.scene)

        centralWidget = QWidget()
        layout = QVBoxLayout(centralWidget)
        layout.addWidget(self.view)
        self.setCentralWidget(centralWidget)

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Custom Graphics View Example")
        self.setGeometry(100, 100, 800, 600)

        # Aggiungi un'immagine di esempio alla scena
        source = QGraphicsPixmapItem(QPixmap(r"C:\Users\aless\Pictures\indian_head-768x576.jpg"))
        self.scene.addItem(source)


if __name__ == '__main__':
    app = QApplication([])
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec()
