from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class StillLoaderWidget(QWidget):
    deviceChanged = pyqtSignal(dict, name="StillLoaderChanged")
    stillLoaderDictionary = {}

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        label = QLabel("StillLoader", self)
        self.labelImage = QLabel(self)
        self.labelImage.setBaseSize(40, 50)
        self.labelImage.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        self.labelImage.setStyleSheet("background-color: black;")
        self.btnLoadImage = QPushButton("Load Image", self)
        layout.addWidget(label)
        layout.addWidget(self.labelImage)
        layout.addWidget(self.btnLoadImage)
        self.btnLoadImage.clicked.connect(self.loadImage)
        self.setLayout(layout)

    def loadImage(self):
        path = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")[0]
        if path:
            pixmap = QPixmap(path)
            scaled_pixmap = pixmap.scaled(self.labelImage.size(), Qt.AspectRatioMode.KeepAspectRatio)
            self.labelImage.setPixmap(scaled_pixmap)
            self.stillLoaderDictionary = {"path": path}
            self.deviceChanged.emit(self.stillLoaderDictionary)

    def getDictionary(self):
        return self.stillLoaderDictionary


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    stillLoader = StillLoaderWidget()
    stillLoader.deviceChanged.connect(print)
    stillLoader.show()
    sys.exit(app.exec())
