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


class VideoApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.synchObject = SynchObject(60)
        self.input1 = RandomNoiseImageGenerator(self.synchObject)
        self.input2 = ColorGenerator(self.synchObject)
        self.input2.setColor(color=QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        self.input3 = ScreenCapture(self.synchObject, screen_index=1)
        self.input4 = VideoCaptureSimple(self.synchObject, input_index=8)
        self.inputList = [self.input1, self.input2, self.input3, self.input4]
        self.widget = QWidget()
        self.mainLayout = QVBoxLayout()
        self.mixBus = MixBus014(self.synchObject)
        self.mixBus.setPreviewInput(self.input1)
        self.mixBus.setProgramInput(self.input2)
        self.viewer = QLabel()
        self.fpsLabel = QLabel()
        self.displayLabel = QLabel()
        self.mainLayout.addWidget(self.viewer)
        self.mainLayout.addWidget(self.fpsLabel)
        self.mainLayout.addWidget(self.displayLabel)
        self.btnMix = QPushButton("Start Mix")
        self.btnMix.clicked.connect(self.start_mix)
        self.btnWipeLeft = QPushButton("Wipe Left")
        #self.btnWipeLeft.clicked.connect(self.wipe_left)
        self.btnWipe_Right = QPushButton("Wipe Right")
       # self.btnWipe_Right.clicked.connect(self.wipe_right)
        self.btnWipe_Bottom = QPushButton("Wipe Bottom")
        #self.btnWipe_Bottom.clicked.connect(self.wipe_bottom)
        self.btnWipe_Top = QPushButton("Wipe Top")
        #self.btnWipe_Top.clicked.connect(self.wipe_top)
        self.btnStinger = QPushButton("Stinger")
        self.btnStinger.clicked.connect(self.stinger)
        self.btnCut = QPushButton("Cut")
        self.btnCut.clicked.connect(self.mixBus.cut)
        self.btnChangePreview = QPushButton("Change Preview Input")
        self.btnChangePreview.clicked.connect(self.changeInput)
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.btnMix)
        btnLayout.addWidget(self.btnCut)
        btnLayout.addWidget(self.btnChangePreview)
        btnLayout.addWidget(self.btnWipeLeft)
        btnLayout.addWidget(self.btnWipe_Right)
        btnLayout.addWidget(self.btnWipe_Bottom)
        btnLayout.addWidget(self.btnWipe_Top)
        btnLayout.addWidget(self.btnStinger)
        self.mainLayout.addLayout(btnLayout)
        self.widget.setLayout(self.mainLayout)
        self.widget.show()
        self.viewer.setFixedSize(1920, 1080)
        self.uiTimer = QTimer(self)
        self.uiTimer.timeout.connect(self.display_frame)
        self.uiTimer.start(1000 // 30)
        QTimer.singleShot(60000, self.stop_app)
        self.frame_times = []

    def display_frame(self):
        try:
            prw, prg = self.mixBus.getMix()
            if prg is not None and prg.size != 0:
                image = QImage(prg.data, prg.shape[1], prg.shape[0], QImage.Format.Format_BGR888)
                self.viewer.setPixmap(QPixmap.fromImage(image))
        except Exception as e:
            print(e)
            print(type(self.mixBus.getMix()))

    def changeInput(self):
        randomInput = random.choice(self.inputList)
        if randomInput != self.mixBus.program_input:
            self.mixBus.setPreviewInput(randomInput)
            print(f"Changed program input to {randomInput}")
        else:
            self.changeInput()

    def start_mix(self):
        self.mixBus._mixType = MIX_TYPE.MIX
        self.mixBus.startMix()

    """def wipe_left(self):
        self.mixBus._mixType = MIX_TYPE.WIPE_LEFT
        self.mixBus.startMix()

    def wipe_right(self):
        self.mixBus._mixType = MIX_TYPE.WIPE_RIGHT
        self.mixBus.startMix()

    def wipe_bottom(self):
        self.mixBus._mixType = MIX_TYPE.WIPE_BOTTOM
        self.mixBus.startMix()

    def wipe_top(self):
        self.mixBus._mixType = MIX_TYPE.WIPE_TOP
        self.mixBus.startMix()"""

    def stinger(self):
        self.mixBus._mixType = MIX_TYPE.STINGER
        self.mixBus.startMix()

    def stop_app(self):
        if self.frame_times:
            avg_fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))
            print(f"Average FPS: {avg_fps:.2f}")
        for input_object in self.inputList:
            input_object.stop()
        self.exit()


if __name__ == "__main__":
    import sys


    def main():
        app = VideoApp(sys.argv)
        app.exec()


    main()