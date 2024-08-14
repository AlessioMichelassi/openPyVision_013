import sys
import time
import cv2
import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from mainDir.inputs.generator_Checkerboard import CheckerBoardGenerator
from mainDir.inputs.generator_Color import ColorGenerator
from mainDir.inputs.generator_Gradients import GradientGenerator
from mainDir.inputs.generator_bars_EBU import FullBarsGenerator
from mainDir.inputs.generator_bars_SMPTE import SMPTEBarsGenerator
from mainDir.inputs.screenCapture import ScreenCapture
from mainDir.inputs.synchObject import SynchObject


# NOT WORKING PROPERLY
class WidgetTest(QWidget):
    def __init__(self):
        super().__init__()

        self.synchObject = SynchObject(60)
        self.inputs = {
            "Full Bars": FullBarsGenerator(self.synchObject),
            "SMPTE Bars": SMPTEBarsGenerator(self.synchObject),
            "Color Generator": ColorGenerator(self.synchObject),
            "Screen Capture": ScreenCapture(self.synchObject, screen_index=1)
        }
        self.masks = {
            "Vertical Gradient": GradientGenerator(self.synchObject, gradient_type='vertical'),
            "Radial Gradient": GradientGenerator(self.synchObject, gradient_type='radial'),
            "Checkerboard": CheckerBoardGenerator(self.synchObject)
        }

        self.current_input = None
        self.current_mask = None

        self.viewerOriginal = QLabel()
        self.viewerEffectApplied = QLabel()
        self.viewerMask = QLabel()
        self.cmbInput = QComboBox()
        self.cmbMask = QComboBox()
        self.lneGamma = QLineEdit()
        self.btnSetGamma = QPushButton("Set Gamma")
        self.btnInvert = QPushButton("Invert")
        self.btnGray = QPushButton("Gray Scale")
        self.btnScreen = QPushButton("Screen Effect")
        self.btnMaskScreen = QPushButton("Mask Screen Effect")
        self.btnBypass = QPushButton("Bypass All Effects")
        self.fpsViewer1 = QLabel()
        self.fpsViewer2 = QLabel()
        self.initUI()
        self.initConnections()
        self.initGeometry()
        self.selectInput()  # Select default input
        self.selectMask()  # Select default mask

    def initUI(self):
        mainLayout = QVBoxLayout()
        monitorLayout = QHBoxLayout()
        monitor1 = QVBoxLayout()
        monitor1.addWidget(self.viewerOriginal)
        lbl = QLabel("Original Frame - fps: ")
        monitor1.addWidget(lbl)
        monitor1.addWidget(self.fpsViewer1)
        monitorLayout.addLayout(monitor1)
        monitor2 = QVBoxLayout()
        monitor2.addWidget(self.viewerEffectApplied)
        lbl = QLabel("Effect Applied - fps: ")
        monitor2.addWidget(lbl)
        monitor2.addWidget(self.fpsViewer2)
        monitorLayout.addLayout(monitor2)
        mainLayout.addLayout(monitorLayout)
        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.viewerMask)
        controlLayout.addWidget(QLabel("Select Input:"))
        self.cmbInput.addItems(self.inputs.keys())
        controlLayout.addWidget(self.cmbInput)

        controlLayout.addWidget(QLabel("Select Mask:"))
        self.cmbMask.addItems(self.masks.keys())
        controlLayout.addWidget(self.cmbMask)

        controlLayout.addWidget(QLabel("Gamma:"))
        controlLayout.addWidget(self.lneGamma)
        controlLayout.addWidget(self.btnSetGamma)
        controlLayout.addWidget(self.btnInvert)
        controlLayout.addWidget(self.btnGray)
        controlLayout.addWidget(self.btnScreen)
        controlLayout.addWidget(self.btnMaskScreen)
        controlLayout.addWidget(self.btnBypass)

        mainLayout.addLayout(controlLayout)
        self.setLayout(mainLayout)

    def initConnections(self):
        self.cmbInput.currentIndexChanged.connect(self.selectInput)
        self.cmbMask.currentIndexChanged.connect(self.selectMask)
        self.btnSetGamma.clicked.connect(self.setGamma)
        self.btnInvert.clicked.connect(self.toggleInvert)
        self.btnGray.clicked.connect(self.toggleGray)
        self.btnScreen.clicked.connect(self.toggleScreen)
        self.btnMaskScreen.clicked.connect(self.toggleMaskScreen)
        self.btnBypass.clicked.connect(self.bypassEffects)
        self.synchObject.synch_SIGNAL.connect(self.displayFrame)

    def initGeometry(self):
        self.viewerOriginal.setStyleSheet("border: 1px solid black; background-color: black;")
        self.viewerOriginal.setFixedSize(720, 480)
        self.viewerEffectApplied.setFixedSize(720, 480)
        self.viewerEffectApplied.setStyleSheet("border: 1px solid black; background-color: black;")
        self.viewerMask.setFixedSize(720, 480)
        self.viewerMask.setStyleSheet("border: 1px solid black; background-color: black;")

    def selectInput(self):
        input_name = self.cmbInput.currentText()
        self.current_input = self.inputs[input_name]

    def selectMask(self):
        """mask_name = self.cmbMask.currentText()
        self.current_mask = self.masks[mask_name]
        if self.current_input:
            self.current_input.screenMask = self.current_mask
            #self.current_input.isMaskedScreen = True"""
        return

    def setGamma(self):
        gamma = float(self.lneGamma.text())
        if self.current_input:
            self.current_input.setGammaCorrection(gamma)

    def toggleInvert(self):
        if self.current_input:
            self.current_input.isNegative = not self.current_input.isNegative

    def toggleGray(self):
        if self.current_input:
            self.current_input.isGrayScale = not self.current_input.isGrayScale

    def toggleScreen(self):
        if self.current_input:
            self.current_input.isSelfScreen = not self.current_input.isSelfScreen

    def toggleMaskScreen(self):
        if self.current_input:
            self.current_input.isMaskedScreen = not self.current_input.isMaskedScreen

    def bypassEffects(self):
        if self.current_input:
            self.current_input.isNegative = False
            self.current_input.isGrayScale = False
            self.current_input.isSelfScreen = False
            self.current_input.isMaskedScreen = False

    def displayFrame(self):
        if self.current_input:
            start_time = time.time()
            frame = self.current_input.getFrame()
            if frame is not None and frame.size != 0:
                processed_frame = self.current_input.frameProcessor(frame)
                mask_frame = self.current_mask.getFrame() if self.current_mask else np.zeros_like(frame)

                image_original = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_BGR888)
                image_processed = QImage(processed_frame.data, processed_frame.shape[1], processed_frame.shape[0],
                                         QImage.Format.Format_BGR888)
                image_mask = QImage(mask_frame.data, mask_frame.shape[1], mask_frame.shape[0],
                                    QImage.Format.Format_BGR888)

                self.viewerOriginal.setPixmap(QPixmap.fromImage(image_original.scaled(720, 480)))
                self.viewerEffectApplied.setPixmap(QPixmap.fromImage(image_processed.scaled(720, 480)))
                self.viewerMask.setPixmap(QPixmap.fromImage(image_mask.scaled(720, 480)))

            end_time = time.time()
            elapsed_time = end_time - start_time
            fps = 1.0 / elapsed_time if elapsed_time > 0 else 0
            self.fpsViewer1.setText(f"{self.current_input.fps:.2f}")
            self.fpsViewer2.setText(f"{fps:.2f}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = WidgetTest()
    widget.show()
    sys.exit(app.exec())
