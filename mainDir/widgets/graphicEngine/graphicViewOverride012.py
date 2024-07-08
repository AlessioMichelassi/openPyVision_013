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
    shiftPressed = False
    ctrlPressed = False
    lastPos: QPointF() = None
    deltaPos = QPointF()

    def __init__(self, _scene, parent=None):
        super().__init__(_scene, parent)
        self.initRenderHints()
        self.isEditorModality = False

    def initRenderHints(self):
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

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
        else:
            self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def mousePressEvent(self, event, _QMouseEvent=None):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.MiddleButton:
            self.mouseMiddlePressEvent(event)
        elif event.button() == Qt.MouseButton.LeftButton and self.isEditorModality:
            self.currentItem = self.itemAt(event.pos())
            if self.currentItem:
                self.lastPos = self.mapToScene(event.pos())
                self.deltaPos = self.currentItem.pos() - self.lastPos

    def mouseMoveEvent(self, event, _QMouseEvent=None):
        super().mouseMoveEvent(event)
        if self._isPanning:
            self.panTheScene(event)
        if self.isEditorModality and self.currentItem and self.lastPos is not None:
            # evita il pan della scena
              
            currentPos = self.mapToScene(event.pos()) + self.deltaPos
            if self.shiftPressed:
                newPos = QPointF(self.currentItem.pos().x(), currentPos.y())
            elif self.ctrlPressed:
                newPos = QPointF(currentPos.x(), self.currentItem.pos().y())
            else:
                newPos = currentPos
            self.currentItem.setPos(newPos)

    def mouseReleaseEvent(self, event, _QMouseEvent=None):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.MiddleButton:
            self.mouseMiddleReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            if self.isEditorModality:
                self.lastPos = None
                self.currentItem = None

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
                self.ctrlPressed = False
        super().keyReleaseEvent(event)


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
