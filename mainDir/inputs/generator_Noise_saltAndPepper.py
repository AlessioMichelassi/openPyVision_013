import numpy as np
import cv2
from PyQt6.QtCore import QSize
from mainDir.inputs.baseClass import BaseClass

class SaltAndPepperNoiseGenerator(BaseClass):
    def __init__(self, synchObject, resolution=QSize(1920, 1080), salt_prob=0.05, pepper_prob=0.05):
        super().__init__(synchObject, resolution)
        self.salt_prob = salt_prob
        self.pepper_prob = pepper_prob
        self.generate_noise()

    def generate_noise(self):
        height, width = self.resolution.height(), self.resolution.width()
        # Create a blank image with all pixels set to middle gray
        image = np.ones((height, width, 3), dtype=np.uint8) * 127

        # Add salt noise (white pixels)
        num_salt = np.ceil(self.salt_prob * height * width)
        coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image.shape[:2]]
        image[coords[0], coords[1], :] = 255

        # Add pepper noise (black pixels)
        num_pepper = np.ceil(self.pepper_prob * height * width)
        coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in image.shape[:2]]
        image[coords[0], coords[1], :] = 0

        return np.ascontiguousarray(image)

    def stop(self):
        super().stop()

    def captureFrame(self):
        self._frame = self.generate_noise()
        self.updateFps()

    def getFrame(self):
        return self._frame
