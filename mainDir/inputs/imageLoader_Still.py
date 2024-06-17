import time
import cv2
import numpy as np
from PyQt6.QtCore import QSize
from mainDir.inputs.baseClass import BaseClass


class ImageLoader(BaseClass):
    def __init__(self, synchObject, path, resolution=QSize(1920, 1080)):
        super().__init__(synchObject, resolution)
        self.path = path
        self._frame = self.setImage(self.path)

    def setImage(self, path):
        self.path = path
        image = cv2.imread(path)
        if image is not None:
            image = cv2.resize(image, (self.resolution.width(), self.resolution.height()))
        else:
            image = np.zeros((self.resolution.height(), self.resolution.width(), 3), dtype=np.uint8)
        self._frame = image
        return image

    def stop(self):
        super().stop()

    def capture_frame(self):
        # No frame capture, just update the FPS
        self.update_fps()

    def getFrame(self):
        return self._frame
