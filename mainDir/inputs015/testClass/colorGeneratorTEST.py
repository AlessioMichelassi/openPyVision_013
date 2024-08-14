import time

import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.inputs015.generator_Color015 import ColorGenerator015
from mainDir.inputs015.synchObject import SynchObject


class VideoApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        # init external object
        self.synchObject = SynchObject(60)
        self.input1 = ColorGenerator015(self.synchObject)
        # init internal widget
        self.widget = QWidget()
        self.viewer = QLabel()
        self.fpsLabel = QLabel("FPS: 0.00")  # Initialize FPS label
        self.displayLabel = QLabel()
        self.uiTimer = QTimer(self)
        self.uiTimer.start(1000 // 30)  # Update UI at 30 FPS
        # init the interface
        self.initUI()
        self.initConnections()
        self.initGeometry()
        # test the payload
        self.testPayload()

    def initUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.viewer)
        mainLayout.addWidget(self.fpsLabel)
        mainLayout.addWidget(self.displayLabel)
        self.widget.setLayout(mainLayout)

    def initConnections(self):
        self.uiTimer.timeout.connect(self.display_frame)
        QTimer.singleShot(10000, self.stop_app)

    def initGeometry(self):
        self.widget.setGeometry(10, 50, 1920, 1080)
        self.widget.show()

    def testPayload(self):
        print("Payload test")
        self.input1.setColor(QColor(0, 0, 255))
        #self.input1.isFlipped = True
        #self.input1.isFrameInverted = True
        self.input1.isAutoScreen = True
        self.input1.isFrameHistogramEqualizationYUV = True

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
    import cProfile
    import pstats
    import io

    def main():
        app = VideoApp(sys.argv)
        app.exec()

    pr = cProfile.Profile()
    pr.enable()
    main()
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

