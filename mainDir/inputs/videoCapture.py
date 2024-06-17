import threading
import time
from collections import deque
import sys
import cv2
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.inputs.synchObject import SynchObject


# from synchObject import SynchObject

class BaseClass:
    def __init__(self, synchObject, resolution=QSize(1920, 1080)):
        self.synchObject = synchObject
        self.resolution = resolution
        self.synchObject.synch_SIGNAL.connect(self.capture_frame)
        self.start_time = time.time()
        self.frame_count = 0
        self.total_time = 0
        self.fps = 0
        self.last_update_time = time.time()
        self._frame = None
        self._gamma_correction = 1.0
        self.isGrayScale = False
        self.isNegative = False
        self.frame_mutex = QMutex()

    def __del__(self):
        self.stop()
        # Force garbage collection
        self.frame_processor = None
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
        with QMutexLocker(self.frame_mutex):
            if self.camera:
                frame = self.camera.grab()
                if frame is not None:
                    print("Frame grabbed successfully")
                    self._frame = self.frameProcessor(frame)
                else:
                    print("Failed to grab frame")
            else:
                print("Camera not initialized")

    def update_fps(self):
        self.frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        if elapsed_time >= 1.0:  # Update FPS every second
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.last_update_time = current_time

    def gammaCorrection(self, frame, gamma: float):
        invGamma = 1.0 / gamma
        table = np.array([(i / 255.0) ** invGamma * 255 for i in range(256)]).astype("uint8")
        print(f"LUT: {table}")  # Debug: Stampa la LUT
        return cv2.LUT(frame, table)

    def negative(self, frame):
        return cv2.bitwise_not(frame)

    def grayScale(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.merge((gray, gray, gray))

    def frameProcessor(self, frame):
        if self._gamma_correction != 1.0:
            frame = self.gammaCorrection(frame, self._gamma_correction)
            print(f"Gamma Correction Applied with Gamma: {self._gamma_correction}")  # Debug
        if self.isNegative:
            frame = self.negative(frame)
        if self.isGrayScale:
            frame = self.grayScale(frame)
        return frame

    def getFrame(self):
        with QMutexLocker(self.frame_mutex):
            return self._frame


class VideoCaptureSimple(BaseClass):
    def __init__(self, synchObject, resolution=QSize(1920, 1080), input_index=0, isUSB_Cam=False):
        super().__init__(synchObject, resolution)
        self.cameraIndex = input_index
        # List of backends to try
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_VFW, cv2.CAP_ANY]
        self.camera = cv2.VideoCapture(input_index, cv2.CAP_DSHOW)

        if self.camera and self.camera.isOpened():
            self.camera.set(cv2.CAP_PROP_FPS, 60)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution.height())
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution.width())

            self.frameBuffer = deque(maxlen=100)  # Increased buffer size
            self.running = True
            self.capture_thread = threading.Thread(target=self.capture_frames_buffered)
            self.capture_thread.start()

            # Print various properties of the capture device
            fps = self.camera.get(cv2.CAP_PROP_FPS)
            frame_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            frame_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print(f"Capture device FPS: {fps}")
            print(f"Capture device Frame Width: {frame_width}")
            print(f"Capture device Frame Height: {frame_height}")

        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)

    def __del__(self):
        self.stop()

    def stop(self):
        super().stop()
        self.running = False
        self.capture_thread.join()
        if self.camera:
            self.camera.release()
            self.camera = None

    def capture_frames_buffered(self):
        while self.running:
            ret, frame = self.camera.read()
            if ret:
                with QMutexLocker(self.frame_mutex):
                    self.frameBuffer.appendleft(frame)
                    self._frame = self.frameProcessor(frame)
            else:
                print(f"Failed to capture video frame from videoCapture {self.cameraIndex}")
                self.reconnect()

    def capture_frame(self):
        self.update_fps()

    def reconnect(self):
        self.camera.release()
        attempts = 0
        while attempts < 5:
            self.camera = cv2.VideoCapture(self.cameraIndex)
            if self.camera.isOpened():
                break
            attempts += 1
        if attempts == 5:
            print(f"Failed to reconnect to videoCapture {self.cameraIndex}")
            self.camera = None

    def getFrame(self):
        with QMutexLocker(self.frame_mutex):
            return self._frame


class VideoApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.synchObject = SynchObject(50)
        self.input1 = VideoCaptureSimple(self.synchObject, input_index=0, isUSB_Cam=True)
        self.widget = QWidget()
        self.mainLayout = QVBoxLayout()
        self.viewer = QLabel()
        self.fpsLabel = QLabel()
        self.displayLabel = QLabel()
        self.gammaSlider = QSlider(Qt.Horizontal)
        self.invertButton = QPushButton("Invert Image")
        self.grayButton = QPushButton("Grayscale Image")

        self.gammaSlider.setRange(-20, 40)  # Scaling factor to handle gamma from -2 to 4
        self.gammaSlider.setValue(10)  # Initial gamma set to 1 (10 / 10)

        self.gammaSlider.valueChanged.connect(self.update_gamma)
        self.invertButton.clicked.connect(self.toggle_invert)
        self.grayButton.clicked.connect(self.toggle_gray)

        self.mainLayout.addWidget(self.viewer)
        self.mainLayout.addWidget(self.fpsLabel)
        self.mainLayout.addWidget(self.displayLabel)
        self.mainLayout.addWidget(self.gammaSlider)
        self.mainLayout.addWidget(self.invertButton)
        self.mainLayout.addWidget(self.grayButton)

        self.widget.setLayout(self.mainLayout)
        self.widget.show()
        self.viewer.setFixedSize(1280, 720)
        self.uiTimer = QTimer(self)
        self.uiTimer.timeout.connect(self.display_frame)
        self.uiTimer.start(1000 // 30)  # Update UI at 30 FPS
        QTimer.singleShot(60000, self.stop_app)

    def display_frame(self):
        frame = self.input1.getFrame()
        if frame is not None and frame.size != 0:
            start_time = time.time()
            # Maintain aspect ratio while resizing
            target_width = self.viewer.width()
            target_height = self.viewer.height()
            frame_height, frame_width = frame.shape[:2]
            aspect_ratio = frame_width / frame_height

            if target_width / target_height > aspect_ratio:
                new_height = target_height
                new_width = int(aspect_ratio * new_height)
            else:
                new_width = target_width
                new_height = int(new_width / aspect_ratio)

            resized_image = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
            # Convert frame to QImage
            image = QImage(resized_image.data, resized_image.shape[1], resized_image.shape[0], QImage.Format.Format_BGR888)
            self.viewer.setPixmap(QPixmap.fromImage(image))
            display_time = time.time() - start_time
            self.displayLabel.setText(f"Frame displayed in {display_time:.6f} seconds")
            self.fpsLabel.setText(f"FPS: {self.input1.fps:.2f}")

    def update_gamma(self, value):
        gamma = (value + 20) / 10.0
        self.input1.setGammaCorrection(gamma)
        print(f"Gamma set to {gamma}")

    def toggle_invert(self):
        self.input1.isNegative = not self.input1.isNegative
        print(f"Invert set to {self.input1.isNegative}")

    def toggle_gray(self):
        self.input1.isGrayScale = not self.input1.isGrayScale
        print(f"Grayscale set to {self.input1.isGrayScale}")

    def stop_app(self):
        print(f"Media FPS: {self.input1.fps:.2f}")
        self.input1.stop()
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
