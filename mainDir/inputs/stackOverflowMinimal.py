import threading
import cv2
import numpy as np
import subprocess
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

class VideoStreamer:
    def __init__(self, resolution, fps, rtmp_url):
        self.resolution = resolution
        self.fps = fps
        self.rtmp_url = rtmp_url
        self.streaming = False
        self.command = [
            'ffmpeg',
            '-re',
            '-f', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', f'{resolution[0]}x{resolution[1]}',
            '-r', str(fps),
            '-i', '-',
            '-f', 'lavfi',
            '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-x264-params', 'keyint=48:min-keyint=48:scenecut=-1',
            '-b:v', '4500k',
            '-b:a', '128k',
            '-ar', '44100',
            '-acodec', 'aac',
            '-vcodec', 'libx264',
            '-preset', 'medium',
            '-crf', '28',
            '-threads', '4',
            '-f', 'flv',
            self.rtmp_url
        ]

    def start(self):
        self.streaming = True
        self.pipe = subprocess.Popen(self.command, stdin=subprocess.PIPE)
        self.thread = threading.Thread(target=self.stream)
        self.thread.start()

    def stop(self):
        self.streaming = False
        self.thread.join()
        self.pipe.stdin.close()
        self.pipe.terminate()

    def stream(self):
        while self.streaming:
            if hasattr(self, 'frame'):
                self.pipe.stdin.write(self.frame.tobytes())

    def add_frame(self, frame):
        self.frame = frame

class SynchObject(QObject):
    synch_SIGNAL = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000 // 60)

    def update(self):
        self.synch_SIGNAL.emit()

class VideoMixer(QWidget):
    monitorSize = (640, 480)
    _programFrame = None
    _previewFrame = None
    rtmp_url = 'rtmp://a.rtmp.youtube.com/live2/YOUR_KEY'

    def __init__(self, synchObject, parent=None):
        super().__init__(parent)
        self.synchObject = synchObject
        self.resolution = (1920, 1080)
        self.fps = 60
        self.programMonitor = QLabel()
        self.previewMonitor = QLabel()
        self.input1 = None
        self.input2 = None
        self.btnCut = QPushButton("Cut")
        self.btnStream = QPushButton("Stream")
        self.initUI()
        self.initStyle()
        self.initDemoMode()
        self.initConnections()

    def initUI(self):
        mainLayout = QVBoxLayout()
        monitorLayout = QHBoxLayout()
        monitorLayout.addWidget(self.programMonitor)
        monitorLayout.addWidget(self.previewMonitor)
        mainLayout.addLayout(monitorLayout)
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.btnCut)
        btnLayout.addWidget(self.btnStream)
        mainLayout.addLayout(btnLayout)
        self.setLayout(mainLayout)

    def initStyle(self):
        self.programMonitor.setFixedSize(self.monitorSize[0], self.monitorSize[1])
        self.previewMonitor.setFixedSize(self.monitorSize[0], self.monitorSize[1])

    def initDemoMode(self):
        self.input1 = cv2.VideoCapture(4)
        self.input2 = cv2.VideoCapture(5)
        self.stream = VideoStreamer(self.resolution, self.fps, self.rtmp_url)

    def initConnections(self):
        self.synchObject.synch_SIGNAL.connect(self.updateFrame)
        self.btnCut.clicked.connect(self.cut)
        self.btnStream.clicked.connect(self.streamStart)

    def updateFrame(self):
        self._previewFrame = self.input1.read()[1]
        self._programFrame = self.input2.read()[1]
        self._programFrame = cv2.resize(self._programFrame, self.monitorSize)
        self._previewFrame = cv2.resize(self._previewFrame, self.monitorSize)
        prwImage = QImage(self._previewFrame.data, self._previewFrame.shape[1], self._previewFrame.shape[0], QImage.Format.Format_BGR888)
        prgImage = QImage(self._programFrame.data, self._programFrame.shape[1], self._programFrame.shape[0], QImage.Format.Format_BGR888)
        self.previewMonitor.setPixmap(QPixmap.fromImage(prwImage))
        self.programMonitor.setPixmap(QPixmap.fromImage(prgImage))

    def cut(self):
        prw, prg = self.input1, self.input2
        self.input1, self.input2 = prg, prw
        self.updateFrame()

    def streamStart(self):
        self.stream.start()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    synchObject = SynchObject()
    w = VideoMixer(synchObject)
    w.show()
    sys.exit(app.exec())