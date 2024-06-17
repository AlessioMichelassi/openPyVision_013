import cv2
import numpy as np
from PyQt6.QtCore import QSize

from mainDir.inputs.baseClass import BaseClass


class CheckerboardGenerator(BaseClass):

    def __init__(self, synchObject, resolution=QSize(1920, 1080), num_rows=10, num_cols=8, color1=(192, 192, 192),
                 color2=(64, 64, 64)):
        super().__init__(synchObject, resolution)
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.color1 = color1
        self.color2 = color2
        self.target_resolution = (resolution.height(), resolution.width())
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)
        self.createCheckerboard()

    def createCheckerboard(self):
        height, width = self.resolution.height(), self.resolution.width()
        # Calcola la dimensione dei singoli quadrati in modo che siano quadrati
        square_size = min(height // self.num_rows, width // self.num_cols)

        # Calcola il nuovo numero di righe e colonne per occupare tutta l'immagine
        num_rows_adjusted = height // square_size
        num_cols_adjusted = width // square_size

        # Genera una scacchiera centrata
        checkerboard = np.zeros((height, width, 3), dtype=np.uint8)
        for row in range(num_rows_adjusted):
            for col in range(num_cols_adjusted):
                top_left_y = row * square_size
                top_left_x = col * square_size
                bottom_right_y = top_left_y + square_size
                bottom_right_x = top_left_x + square_size
                color = self.color1 if (row + col) % 2 == 0 else self.color2
                cv2.rectangle(checkerboard, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), color, -1)

        # Centro la scacchiera
        y_offset = (height - num_rows_adjusted * square_size) // 2
        x_offset = (width - num_cols_adjusted * square_size) // 2
        self._frame[y_offset:y_offset + num_rows_adjusted * square_size,
        x_offset:x_offset + num_cols_adjusted * square_size] = checkerboard[
                                                               y_offset:y_offset + num_rows_adjusted * square_size,
                                                               x_offset:x_offset + num_cols_adjusted * square_size]


    def stop(self):
        super().stop()

    def capture_frame(self):
        self._numpyFrame = np.ascontiguousarray(self._frame)
        self.update_fps()

    def getFrame(self):
        return self._numpyFrame


import time

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from mainDir.inputs.synchObject import SynchObject


class VideoApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.synchObject = SynchObject(60)  # Set FPS to 60
        self.input1 = CheckerboardGenerator(self.synchObject)
        self.widget = QWidget()
        self.mainLayout = QVBoxLayout()
        self.viewer = QLabel()
        self.fpsLabel = QLabel()
        self.displayLabel = QLabel()
        self.mainLayout.addWidget(self.viewer)
        self.mainLayout.addWidget(self.fpsLabel)
        self.mainLayout.addWidget(self.displayLabel)
        self.widget.setLayout(self.mainLayout)
        self.widget.show()
        self.viewer.setFixedSize(1920, 1080)
        self.uiTimer = QTimer(self)
        self.uiTimer.timeout.connect(self.display_frame)
        self.uiTimer.start(1000 // 30)  # Update UI at 30 FPS
        QTimer.singleShot(10000, self.stop_app)

    def display_frame(self):
        frame = self.input1.getFrame()
        if frame is not None and frame.size != 0:
            start_time = time.time()
            image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_BGR888)
            self.viewer.setPixmap(QPixmap.fromImage(image))
            display_time = time.time() - start_time
            self.displayLabel.setText(f"Frame displayed in {display_time:.6f} seconds")
            self.fpsLabel.setText(f"FPS: {self.input1.fps:.2f}")

    def stop_app(self):
        print(f"Media FPS: {self.input1.fps:.2f}")
        self.exit()


# Example usage of the CheckerboardGenerator class

if __name__ == "__main__":
    import sys


    def main():
        app = VideoApp(sys.argv)
        app.exec()


    if __name__ == '__main__':
        import cProfile
        import pstats
        import io

        pr = cProfile.Profile()
        pr.enable()
        main()
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
