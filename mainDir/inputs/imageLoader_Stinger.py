import os
import cv2
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from mainDir.inputs.baseClass import BaseClass

"""
La classe stingerLoader permette di caricare una sequenza di immagini PNG con canale alpha. Tramite getFrame si ottiene
l'immagine corrente. Nel caso in cui si necessiti di un frame di fill e di key, è possibile utilizzare il metodo
getFillAndKey che restituisce una tupla (bgr, alpha), dove alpha non è un immagine a 3 canali ma è monocanale in modo 
da essere poter essere usata nelle operazioni di blending.
Il metodo setSwitchingFrameNumber permette di impostare il frame in cui emettere il segnale di switching. Se usato 
durante il mix live di solito si vuole passare da program a preview quando l'immagine di sting è a schermo pieno. Di
Default viene settata a metà della sequenza di immagini, ma è possibile variarla a piacimento.
Il metodo setLoop permette di impostare se la sequenza di immagini deve essere in loop o meno.
"""


class StingerLoader(BaseClass):
    switching_SIGNAL = pyqtSignal()  # Segnale per indicare il frame di switching

    def __init__(self, synchObject, stinger_folder, resolution=QSize(1920, 1080)):
        super().__init__(synchObject, resolution)
        self.isStarted = False
        self.stinger_folder = stinger_folder
        self.stingerLength = 0
        self._isLooped = False
        self._switching_signal_sent = False  # Variabile per tenere traccia del segnale di switching
        self.images = self.load_images()
        self._current_image_index = 0
        self.switchingFrameNumber = self.stingerLength // 2 # Default a metà della sequenza
        self._frame = self.images[self._current_image_index] if self.images else np.zeros(
            (resolution.height(), resolution.width(), 4), dtype=np.uint8)  # Include il canale alpha
        self.synch_Object.synch_SIGNAL.connect(self.capture_frame)

    def load_images(self):
        images = []
        for filename in sorted(os.listdir(self.stinger_folder)):
            if filename.endswith('.png'):
                image_path = os.path.join(self.stinger_folder, filename)
                image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Legge anche il canale alpha
                if image is not None:
                    image = cv2.resize(image, (self.resolution.width(), self.resolution.height()))
                    images.append(image)
        self.stingerLength = len(images)
        return images

    def stop(self):
        super().stop()

    def startAnimation(self):
        self.isStarted = True

    def capture_frame(self):
        """
        In questo caso in capture frame viene implementata la logica per aumentare l'indice dell'immagine corrente.
        :return:
        """
        if self.isStarted:
            self._current_image_index += 1
            if self._current_image_index >= self.stingerLength:
                self._current_image_index = 0
                self._switching_signal_sent = False  # Reset al termine del loop
                if not self._isLooped:
                    self.isStarted = False
            if self._current_image_index == self.switchingFrameNumber and not self._switching_signal_sent:
                print(f"Switching signal sent at frame {self._current_image_index} while total frames are "
                      f"{self.stingerLength} and switching frame is {self.switchingFrameNumber}")
                self.switching_SIGNAL.emit()
                self._switching_signal_sent = True  # Imposta come inviato
            if self.images:
                self._frame = self.images[self._current_image_index]
        else:
            self._frame = self.images[self._current_image_index] if self.images else np.zeros(
                (self.resolution.height(), self.resolution.width(), 4), dtype=np.uint8)
        self.update_fps()

    def setIndex(self, index):
        self._current_image_index = index

    def getCurrentIndex(self):
        return self._current_image_index

    def setSwitchingFrameNumber(self, frameNumber):
        self.switchingFrameNumber = frameNumber

    def getFrame(self):
        return self._frame

    def getFillAndKey(self):
        """
        Ritorna il frame di fill e di key.
        Il key è una matrice singola e può quindi essere usata nelle operazioni di blending.
        :return:
        """
        black = np.zeros((self.resolution.height(), self.resolution.width(), 3), dtype=np.uint8)
        alpha = np.zeros((self.resolution.height(), self.resolution.width()), dtype=np.uint8)
        if self._frame is None:
            return black, alpha
        b, g, r, a = cv2.split(self._frame)
        return cv2.merge((b, g, r)), a

    def setLoop(self, isLooped):
        self._isLooped = isLooped
