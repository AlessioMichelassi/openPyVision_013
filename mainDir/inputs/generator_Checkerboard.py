import numpy as np
import cv2
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QImage

from mainDir.inputs.baseClass import BaseClass
from mainDir.inputs.synchObject import SynchObject


class CheckerBoardGenerator(BaseClass):
    def __init__(self, synchObject, resolution=QSize(1920, 1080), square_size=60):
        super().__init__(synchObject, resolution)
        self.square_size = square_size
        self._frame = self.generate_checkerboard()

    def setSquareSize(self, square_size):
        self.square_size = square_size
        self._frame = self.generate_checkerboard()

    def generate_checkerboard(self):
        rows, cols = self.resolution.height(), self.resolution.width()
        # Calculate number of squares needed
        num_rows = rows // self.square_size
        num_cols = cols // self.square_size

        # Initialize checkerboard pattern
        checkerboard = np.zeros((rows, cols), dtype=np.uint8)

        # Fill the checkerboard with white (255) and grey (127) squares
        for row in range(num_rows):
            for col in range(num_cols):
                if (row + col) % 2 == 0:
                    checkerboard[row * self.square_size:(row + 1) * self.square_size,
                    col * self.square_size:(col + 1) * self.square_size] = 255
                else:
                    checkerboard[row * self.square_size:(row + 1) * self.square_size,
                    col * self.square_size:(col + 1) * self.square_size] = 127

        # Convert single channel to 3 channel
        checkerboard = np.dstack([checkerboard] * 3)
        return checkerboard

    def capture_frame(self):
        super().capture_frame()
        self._frame = self.generate_checkerboard()

    def getFrame(self):
        return self._frame


# Example usage
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QLabel
    from PyQt6.QtGui import QPixmap

    app = QApplication(sys.argv)
    synchObject = SynchObject()

    checkerboard_input = CheckerBoardGenerator(synchObject)
    window = QLabel()
    window.setFixedSize(1920, 1080)


    def update_display():
        frame = checkerboard_input.getFrame()
        if frame is not None:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            qimg = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            window.setPixmap(QPixmap(qimg))


    synchObject.synch_SIGNAL.connect(update_display)
    window.show()
    sys.exit(app.exec())
