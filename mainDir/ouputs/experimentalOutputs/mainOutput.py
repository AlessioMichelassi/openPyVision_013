import cv2
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from mainDir.inputs.baseClass import BaseClass


class MainOutSignal(BaseClass):
    mainViewer: QLabel

    def __init__(self, synchObject, resolution=QSize(1920, 1080)):
        super().__init__(synchObject, resolution)
        self.mainViewer = QLabel()
        self.mainViewer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainViewer.setFixedSize(resolution)
        self.mainViewer.show()

    def captureFrame(self):
        super().captureFrame()
        self._frame = np.zeros((self.resolution.height(), self.resolution.width(), 3), dtype=np.uint8)

    def feedFrame(self, frame):
        self._frame = frame

    def drawPointer(self, position, diameter=10):
        x, y = position
        image = np.zeros((self.resolution.height(), self.resolution.width(), 3), np.uint8)
        cv2.circle(image, (x, y), diameter, (0, 0, 255), -1)
        return image

    def getFrame(self):
        return self._frame
