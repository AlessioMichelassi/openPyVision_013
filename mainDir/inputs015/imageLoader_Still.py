import cv2
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from cap3.cap3_1.baseClass import BaseClass


class StillImageLoader(BaseClass):
    _color = QColor(250, 0, 0)  # Colore iniziale: rosso

    def __init__(self, imagePath, synchObject, resolution=QSize(1920, 1080)):
        super().__init__(synchObject, resolution)
        self.loadImage(imagePath)

    def loadImage(self, imagePath):
        """
        Carica l'immagine e fa il resize a 1920x1080 se necessario.
        """
        try:
            image = cv2.imread(imagePath)
            # se le dimensioni dell'immagine sono diverse da quelle
            # specificate, ridimensiona l'immagine
            if image.shape[:2] != (self.resolution.height(), self.resolution.width()):
                image = cv2.resize(image, (self.resolution.width(), self.resolution.height()))

            self._frame = image
        except Exception as e:
            print(f"Error loading image: {e}")
            self._frame = np.zeros((self.resolution.height(),
                                    self.resolution.width(), 3), dtype=np.uint8)

    def captureFrame(self):
        """
        Sovrascrive la funzione captureFrame della classe base, mantenendo la funzionalità originale.
        """
        super().captureFrame()

    def getFrame(self):
        """
        Sovrascrive la funzione getFrame della classe base, mantenendo la funzionalità originale.
        """
        return super().getFrame()
