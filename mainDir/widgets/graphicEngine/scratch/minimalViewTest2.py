from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *


class InteractiveResizableRectangle(QObject):
    sizeChanged_SIGNAL = pyqtSignal(QRectF, name="sizeChanged_SIGNAL")

    handleTopLeft = 1
    handleTopMiddle = 2
    handleTopRight = 3
    handleMiddleLeft = 4
    handleMiddleRight = 5
    handleBottomLeft = 6
    handleBottomMiddle = 7
    handleBottomRight = 8

    handleSize = 10.0
    handleSpace = -4.0

    handleCursors = {
        handleTopLeft: Qt.CursorShape.SizeFDiagCursor,
        handleTopMiddle: Qt.CursorShape.SizeVerCursor,
        handleTopRight: Qt.CursorShape.SizeBDiagCursor,
        handleMiddleLeft: Qt.CursorShape.SizeHorCursor,
        handleMiddleRight: Qt.CursorShape.SizeHorCursor,
        handleBottomLeft: Qt.CursorShape.SizeBDiagCursor,
        handleBottomMiddle: Qt.CursorShape.SizeVerCursor,
        handleBottomRight: Qt.CursorShape.SizeFDiagCursor,
    }

    def __init__(self, rect, parent=None):
        super().__init__(parent)
        self.rectItem = QGraphicsRectItem(rect)
        self.rectItem.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                               QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                               QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges |
                               QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.handles = {}
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.rectItem.setAcceptHoverEvents(True)
        self.updateHandlesPos()

    def setHandleSize(self, size):
        self.handleSize = size
        self.updateHandlesPos()

    def handleAt(self, point):
        """
        Returns the resize handle below the given point.
        """
        for k, v, in self.handles.items():
            if v.contains(point):
                return k
        return None

    def hoverMoveEvent(self, moveEvent):
        """
        Executed when the mouse moves over the shape (NOT PRESSED).
        """
        if self.rectItem.isSelected():
            handle = self.handleAt(moveEvent.pos())
            cursor = Qt.CursorShape.ArrowCursor if handle is None else self.handleCursors[handle]
            self.rectItem.setCursor(cursor)
        super(QGraphicsRectItem, self.rectItem).hoverMoveEvent(moveEvent)

    def hoverLeaveEvent(self, moveEvent):
        """
        Executed when the mouse leaves the shape (NOT PRESSED).
        """
        self.rectItem.setCursor(Qt.CursorShape.ArrowCursor)
        super(QGraphicsRectItem, self.rectItem).hoverLeaveEvent(moveEvent)

    def mousePressEvent(self, mouseEvent):
        """
        Executed when the mouse is pressed on the item.
        """
        self.handleSelected = self.handleAt(mouseEvent.pos())
        if self.handleSelected:
            self.mousePressPos = mouseEvent.pos()
            self.mousePressRect = self.rectItem.boundingRect()
        super(QGraphicsRectItem, self.rectItem).mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        """
        Executed when the mouse is being moved over the item while being pressed.
        """
        if self.handleSelected is not None:
            self.interactiveResize(mouseEvent.pos())
        else:
            super(QGraphicsRectItem, self.rectItem).mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        """
        Executed when the mouse is released from the item.
        """
        super(QGraphicsRectItem, self.rectItem).mouseReleaseEvent(mouseEvent)
        self.handleSelected = None
        self.mousePressPos = None
        self.mousePressRect = None
        self.rectItem.update()
        self.sizeChanged_SIGNAL.emit(self.rectItem.rect())

    def boundingRect(self):
        """
        Returns the bounding rect of the shape (including the resize handles).
        """
        o = self.handleSize + self.handleSpace
        return self.rectItem.rect().adjusted(-o, -o, o, o)

    def updateHandlesPos(self):
        """
        Update current resize handles according to the shape size and position.
        """
        s = self.handleSize
        b = self.boundingRect()
        self.handles[self.handleTopLeft] = QRectF(b.left(), b.top(), s, s)
        self.handles[self.handleTopMiddle] = QRectF(b.center().x() - s / 2, b.top(), s, s)
        self.handles[self.handleTopRight] = QRectF(b.right() - s, b.top(), s, s)
        self.handles[self.handleMiddleLeft] = QRectF(b.left(), b.center().y() - s / 2, s, s)
        self.handles[self.handleMiddleRight] = QRectF(b.right() - s, b.center().y() - s / 2, s, s)
        self.handles[self.handleBottomLeft] = QRectF(b.left(), b.bottom() - s, s, s)
        self.handles[self.handleBottomMiddle] = QRectF(b.center().x() - s / 2, b.bottom() - s, s, s)
        self.handles[self.handleBottomRight] = QRectF(b.right() - s, b.bottom() - s, s, s)

    def interactiveResize(self, mousePos):
        """
        Perform shape interactive resize.
        """
        offset = self.handleSize + self.handleSpace
        boundingRect = self.boundingRect()
        rect = self.rectItem.rect()
        diff = QPointF(0, 0)

        self.rectItem.prepareGeometryChange()

        if self.handleSelected == self.handleTopLeft:

            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.top()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setLeft(toX)
            boundingRect.setTop(toY)
            rect.setLeft(boundingRect.left() + offset)
            rect.setTop(boundingRect.top() + offset)
            self.rectItem.setRect(rect)

        elif self.handleSelected == self.handleTopMiddle:

            fromY = self.mousePressRect.top()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setY(toY - fromY)
            boundingRect.setTop(toY)
            rect.setTop(boundingRect.top() + offset)
            self.rectItem.setRect(rect)

        elif self.handleSelected == self.handleTopRight:

            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.top()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setRight(toX)
            boundingRect.setTop(toY)
            rect.setRight(boundingRect.right() - offset)
            rect.setTop(boundingRect.top() + offset)
            self.rectItem.setRect(rect)

        elif self.handleSelected == self.handleMiddleLeft:

            fromX = self.mousePressRect.left()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            diff.setX(toX - fromX)
            boundingRect.setLeft(toX)
            rect.setLeft(boundingRect.left() + offset)
            self.rectItem.setRect(rect)

        elif self.handleSelected == self.handleMiddleRight:
            fromX = self.mousePressRect.right()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            diff.setX(toX - fromX)
            boundingRect.setRight(toX)
            rect.setRight(boundingRect.right() - offset)
            self.rectItem.setRect(rect)

        elif self.handleSelected == self.handleBottomLeft:

            fromX = self.mousePressRect.left()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setLeft(toX)
            boundingRect.setBottom(toY)
            rect.setLeft(boundingRect.left() + offset)
            rect.setBottom(boundingRect.bottom() - offset)
            self.rectItem.setRect(rect)

        elif self.handleSelected == self.handleBottomMiddle:

            fromY = self.mousePressRect.bottom()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setY(toY - fromY)
            boundingRect.setBottom(toY)
            rect.setBottom(boundingRect.bottom() - offset)
            self.rectItem.setRect(rect)

        elif self.handleSelected == self.handleBottomRight:

            fromX = self.mousePressRect.right()
            fromY = self.mousePressRect.bottom()
            toX = fromX + mousePos.x() - self.mousePressPos.x()
            toY = fromY + mousePos.y() - self.mousePressPos.y()
            diff.setX(toX - fromX)
            diff.setY(toY - fromY)
            boundingRect.setRight(toX)
            boundingRect.setBottom(toY)
            rect.setRight(boundingRect.right() - offset)
            rect.setBottom(boundingRect.bottom() - offset)
            self.rectItem.setRect(rect)

        self.updateHandlesPos()

    def shape(self):
        """
        Returns the shape of this item as a QPainterPath in local coordinates.
        """
        path = QPainterPath()
        path.addRect(self.rectItem.rect())
        if self.rectItem.isSelected():
            for shape in self.handles.values():
                path.addEllipse(shape)
        return path

    def paint(self, painter, option, widget=None):
        """
        Paint the node in the graphic view.
        """
        painter.setBrush(QBrush(QColor(255, 0, 0, 100)))
        painter.setPen(QPen(QColor(0, 0, 0), 1.0, Qt.PenStyle.SolidLine))
        painter.drawRect(self.rectItem.rect())

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 0, 0, 255)))
        painter.setPen(
            QPen(QColor(0, 0, 0, 255), 1.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        for handle, rect in self.handles.items():
            if self.handleSelected is None or handle == self.handleSelected:
                painter.drawEllipse(rect)


class CustomGraphicsItem(QGraphicsPixmapItem):
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges |
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.isMovable = True
        self.isResizable = False  # Default is not resizable
        self.resizableRect = InteractiveResizableRectangle(self.boundingRect())
        self.resizableRect.sizeChanged_SIGNAL.connect(self.updateSize)
        self.resizableRect.rectItem.setParentItem(self)
        self.resizableRect.rectItem.setVisible(False)

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
                self.resizableRect.rectItem.setVisible(False)
            elif action.text() == "Unlock Resize":
                self.isResizable = True
                self.resizableRect.rectItem.setVisible(True)

    def updateSize(self, newRect):
        pixmap = self.pixmap().scaled(newRect.size().toSize(), Qt.AspectRatioMode.KeepAspectRatio)
        self.setPixmap(pixmap)
        self.resizableRect.rectItem.setRect(newRect)


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
