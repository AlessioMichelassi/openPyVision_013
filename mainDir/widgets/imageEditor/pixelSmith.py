from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt6.QtGui import QPixmap, QImageReader

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import os

from mainDir.widgets.graphicEngine.graphicSceneOverride012 import GraphicSceneOverride012
from mainDir.widgets.graphicEngine.graphicViewOverride013 import GraphicViewOverride013

"""
ImageEdit ho una graphicView che permette di ridimensionare l'immagine,
ruotarla, e aggiungere alcuni effetti.
"""


class PixelSmith200(QWidget):
    isMovable = False
    isResizable = False

    def __init__(self, filePath, parent=None):
        super().__init__(parent)
        self.filePath = filePath

        # Graphics scene and view
        self.scene = GraphicSceneOverride012()
        self.view = GraphicViewOverride013(self.scene)
        self.view.setEditorModality(True)
        self.imagePixmap = None
        self.HD_resolution_guide = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("pixelSmith v0.2")

        # Main layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.view)

        # Load image
        self.imagePixmap = QGraphicsPixmapItem()
        pixmap = QPixmap(self.filePath)
        self.imagePixmap.setPixmap(pixmap)
        self.scene.addItem(self.imagePixmap)
        self.scene.showGrid(True)
        self.scene.showResolutionGuide(True)
        # Buttons for operations
        buttonLayout = QHBoxLayout()
        resizeButton = QPushButton('Resize')
        rotateButton = QPushButton('Rotate')
        flipButton = QPushButton('Flip')
        effectButton = QPushButton('Apply Effect')

        resizeButton.clicked.connect(self.resizeImage)
        rotateButton.clicked.connect(self.rotateImage)
        flipButton.clicked.connect(self.flipImage)
        effectButton.clicked.connect(self.applyEffect)

        buttonLayout.addWidget(resizeButton)
        buttonLayout.addWidget(rotateButton)
        buttonLayout.addWidget(flipButton)
        buttonLayout.addWidget(effectButton)

        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

    def contextMenuEvent(self, a0):
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

        action = menu.exec(self.mapToGlobal(a0.pos()))
        if action:
            if action.text() == "Lock Image":
                self.isMovable = False
                self.imagePixmap.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
            elif action.text() == "Unlock Image":
                self.isMovable = True
                self.imagePixmap.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
            elif action.text() == "Lock Resize":
                self.isResizable = False

            elif action.text() == "Unlock Resize":
                self.isResizable = True

    def resizeImage(self):
        self.imagePixmap.setPixmap(self.imagePixmap.pixmap().scaled(1920, 1080, Qt.AspectRatioMode.KeepAspectRatio))
        print(f"Image resized to fit within 1920x1080")

    def rotateImage(self):
        transform = QTransform()
        transform.rotate(90)
        self.imagePixmap.setPixmap(self.imagePixmap.pixmap().transformed(transform))
        print(f"Image rotated 90 degrees")

    def flipImage(self):
        transform = QTransform()
        transform.scale(-1, 1)  # Horizontal flip
        self.imagePixmap.setPixmap(self.imagePixmap.pixmap().transformed(transform))
        print(f"Image flipped horizontally")

    def applyEffect(self):
        # Applying a grayscale effect as an example
        image = self.imagePixmap.pixmap().toImage()
        for i in range(image.width()):
            for j in range(image.height()):
                pixel = image.pixel(i, j)
                gray = qGray(pixel)
                image.setPixel(i, j, qRgb(gray, gray, gray))
        self.imagePixmap.setPixmap(QPixmap.fromImage(image))
        print(f"Grayscale effect applied")


# Test class
if __name__ == '__main__':
    app = QApplication([])
    dialog = PixelSmith200(r"C:\Users\aless\Pictures\indian_head-768x576.jpg")
    dialog.show()
    app.exec()
