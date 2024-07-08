import cv2

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

class SynchObject(QObject):
    synch_SIGNAL = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sinch = QTimer()
        self.sinch.timeout.connect(self.update)
        self.sinch.start(1000 // 60)

    def update(self):
        self.synch_SIGNAL.emit()


class VideoMixer(QWidget):
    monitorSize = (640, 480)
    _input_frame = None

    def __init__(self, synchObject, parent=None):
        super().__init__(parent)
        self.synchObject = synchObject
        self.resolution = (1920, 1080)
        self.fps = 60
        self.monitor = QLabel()
        self.input1 = None
        self.initUI()
        self.initStyle()
        self.initDemoMode()
        self.initConnections()

    def initUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.monitor)
        self.setLayout(mainLayout)

    def initStyle(self):
        self.monitor.setFixedSize(self.monitorSize[0], self.monitorSize[1])

    def initDemoMode(self):
        self.input1 = cv2.VideoCapture(5)  # put here the index of your camer

    def initConnections(self):
        self.synchObject.synch_SIGNAL.connect(self.captureFrame)

    def captureFrame(self):
        try:
            # there is a best way to do this, but this is just a demo
            ret, cap = self.input1.read()
            if ret:
                input_frame = cv2.resize(cap, self.monitorSize)
                qImage = QImage(input_frame.data, input_frame.shape[1], input_frame.shape[0],
                                QImage.Format.Format_BGR888)
                self._input_frame = QPixmap.fromImage(qImage)
                self.monitor.setPixmap(self._input_frame)
            else:
                print("Error: Unable to capture frame from camera")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    synchObject = SynchObject()
    w = VideoMixer(synchObject)
    w.show()
    sys.exit(app.exec())
