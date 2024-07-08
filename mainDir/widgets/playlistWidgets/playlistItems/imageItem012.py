import json
import cv2
import subprocess
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import os

from mainDir.widgets.playlistWidgets.playlistItems.baseItem import BaseItem


class ItemImage(BaseItem):

    def __init__(self, filePath=None, parent=None):
        super().__init__(parent)
        self.initConnections()
        if filePath:
            self.loadImageFile(filePath)

    def initConnections(self):
        super().initConnections()
        self.btnLoad.clicked.connect(self.loadItem)

    def loadItem(self):
        """
        Open a file dialog to select an image file
        :return:
        """
        file_filter = "Image Files (*.png *.jpg *.jpeg);;All Files (*)"
        filePath, _ = QFileDialog.getOpenFileName(self, 'Select Image', '', file_filter)
        if filePath:
            self.loadImageFile(filePath)

    def loadImageFile(self, filePath):
        """
        Load the image file and update the UI
        :param filePath: Path to the image file
        """
        self.name = filePath.split('/')[-1]
        self.path = filePath
        self.setThumbnail(QPixmap(filePath))
        self.setFileName(self.name)
        self.setStartAt("00:00")
        self.setEndAt("00:10")  # Default duration for an image
        self.update()
        self.getImageInfo(filePath)

    def getImageInfo(self, path):
        """
        Get image information and update labels.
        :param path: Path to the image file
        """
        image = QImage(path)
        width = image.width()
        height = image.height()
        self.setMediaCodec(f"Image: {width}x{height}")

        # No audio information for images, so set default values
        self.setAudioCodec("No audio")
        self.setVolume("No audio")

    def check_black_frame(self, path, start=True, fps=30, duration_seconds=0, duration_minutes=0):
        """
        Check for black frames is not applicable for images.
        """
        return None


if __name__ == '__main__':
    app = QApplication([])
    widget = ItemImage(r"C:\Users\aless\Pictures\sample_image.jpg")
    widget.show()
    app.exec()
