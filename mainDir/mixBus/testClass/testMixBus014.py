# Rest of the VideoApp code remains the same
import random

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.inputs.generator_Color import ColorGenerator
from mainDir.inputs.generator_Noise_Random import RandomNoiseImageGenerator
from mainDir.inputs.screenCapture import ScreenCapture
from mainDir.inputs.synchObject import SynchObject
from mainDir.inputs.videoCapture import VideoCaptureSimple
from mainDir.mixBus.mixBus_014 import MixBus014, MIX_TYPE


class mixBusWidget(QWidget):
    viewer1: QLabel = None
    viewer2: QLabel = None
    btnMix: QPushButton = None
    btnCut: QPushButton = None
    btnStinger: QPushButton = None
    btnWipeLeft: QPushButton = None
    btnWipeRight: QPushButton = None
    btnWipeTop: QPushButton = None
    btnWipeBottom: QPushButton = None

    def __init__(self, synchObject: SynchObject, input1, input2):
        super().__init__()
        self.synchObject = synchObject
        self.input1 = input1
        self.input2 = input2
        self.mixBus = MixBus014(self.synchObject)
        self.mixBus.setPreviewInput(self.input1)
        self.mixBus.setProgramInput(self.input2)
        self.initUI()
        self.initGeometry()
        self.initConnections()

    def initUI(self):
        self.viewer1 = QLabel()
        self.viewer2 = QLabel()
        self.btnMix = QPushButton("Start Mix")
        self.btnMix.clicked.connect(self.start_mix)
        self.btnCut = QPushButton("Cut")
        self.btnCut.clicked.connect(self.mixBus.cut)
        self.btnStinger = QPushButton("Stinger")
        self.btnStinger.clicked.connect(self.stinger)
        self.btnWipeLeft = QPushButton("Wipe Left")
        self.btnWipeLeft.clicked.connect(self.wipe_left)
        self.btnWipeRight = QPushButton("Wipe Right")
        self.btnWipeRight.clicked.connect(self.wipe_right)
        self.btnWipeTop = QPushButton("Wipe Top")
        self.btnWipeTop.clicked.connect(self.wipe_top)
        self.btnWipeBottom = QPushButton("Wipe Bottom")
        self.btnWipeBottom.clicked.connect(self.wipe_bottom)

        mainLayout = QVBoxLayout()
        monitorLayout = QHBoxLayout()
        monitorLayout.addWidget(self.viewer1)
        monitorLayout.addWidget(self.viewer2)
        mainLayout.addLayout(monitorLayout)
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.btnMix)
        btnLayout.addWidget(self.btnCut)
        btnLayout.addWidget(self.btnStinger)
        btnLayout.addWidget(self.btnWipeLeft)
        btnLayout.addWidget(self.btnWipeRight)
        btnLayout.addWidget(self.btnWipeTop)
        btnLayout.addWidget(self.btnWipeBottom)
        mainLayout.addLayout(btnLayout)
        self.setLayout(mainLayout)

    def initGeometry(self):
        self.viewer1.setFixedSize(640, 480)
        self.viewer1.setScaledContents(True)
        self.viewer2.setFixedSize(640, 480)
        self.viewer2.setScaledContents(True)

    def initConnections(self):
        self.uiTimer = QTimer(self)
        self.uiTimer.timeout.connect(self.display_frame)
        self.uiTimer.start(1000 // 60)


    def start_mix(self):
        self.mixBus._mixType = MIX_TYPE.MIX
        self.mixBus.startMix()

    def stinger(self):
        self.mixBus._mixType = MIX_TYPE.STINGER
        self.mixBus.startStinger()

    def wipe_left(self):
        self.mixBus._mixType = MIX_TYPE.WIPE_LEFT
        self.mixBus.startMix()

    def wipe_right(self):
        self.mixBus._mixType = MIX_TYPE.WIPE_RIGHT
        self.mixBus.startMix()

    def wipe_top(self):
        self.mixBus._mixType = MIX_TYPE.WIPE_TOP
        self.mixBus.startMix()

    def wipe_bottom(self):
        self.mixBus._mixType = MIX_TYPE.WIPE_BOTTOM
        self.mixBus.startMix()

    def changeInput(self, newInput):
        self.mixBus.setPreviewInput(newInput)

    def display_frame(self):
        try:
            prw, prg = self.mixBus.getMix()
            if prg is not None:
                image = QImage(prg.data, prg.shape[1], prg.shape[0], QImage.Format.Format_BGR888)
                self.viewer2.setPixmap(QPixmap.fromImage(image))
            if prw is not None:
                image = QImage(prw.data, prw.shape[1], prw.shape[0], QImage.Format.Format_BGR888)
                self.viewer1.setPixmap(QPixmap.fromImage(image))
        except Exception as e:
            print(e)
            print(type(self.mixBus.getMix()))


class VideoApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.synchObject = SynchObject(60)
        self.input1 = ScreenCapture(self.synchObject, screen_index=1)
        self.input2 = ColorGenerator(self.synchObject)
        self.input2.setColor(color=QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

        self.widget = mixBusWidget(self.synchObject, self.input1, self.input2)
        self.widget.show()
        QTimer.singleShot(60000, self.stop_app)
    def stop_app(self):
        self.exit()


if __name__ == "__main__":
    import sys


    def main():
        app = VideoApp(sys.argv)
        app.exec()


    main()
