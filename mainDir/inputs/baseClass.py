import time
import cv2
import numpy as np
from PyQt6.QtCore import *


class BaseClass(QObject):
    _frame = None
    isALoadTesting = False
    _gamma_correction = 1.0
    isGrayScale = False
    isNegative = False

    def __init__(self, synchObject, resolution=QSize(1920, 1080)):
        super().__init__()
        self.synchObject = synchObject
        self.resolution = resolution
        self.synchObject.synch_SIGNAL.connect(self.capture_frame)
        self.start_time = time.time()
        self.frame_count = 0
        self.total_time = 0
        self.fps = 0
        self.last_update_time = time.time()

    def __del__(self):
        self.stop()
        # force garbage collection
        self.frame_processor = None
        # imposta su none tutte le variabili
        for key in self.__dict__.keys():
            self.__dict__[key] = None

    def setGammaCorrection(self, value):
        self._gamma_correction = value

    def stop(self):
        try:
            if hasattr(self, 'frame_processor') and self.frame_processor.isRunning():
                self.frame_processor.stop()
        except RuntimeError as e:
            print(f"Error stopping frame processor: {e}")

    def capture_frame(self):
        self.update_fps()
        image = np.zeros((self.resolution.height(), self.resolution.width(), 3), dtype=np.uint8)
        self._frame = np.ascontiguousarray(image)

    def update_fps(self):
        self.frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        if elapsed_time >= 1.0:  # Update FPS every second
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.last_update_time = current_time

    def flipFrame(self, flipCode: int):
        """
        Ritorna il flip del frame
        :param flipCode: es. 0: flip orizzontale, 1: flip verticale, -1: flip orizzontale e verticale
        :return:
        """
        return cv2.flip(self._frame, flipCode)

    @staticmethod
    def gammaCorrection(gamma: float):
        # Creazione della Look-Up Table per la correzione di gamma
        invGamma = 1.0 / gamma
        table = np.array([(i / 255.0) ** invGamma * 255 for i in range(256)]).astype("uint8")
        return table

    @staticmethod
    def negative(frame):
        return cv2.bitwise_not(frame)

    @staticmethod
    def grayScale(frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.merge((gray, gray, gray))

    @staticmethod
    def applyUnSharpMask(image, amount=1.5, radius=1.0, threshold=0):
        # Applica una sfocatura gaussiana all'immagine
        blurred = cv2.GaussianBlur(image, (0, 0), radius)

        # Crea la maschera di contrasto
        return cv2.addWeighted(image, 1 + amount, blurred, -amount, 0)

    def selfScreenImage(self, frame):
        """
        selfScreen è un metodo preso a prestito dalla pellicola. Quando si compositavano gli effetti di luce, per non
        sovrapporre i colori, si usava proiettare le due immagini dal negativo, su una pellicola vergine per poi invertire
        il tutto. Questo metodo simula questo effetto. Se lo facciamo sulla stesso frame, otteniamo l'immagine originale un pò più
        luminosa. Fa particolarmente comodo quando si acquisisce da webcam o da camere che sono già al massimo dell'apertura,
        per aumentare la luminosità senza usare il gain che introdurrebbe rumore.
        Il problema però è che bitiwse_and non si applica se le due immagini sono uguali, quindi bisogna fare un po' di
        contorsionismo per ottenere il risultato desiderato.
        :param frame:
        :return:
        """
        not_frame = cv2.bitwise_not(frame)
        # AND inversi
        and_result = cv2.bitwise_and(not_frame, not_frame)
        return cv2.bitwise_not(and_result)

    def oldSchoolScreen(self, frame):
        not_image = cv2.bitwise_not(frame)
        # Scale not_image to simulate (1 - A) * (1 - B)
        screen_result = 255 - cv2.multiply(not_image, not_image, scale=1.0 / 255.0)
        return screen_result

    def frameProcessor(self, frame):
        if self._gamma_correction != 1.0:
            lut = self.gammaCorrection(self._gamma_correction)
            frame = cv2.LUT(frame, lut)
        if self.isNegative:
            frame = self.negative(frame)
        if self.isGrayScale:
            frame = self.grayScale(frame)
        return frame

    def getFrame(self):
        return self._frame
