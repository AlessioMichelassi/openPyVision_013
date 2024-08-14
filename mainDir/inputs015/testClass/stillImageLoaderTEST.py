import time

import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from cap2.cap2_6.synchObject import SynchObject
from cap3.cap3_1.stillImageLoader import StillImageLoader


class VideoApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.synchObject = SynchObject(60)
        # insert the full path to the image file
        self.input1 = StillImageLoader(r"\openPyVisionBook\cap3\cap3_1\testClass\Grass_Valley_110_Switcher.jpg",
                                       self.synchObject)
        self.widget = QWidget()
        self.mainLayout = QVBoxLayout()
        self.viewer = QLabel()
        self.fpsLabel = QLabel("FPS: 0.00")  # Initialize FPS label
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
            image = QImage(frame.data, frame.shape[1], frame.shape[0],
                           QImage.Format.Format_BGR888)
            self.viewer.setPixmap(QPixmap.fromImage(image))
            display_time = time.time() - start_time
            self.displayLabel.setText(f"Frame displayed in {display_time:.6f} seconds")
            self.fpsLabel.setText(f"FPS: {self.input1.fps:.2f}")  # Update FPS label

    def stop_app(self):
        print(f"Media FPS: {self.input1.fps:.2f}")
        self.exit()


if __name__ == "__main__":
    import sys


    def main():
        app = VideoApp(sys.argv)
        app.exec()


    if __name__ == '__main__':
        main()
