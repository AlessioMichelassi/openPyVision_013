import numpy as np
from PyQt6.QtCore import *

from mainDir.inputs015.baseClass015 import BaseClass015


class RandomNoiseGenerator(BaseClass015):

    def __init__(self, synchObject, resolution=QSize(1920, 1080)):
        super().__init__(synchObject, resolution)
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)

    def captureFrame(self):
        """
        Sovrascrive la funzione captureFrame della classe base, mantenendo la funzionalità originale.
        """
        super().captureFrame()
        self._frame = np.random.randint(0, 255, (self.resolution.height(), self.resolution.width(), 3), dtype=np.uint8)

    def getFrame(self):
        """
        Sovrascrive la funzione getFrame della classe base, mantenendo la funzionalità originale.
        """
        return super().getFrame()
