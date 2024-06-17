import time

import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.inputs.baseClass import BaseClass


class FullBarsGenerator(BaseClass):

    def __init__(self, synchObject, resolution=QSize(1920, 1080)):
        super().__init__(synchObject, resolution)
        self.target_resolution = (resolution.height(), resolution.width())
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)
        self.createBars()

    def createBars(self):
        """
        Genera un'immagine con le barre SMPTE in formato np.array
        :return:
        """
        # Definisci i colori in formato BGR
        colors = [
            (192, 192, 192),  # Grigio
            (0, 192, 192),  # Giallo
            (192, 192, 0),  # Ciano
            (0, 192, 0),  # Verde
            (192, 0, 192),  # Magenta
            (0, 0, 192),  # Rosso
            (192, 0, 0),  # Blu
            (0, 0, 0)  # Nero
        ]
        width, height = self.resolution.width(), self.resolution.height()
        # Crea una matrice vuota
        bar_height = height
        bar_width = width // len(colors)
        bars = np.zeros((bar_height, width, 3), dtype=np.uint8)
        # Riempie ogni sezione con il colore corrispondente
        for i, color in enumerate(colors):
            bars[:, i * bar_width:(i + 1) * bar_width, :] = color
        self._frame = bars

    def stop(self):
        super().stop()
        # No specific resources to release for ColorGenerator

    def capture_frame(self):
        # ColorGenerator doesn't capture frames, it generates them
        self.update_fps()

    def getFrame(self):
        return self._frame


