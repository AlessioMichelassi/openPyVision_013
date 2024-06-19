import time
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from mainDir.inputs.generator_Gradients import GradientGenerator
from mainDir.inputs.screenCapture import ScreenCapture
from mainDir.inputs.synchObject import SynchObject
from mainDir.inputs.baseClass import BaseClass


class VideoApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.synchObject = SynchObject(60)
        self.input1 = ScreenCapture(self.synchObject, screen_index=1)
        self.widget = QWidget()
        self.viewer = QLabel()
        self.lneGamma = QLineEdit()
        self.btnSetGamma = QPushButton("Set Gamma")
        self.btnInvert = QPushButton("Invert")
        self.btnGray = QPushButton("Gray Scale")
        self.btnScreen = QPushButton("Screen Effect")
        self.btnMaskScreen = QPushButton("Mask Screen Effect")
        self.btnFlip = QPushButton("Flip")
        self.btnBlur = QPushButton("Blur")
        self.btnBypass = QPushButton("Bypass All Effects")
        self.fpsLabel = QLabel()
        self.displayLabel = QLabel()
        self.mainLayout = self.initLayout()
        self.widget.setLayout(self.mainLayout)
        self.widget.show()
        self.viewer.setFixedSize(1920, 1080)
        self.initConnections()

        self.uiTimer = QTimer(self)
        self.uiTimer.timeout.connect(self.display_frame)
        self.uiTimer.start(1000 // 60)  # Update UI at 60 FPS
        QTimer.singleShot(80000, self.stop_app)

    def initLayout(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.viewer)
        monitorLayout = QHBoxLayout()
        monitorLayout.addWidget(self.displayLabel)
        monitorLayout.addWidget(self.fpsLabel)
        mainLayout.addLayout(monitorLayout)
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.lneGamma)
        btnLayout.addWidget(self.btnSetGamma)
        btnLayout.addWidget(self.btnInvert)
        btnLayout.addWidget(self.btnGray)
        btnLayout.addWidget(self.btnScreen)
        btnLayout.addWidget(self.btnMaskScreen)
        btnLayout.addWidget(self.btnFlip)
        btnLayout.addWidget(self.btnBlur)
        btnLayout.addWidget(self.btnBypass)
        mainLayout.addLayout(btnLayout)
        return mainLayout

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

    def initConnections(self):
        self.btnSetGamma.clicked.connect(self.setGamma)
        self.btnInvert.clicked.connect(self.toggleInvert)
        self.btnGray.clicked.connect(self.toggleGray)
        self.btnScreen.clicked.connect(self.toggleScreen)
        self.btnMaskScreen.clicked.connect(self.toggleMaskScreen)
        self.btnFlip.clicked.connect(self.toggleFlip)
        self.btnBlur.clicked.connect(self.toggleBlur)
        self.btnBypass.clicked.connect(self.bypassEffects)

    def setGamma(self):
        gamma = float(self.lneGamma.text())
        if self.input1:
            self.input1.setGammaCorrection(gamma)

    def toggleInvert(self):
        if self.input1:
            self.input1.isNegative = not self.input1.isNegative

    def toggleGray(self):
        if self.input1:
            self.input1.isGrayScale = not self.input1.isGrayScale

    def toggleScreen(self):
        if self.input1:
            self.input1.isSelfScreen = not self.input1.isSelfScreen

    def toggleMaskScreen(self):
        if self.input1:
            self.input1.isMaskedScreen = not self.input1.isMaskedScreen

    def toggleFlip(self):
        if self.input1:
            self.input1.isFlipped = not self.input1.isFlipped

    def toggleBlur(self):
        if self.input1:
            self.input1.isBlurred = not self.input1.isBlurred

    def bypassEffects(self):
        if self.input1:
            self.input1.isNegative = False
            self.input1.isGrayScale = False
            self.input1.isSelfScreen = False
            self.input1.isMaskedScreen = False


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
