import sys
import time
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap

from mainDir.inputs.synchObject import SynchObject
from mainDir.inputs.testClass.uMat_vs_NumpyTest.uMatScreenCapture import Umat_ScreenCapture


class FrameConverter:
    def convert(self, frame: cv2.UMat):
        image = QImage(frame.get().data, frame.get().shape[1], frame.get().shape[0], QImage.Format.Format_BGR888)
        return QPixmap.fromImage(image)


frame_converter = FrameConverter()


class VideoApp(QApplication):
    def __init__(self, argv, converter, duration=60):
        super().__init__(argv)
        self.synchObject = SynchObject(60)
        self.input1 = Umat_ScreenCapture(self.synchObject, screen_index=1)
        self.converter = converter
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
        self.media_fps = 0
        self.uiTimer = QTimer(self)
        self.uiTimer.timeout.connect(self.display_frame)
        self.uiTimer.start(1000 // 60)  # Update UI at 60 FPS
        QTimer.singleShot(duration * 1000, self.stop_app)

    def display_frame(self):
        frame = self.input1.getFrame()
        if frame is not None:
            start_time = time.time()
            if self.converter is not None:
                pixmap = self.converter.convert(frame)  # Use the provided converter
                self.viewer.setPixmap(pixmap)
            else:
                image = QImage(frame.get().data, frame.get().shape[1], frame.get().shape[0], QImage.Format.Format_BGR888)
                self.viewer.setPixmap(QPixmap.fromImage(image))
            display_time = time.time() - start_time
            self.displayLabel.setText(f"Frame displayed in {display_time:.6f} seconds")
            self.fpsLabel.setText(f"FPS: {self.input1.fps:.2f}")

    def stop_app(self):
        self.media_fps = self.input1.fps
        print(f"Media FPS: {self.input1.fps:.2f}")
        try:
            self.input1.stop()
            cv2.destroyAllWindows()  # Close all OpenCV windows
        except Exception as e:
            print(e)
        self.exit()


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
