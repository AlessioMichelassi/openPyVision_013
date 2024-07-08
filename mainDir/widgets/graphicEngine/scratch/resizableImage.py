import sys
import cv2
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.widgets.graphicEngine.graphicSceneOverride012 import GraphicSceneOverride012
from mainDir.widgets.graphicEngine.graphicViewOverride013 import GraphicViewOverride013


class Resizer(QGraphicsRectItem):
    startPos = None
    startRect = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resizeHandleSize = 20
        self.resizeHandelColor = QColor(255, 0, 0)
        self.setRect(QRectF(0, 0, self.resizeHandleSize, self.resizeHandleSize))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setBrush(QBrush(QColor(255, 0, 0)))
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.hide()

    def setHandleSize(self, size):
        self.resizeHandleSize = size
        self.setRect(QRectF(0, 0, self.resizeHandleSize, self.resizeHandleSize))

    def setHandleColor(self, color):
        self.resizeHandelColor = color
        self.setBrush(QBrush(self.resizeHandelColor))

    def mousePressEvent(self, event):
        self.startPos = event.scenePos()
        self.startRect = self.parentItem().boundingRect()
        print(f"Start resizing from: {self.startRect}")
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        diff = event.scenePos() - self.startPos
        newWidth = self.startRect.width() + diff.x()
        newHeight = self.startRect.height() + diff.y()
        print(f"Resizing to: Width={newWidth}, Height={newHeight}")
        self.parentItem().resizePixmap(QSizeF(newWidth, newHeight).toSize())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.startPos = None
        self.startRect = None
        print(f"Finished resizing to: {self.parentItem().boundingRect()}")
        super().mouseReleaseEvent(event)


class ResizableGraphicsItem(QGraphicsPixmapItem):
    def __init__(self, image_path):
        super().__init__()
        self.original_pixmap = QPixmap(image_path)
        self.setPixmap(self.original_pixmap)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges |
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.isMovable = True
        self.isResizable = False

        # Inizializza il resizer e posizionalo nell'angolo in basso a destra dell'item
        self.resizer = Resizer(parent=self)
        self.resizer.setPos(self.boundingRect().bottomRight() - QPointF(10, 10))

    def contextMenuEvent(self, event):
        menu = QMenu()
        menu.addAction("Lock Image" if self.isMovable else "Unlock Image")
        menu.addSeparator()
        menu.addAction("Lock Resize" if self.isResizable else "Unlock Resize")
        action = menu.exec(event.screenPos())

        if action:
            if "Image" in action.text():
                self.isMovable = not self.isMovable
                self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, self.isMovable)
            elif "Resize" in action.text():
                self.isResizable = not self.isResizable
                self.resizer.setVisible(self.isResizable)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        print(f"Mouse pressed on item: {self.boundingRect()}")
        if self.isResizable and self.resizer.isUnderMouse():
            self.startPos = event.scenePos()
            self.startRect = self.boundingRect()
            print(f"Start resizing from: {self.startRect}")

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.isResizable and self.currentHandle:
            rect = self.boundingRect()
            diff = event.scenePos() - self.mousePressPos
            newWidth = self.startRect.width() + diff.x()
            newHeight = self.startRect.height() + diff.y()

            # Aggiorna le dimensioni
            self.resizePixmap(QSizeF(newWidth, newHeight).toSize())

            # Calcolo per lo snap
            snap_point = QPointF(1920, 1080)
            snap_distance = 50
            current_bottom_right = self.mapToScene(self.boundingRect().bottomRight())

            if (abs(current_bottom_right.x() - snap_point.x()) < snap_distance and
                    abs(current_bottom_right.y() - snap_point.y()) < snap_distance):
                # Calcola la differenza per allineare esattamente al punto di snap
                offset_x = snap_point.x() - current_bottom_right.x()
                offset_y = snap_point.y() - current_bottom_right.y()
                self.setPos(self.pos() + QPointF(offset_x, offset_y))


    def resizePixmap(self, newSize):
        resizedPixmap = self.original_pixmap.scaled(newSize, Qt.AspectRatioMode.IgnoreAspectRatio,
                                                    Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(resizedPixmap)
        self.updateResizer()

    def updateResizer(self):
        self.resizer.setPos(self.boundingRect().bottomRight() - QPointF(10, 10))

    def mouseReleaseEvent(self, event):
        if self.isResizable and self.resizer.isUnderMouse():
            print(f"Finished resizing to: {self.boundingRect()}")
        super().mouseReleaseEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.scene = GraphicSceneOverride012()
        self.view = GraphicViewOverride013(self.scene)
        self.scene.showGrid(True)
        self.scene.showResolutionGuide(True)
        self.view.setEditorModality(True)

        centralWidget = QWidget()
        layout = QVBoxLayout(centralWidget)
        layout.addWidget(self.view)
        self.setCentralWidget(centralWidget)

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Custom Graphics View Example")
        self.setGeometry(100, 100, 800, 600)

        # Aggiungi un'immagine di esempio alla scena
        image = ResizableGraphicsItem(r"C:\Users\aless\Pictures\indian_head-768x576.jpg")
        self.scene.addImage(image)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
