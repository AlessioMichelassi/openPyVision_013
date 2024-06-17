import numpy as np
from PyQt6.QtCore import QSize
from mainDir.inputs.baseClass import BaseClass


class RandomNoiseImageGenerator(BaseClass):
    def __init__(self, synchObject, resolution=QSize(1920, 1080)):
        super().__init__(synchObject, resolution)
        self.generate_noise()

    def generate_noise(self):
        height, width = self.resolution.height(), self.resolution.width()
        noise = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        return np.ascontiguousarray(noise)

    def stop(self):
        super().stop()

    def capture_frame(self):
        self._frame = self.generate_noise()
        self.update_fps()

    def getFrame(self):
        return self._frame


import sys
import time

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from mainDir.inputs.synchObject import SynchObject


class VideoApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.synchObject = SynchObject(60)  # Set FPS to 60
        self.input1 = RandomNoiseImageGenerator(self.synchObject)
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


# Example usage of the ColorGenerator class

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
