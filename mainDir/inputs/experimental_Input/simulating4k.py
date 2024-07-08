import time
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class SynchObject(QObject):
    """
    A class to emit synchronization signals at a specified FPS.
    """
    synch_SIGNAL = pyqtSignal()

    def __init__(self, fps=60, parent=None):
        """
        Initialize the SynchObject with a specified FPS.

        :param fps: Frames per second
        :param parent: Parent QObject
        """
        super().__init__(parent)
        self.fps = fps
        self.syncTimer = QTimer(self)
        self.syncTimer.timeout.connect(self.sync)
        self.syncTimer.start(1000 // fps)  # Set timer interval based on FPS
        self._initialized = True

    def sync(self):
        """
        Emit the synchronization signal.
        """
        self.synch_SIGNAL.emit()

class RandomNoiseImageGenerator(QObject):
    """
    A class to generate frames of random noise and update FPS.
    """
    def __init__(self, synchObject, resolution=QSize(3840, 2160)):
        """
        Initialize the RandomNoiseImageGenerator with a synchronization object and resolution.

        :param synchObject: The SynchObject to synchronize frame generation
        :param resolution: Resolution of the generated frames
        """
        super().__init__()
        self._frame = None
        self.frame_count = 0
        self.last_update_time = time.time()
        self.resolution = resolution
        self.synchObject = synchObject
        self.fps = self.synchObject.fps
        self._frame = self.generate_noise()  # Generate initial noise frame
        self.setPayload(True)

    def setPayload(self, _isPayload):
        """
        Simulate a workload based on the computer's CPU if needed.

        :param _isPayload: Flag to simulate workload
        """
        # Connect the sync signal to the capture_frame slot
        self.synchObject.synch_SIGNAL.connect(self.capture_frame)

    def generate_noise(self):
        """
        Generate a frame of random noise.

        :return: A frame of random noise as a numpy array
        """
        height, width = self.resolution.height(), self.resolution.width()
        # Use uint16 to allow 10-bit depth (0-1023 range)
        return np.ascontiguousarray(np.random.randint(0, 1024, (height, width, 3), dtype=np.uint16))

    def capture_frame(self):
        """
        Capture a new frame of random noise and update FPS.
        """
        self._frame = self.generate_noise()
        self.update_fps()

    def getFrame(self):
        """
        Get the current frame.

        :return: The current frame or a white frame if no frame is available
        """
        if self._frame is None:
            return np.ones((self.resolution.height(), self.resolution.width(), 3), dtype=np.uint16) * 1023
        return self._frame

    def update_fps(self):
        """
        Update the FPS (frames per second) value.
        """
        self.frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        if elapsed_time >= 1.0:  # Update FPS every second
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.last_update_time = current_time

class VideoApp(QApplication):
    """
    The main PyQt application to display random noise frames and show FPS.
    """
    def __init__(self, argv):
        """
        Initialize the VideoApp with command line arguments.

        :param argv: Command line arguments
        """
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
        self.viewer.setFixedSize(1920, 1080)  # Set viewer size to 4K
        self.uiTimer = QTimer(self)
        self.uiTimer.timeout.connect(self.display_frame)
        self.uiTimer.start(1000 // 30)  # Update UI at 30 FPS
        QTimer.singleShot(10000, self.stop_app)  # Stop the app after 10 seconds

    def display_frame(self):
        """
        Display the current frame and update FPS and display time.
        """
        frame = self.input1.getFrame()
        if frame is not None and frame.size != 0:
            start_time = time.time()
            # Convert the frame to QImage and display it
            image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB30)
            self.viewer.setPixmap(QPixmap.fromImage(image))
            display_time = time.time() - start_time
            self.displayLabel.setText(f"Frame displayed in {display_time:.6f} seconds")
            self.fpsLabel.setText(f"FPS: {self.input1.fps:.2f}")

    def stop_app(self):
        """
        Print the average FPS and exit the application.
        """
        print(f"Media FPS: {self.input1.fps:.2f}")
        self.exit()

# Example usage of the VideoApp class

if __name__ == "__main__":
    import sys

    def main():
        app = VideoApp(sys.argv)
        app.exec()

    if __name__ == '__main__':
        import cProfile
        import pstats
        import io

        # Profile the main function to analyze performance
        pr = cProfile.Profile()
        pr.enable()
        main()
        pr.disable()

        # Use pstats to sort and print the profiling results
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

# cProfile.Profile() is used to profile the performance of the application. It records the execution time of different functions.
# pstats is used to analyze and sort the profiling results. It helps to identify which parts of the code are consuming the most time.
