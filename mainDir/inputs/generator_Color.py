import time

import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.inputs.baseClass import BaseClass


class ColorGenerator(BaseClass):
    _color = QColor(250, 0, 0)

    def __init__(self, synchObject, resolution=QSize(1920, 1080)):
        super().__init__(synchObject, resolution)
        self.target_resolution = (resolution.height(), resolution.width())
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)
        self.setColor(self._color)  # Initialize the color frame

    def setColor(self, color: QColor):
        self._color = color
        self._frame[:, :] = [color.blue(), color.green(), color.red()]

    def stop(self):
        super().stop()
        # No specific resources to release for ColorGenerator

    def captureFrame(self):
        # ColorGenerator doesn't capture frames, it generates them

        self.updateFps()

    def getFrame(self):
        return self._frame


