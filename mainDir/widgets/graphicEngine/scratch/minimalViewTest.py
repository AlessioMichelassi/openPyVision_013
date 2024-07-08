from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


class CustomGraphicsItem(QGraphicsPixmapItem):
    handleSize = 10.0
    handleSpace = -5.0

    handleBottomRight = 1
    handleRight = 2
    handleBottom = 3

    handleCursors = {
        handleBottomRight: Qt.CursorShape.SizeFDiagCursor,
        handleRight: Qt.CursorShape.SizeHorCursor,
        handleBottom: Qt.CursorShape.SizeVerCursor,
    }

    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges |
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.shiftPressed = False
        self.ctrlPressed = False
        self.isMovable = True
        self.isResizable = False  # Default is not resizable
        self.handles = {}  # Dictionary to store handle positions
        self.currentHandle = None  # Current handle being dragged
        self.updateHandlesPos()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Shift:
            self.shiftPressed = True
            print("Shift pressed")
        elif event.key() == Qt.Key.Key_Control:
            self.ctrlPressed = True
            print("Ctrl pressed")
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Shift:
            self.shiftPressed = False
        elif event.key() == Qt.Key.Key_Control:
            self.ctrlPressed = False
        super().keyReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene():
            newPos = value.toPoint()
            if self.shiftPressed:
                newPos.setX(int(self.pos().x()))
            elif self.ctrlPressed:
                newPos.setY(int(self.pos().y()))
            return newPos
        return super().itemChange(change, value)

    def contextMenuEvent(self, event):
        menu = QMenu()
        if self.isMovable:
            menu.addAction("Lock Image")
        else:
            menu.addAction("Unlock Image")
        menu.addSeparator()
        if self.isResizable:
            menu.addAction("Lock Resize")
        else:
            menu.addAction("Unlock Resize")
        menu.addSeparator()

        action = menu.exec(event.screenPos())
        if action:
            if action.text() == "Lock Image":
                self.isMovable = False
                self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            elif action.text() == "Unlock Image":
                self.isMovable = True
                self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
            elif action.text() == "Lock Resize":
                self.isResizable = False
                self.handles = {}
            elif action.text() == "Unlock Resize":
                self.isResizable = True
                self.updateHandlesPos()

    def updateHandlesPos(self):
        rect = self.boundingRect()
        s = self.handleSize
        self.handles[self.handleBottomRight] = QRectF(rect.right() - s, rect.bottom() - s, s, s)
        self.handles[self.handleRight] = QRectF(rect.right() - s, rect.center().y() - s / 2, s, s)
        self.handles[self.handleBottom] = QRectF(rect.center().x() - s / 2, rect.bottom() - s, s, s)

    def boundingRect(self):
        o = int(self.handleSize + self.handleSpace)
        return QRectF(self.pixmap().rect().adjusted(-o, -o, o, o))

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.isResizable:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QBrush(QColor(255, 0, 0, 255)))
            painter.setPen(QPen(QColor(0, 0, 0, 255)))
            for handle in self.handles.values():
                painter.drawRect(handle)

    def handleAt(self, point):
        for k, v in self.handles.items():
            if v.contains(point):
                return k
        return None

    def mousePressEvent(self, event):
        if self.isResizable:
            self.currentHandle = self.handleAt(event.pos())
            if self.currentHandle:
                self.mousePressPos = event.pos()
                self.mousePressRect = self.boundingRect()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.isResizable and self.currentHandle:
            rect = self.boundingRect()
            diff = QPointF(0, 0)
            self.prepareGeometryChange()

            if self.currentHandle == self.handleRight:
                fromX = self.mousePressRect.right()
                toX = fromX + event.pos().x() - self.mousePressPos.x()
                diff.setX(toX - fromX)
                rect.setRight(rect.right() + diff.x())

            elif self.currentHandle == self.handleBottom:
                fromY = self.mousePressRect.bottom()
                toY = fromY + event.pos().y() - self.mousePressPos.y()
                diff.setY(toY - fromY)
                rect.setBottom(rect.bottom() + diff.y())

            elif self.currentHandle == self.handleBottomRight:
                fromX = self.mousePressRect.right()
                fromY = self.mousePressRect.bottom()
                toX = fromX + event.pos().x() - self.mousePressPos.x()
                toY = fromY + event.pos().y() - self.mousePressPos.y()
                diff.setX(toX - fromX)
                diff.setY(toY - fromY)
                rect.setRight(rect.right() + diff.x())
                rect.setBottom(rect.bottom() + diff.y())

            self.setPixmap(self.pixmap().scaled(rect.size().toSize(), Qt.AspectRatioMode.KeepAspectRatio))
            self.updateHandlesPos()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.currentHandle = None
        super().mouseReleaseEvent(event)

class CustomGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 1920, 1080)
        self.addResolutionGuide()

    def addResolutionGuide(self):
        self.addRect(0, 0, 1920, 1080, pen=QPen(Qt.GlobalColor.red))

    def addImage(self, image_path):
        pixmap = QPixmap(image_path)
        item = CustomGraphicsItem(pixmap)
        self.addItem(item)
        item.setPos(0, 0)  # Posiziona l'immagine in (0, 0)
        return item


class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.initRenderHints()
        self.isEditorModality = True
        self._isPanning = False
        self._lastMiddleMousePosition = QPoint()
        self.currentItem = None

    def initRenderHints(self):
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.mouseMiddlePressEvent(event)
        elif event.button() == Qt.MouseButton.LeftButton and self.isEditorModality:
            self.currentItem = self.itemAt(event.pos())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._isPanning:
            self.panTheScene(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.mouseMiddleReleaseEvent(event)
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if self.currentItem:
            self.currentItem.keyPressEvent(event)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if self.currentItem:
            self.currentItem.keyReleaseEvent(event)
        super().keyReleaseEvent(event)

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
        event.accept()

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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.scene = CustomGraphicsScene()
        self.view = CustomGraphicsView(self.scene)

        centralWidget = QWidget()
        layout = QVBoxLayout(centralWidget)
        layout.addWidget(self.view)
        self.setCentralWidget(centralWidget)

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Custom Graphics View Example")
        self.setGeometry(100, 100, 800, 600)

        # Aggiungi un'immagine di esempio alla scena
        self.scene.addImage(r"C:\Users\aless\Pictures\indian_head-768x576.jpg")


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
