import time
import cv2
import numpy as np
from PyQt6.QtCore import QSize


class UMAt_BaseClass:
    _frame = None
    isALoadTesting = False
    _gamma_correction = 1.0
    isGrayScale = False
    isNegative = False

    def __init__(self, synchObject, resolution=QSize(1920, 1080)):
        self.synchObject = synchObject
        self.resolution = resolution
        self.synchObject.synch_SIGNAL.connect(self.capture_frame)
        self.start_time = time.time()
        self.frame_count = 0
        self.total_time = 0
        self.fps = 0
        self.last_update_time = time.time()

        # Precompute gamma correction LUT
        self.gamma_lut = self.gammaCorrection(self._gamma_correction)

    def __del__(self):
        self.stop()
        self.frame_processor = None
        for key in self.__dict__.keys():
            self.__dict__[key] = None

    def setGammaCorrection(self, value):
        self._gamma_correction = value
        self.gamma_lut = self.gammaCorrection(value)

    def stop(self):
        try:
            if hasattr(self, 'frame_processor') and self.frame_processor.isRunning():
                self.frame_processor.stop()
        except RuntimeError as e:
            print(f"Error stopping frame processor: {e}")

    def capture_frame(self):
        self.update_fps()
        image = np.zeros((self.resolution.height(), self.resolution.width(), 3), dtype=np.uint8)
        self._frame = cv2.UMat(image)  # Use UMat for potential GPU acceleration

    def update_fps(self):
        self.frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        if elapsed_time >= 1.0:
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.last_update_time = current_time

    def flipFrame(self, flipCode: int):
        if self._frame is not None:
            return cv2.flip(self._frame, flipCode)
        return None

    @staticmethod
    def gammaCorrection(gamma: float):
        invGamma = 1.0 / gamma
        table = np.array([(i / 255.0) ** invGamma * 255 for i in range(256)]).astype("uint8")
        return table

    @staticmethod
    def negative(frame):
        if frame is not None:
            return cv2.bitwise_not(frame)
        return None

    @staticmethod
    def grayScale(frame):
        if frame is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return cv2.merge((gray, gray, gray))
        return None

    @staticmethod
    def applyUnSharpMask(image, amount=1.5, radius=1.0, threshold=0):
        if image is not None:
            blurred = cv2.GaussianBlur(image, (0, 0), radius)
            return cv2.addWeighted(image, 1 + amount, blurred, -amount, 0)
        return None

    def selfScreenImage(self):
        if self._frame is not None:
            not_frame = cv2.bitwise_not(self._frame)
            and_result = cv2.bitwise_and(not_frame, not_frame)
            return cv2.bitwise_not(and_result)
        return None

    def frameProcessor(self, frame):
        if frame is not None:
            if self._gamma_correction != 1.0:
                frame = cv2.LUT(frame, self.gamma_lut)
            if self.isNegative:
                frame = self.negative(frame)
            if self.isGrayScale:
                frame = self.grayScale(frame)
        return frame

    def getFrame(self):
        return self._frame
