import numpy as np
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QColor

from mainDir.inputs.baseClass import BaseClass


class GradientGenerator(BaseClass):

    def __init__(self, synchObject, resolution=QSize(1920, 1080), gradient_type='vertical', start_color=QColor(255, 255, 255),
                 end_color=QColor(0, 0, 0)):
        super().__init__(synchObject, resolution)
        self.gradient_type = gradient_type
        self.start_color = np.array([start_color.red(), start_color.green(), start_color.blue()], dtype=np.float32)
        self.end_color = np.array([end_color.red(), end_color.green(), end_color.blue()], dtype=np.float32)
        self.target_resolution = (resolution.height(), resolution.width())
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)
        self.createGradient()

    def createGradient(self):
        if self.gradient_type == 'vertical':
            self._frame = self.generate_vertical_gradient()
        elif self.gradient_type == 'radial':
            self._frame = self.generate_radial_gradient()
        else:
            raise ValueError("gradient_type must be 'vertical' or 'radial'")

    def generate_vertical_gradient(self):
        height, width = self.resolution.height(), self.resolution.width()
        gradient = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(3):  # Iterate over the color channels
            gradient[:, :, i] = np.linspace(self.start_color[i], self.end_color[i], height, dtype=np.uint8)[:, None]
        return gradient

    def generate_radial_gradient(self):
        height, width = self.resolution.height(), self.resolution.width()
        center_x, center_y = width // 2, height // 2
        max_radius = np.sqrt(center_x ** 2 + center_y ** 2)
        y, x = np.ogrid[:height, :width]
        distance = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
        ratio = np.clip(distance / max_radius, 0, 1)
        gradient = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(3):  # Iterate over the color channels
            gradient[:, :, i] = (self.start_color[i] * (1 - ratio) + self.end_color[i] * ratio).astype(np.uint8)
        return gradient

    def stop(self):
        super().stop()

    def captureFrame(self):
        self.updateFps()

    def getFrame(self):
        return self._frame


import time

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from mainDir.inputs.synchObject import SynchObject


class VideoApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.synchObject = SynchObject(60)  # Set FPS to 60
        self.input1 = GradientGenerator(self.synchObject, gradient_type='radial')
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


# Example usage of the GradientGenerator class

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
