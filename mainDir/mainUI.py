

import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from mainDir.inputs.generator_Checkerboard import CheckerBoardGenerator
from mainDir.inputs.generator_Color import ColorGenerator
from mainDir.inputs.generator_Gradients import GradientGenerator
from mainDir.inputs.generator_Noise_Random import RandomNoiseImageGenerator
from mainDir.inputs.generator_bars_EBU import FullBarsGenerator
from mainDir.inputs.generator_bars_SMPTE import SMPTEBarsGenerator
from mainDir.inputs.imageLoader_Still import ImageLoader
from mainDir.inputs.screenCapture import ScreenCapture
from mainDir.inputs.synchObject import SynchObject
from mainDir.inputs.videoCapture import VideoCaptureSimple
from mainDir.mixBus.mixBus_014 import MixBus014, MIX_TYPE
from mainDir.ouputs.monitorWidget import MonitorWidget012
from mainDir.widgets.mixingKeyboard_012 import MixerPanelWidget_012
from mainDir.widgets.videoWidgets.matrixWidget import MatrixWidget


class VideoMixerUI(QWidget):

    transitionDictionary = {
        "mix": "Mix",
        "wipe": "Wipe_Left",
        "sting": "stinger",
        "dve": "DVE",
        "still": "Still"
    }
    transitionType = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle('openPyVision Mixer 0.1.3')

        # Inizializzazione delle variabili
        self.synchObject = SynchObject(60)
        self.mixBus = MixBus014(self.synchObject)
        self.transitionType = self.mixBus.getEffectType()
        self.mixerPanel = MixerPanelWidget_012()
        self.monitor_preview = MonitorWidget012(self.synchObject, False)
        self.monitor_program = MonitorWidget012(self.synchObject, True)
        self.matrixWidget = MatrixWidget()
        self.running_order = QTextEdit('running order')
        self.top_bottom_splitter = QSplitter(Qt.Orientation.Vertical)
        self.bottom_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.tab_widget = QTabWidget(self)
        self._matrix = {1: self.mixBus.preview_input, 2: self.mixBus.program_input, 3: None, 4: None,
                        5: None, 6: None, 7: None, 8: None}
        self.initUI()
        self.initGeometry()
        self.initConnections()

    def initUI(self):
        main_layout = QVBoxLayout()

        main_layout.addWidget(self.top_bottom_splitter)
        # Top part with two monitor widgets
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        self.top_bottom_splitter.addWidget(top_widget)
        top_layout.addWidget(self.monitor_preview)
        top_layout.addWidget(self.monitor_program)

        # Bottom part split vertically
        self.top_bottom_splitter.addWidget(self.bottom_splitter)

        # Running order and keyboard section
        left_bottom_widget = QWidget()
        left_bottom_layout = QVBoxLayout(left_bottom_widget)
        self.bottom_splitter.addWidget(left_bottom_widget)
        left_bottom_layout.addWidget(self.running_order)
        left_bottom_layout.addWidget(self.mixerPanel)

        # Right bottom section with slider, effects buttons, and QTabWidget
        right_bottom_widget = QWidget()
        right_bottom_layout = QVBoxLayout(right_bottom_widget)
        self.bottom_splitter.addWidget(right_bottom_widget)

        effects_layout = QHBoxLayout()
        right_bottom_layout.addLayout(effects_layout)

        self.tab_widget.addTab(self.matrixWidget, 'matrix')
        self.tab_widget.addTab(QWidget(), 'audio Mixer')
        self.tab_widget.addTab(QWidget(), 'system')

        right_bottom_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

    def initGeometry(self):
        self.setFixedSize(1920, 1080)
        self.top_bottom_splitter.setSizes([652, 400])
        self.bottom_splitter.setSizes([1139, 753])

    def initConnections(self):
        self.top_bottom_splitter.splitterMoved.connect(self.print_sizes)
        self.bottom_splitter.splitterMoved.connect(self.print_sizes)
        QTimer.singleShot(500, self.delayedInit)
        self.mixerPanel.tally_SIGNAL.connect(self.onMixerPanelSignal)
        self.matrixWidget.matrix_Signal.connect(self.onMatrixSignal)
        self.synchObject.synch_SIGNAL.connect(self.displayFrame)

    @property
    def matrix(self) -> dict:
        return self._matrix

    @matrix.setter
    def matrix(self, value):
        self._matrix = value

    def set_matrix_value(self, index, value):
        self._matrix[index] = value

    def delayedInit(self):
        self.monitor_preview.setAutoFit()
        self.monitor_program.setAutoFit()

    def print_sizes(self, pos, index):
        print("Top-Bottom Splitter Sizes:")
        print(f"Top Widget: {self.top_bottom_splitter.widget(0).size()}")
        print(f"Bottom Widget: {self.top_bottom_splitter.widget(1).size()}")
        print("Bottom Splitter Sizes:")
        print(f"Left Bottom Widget: {self.bottom_splitter.widget(0).size()}")
        print(f"Right Bottom Widget: {self.bottom_splitter.widget(1).size()}")
        print("-" * 50)

    def displayFrame(self):
        prw, prg = self.mixBus.getMix()
        self.monitor_program.feedInput(prg)
        self.monitor_preview.feedInput(prw)
        self._dirtyFrame = self.monitor_program.getDirtyFrame()

    def getDirtyFrame(self):
        # Assuming frame_dirty is a numpy array
        if self._dirtyFrame is not None:
            return self._dirtyFrame
        else:
            return np.zeros((1080, 1920, 3), dtype=np.uint8)

    def onMixerPanelSignal(self, data):
        """
        Gestisce il segnale proveniente dal mixer panel.
        data è un dizionario tipo:
        {"tally": "previewChange", "input": number}
        {"tally": "cut"}
        {"tally": "auto"}
        """
        print(f"Data: {data}")
        if data["tally"] == "previewChange":
            inputInt = int(data["input"])
            if self.matrix[inputInt] is not None:
                videoInput = self.matrix[inputInt]
                self.mixBus.setPreviewInput(videoInput)
            else:
                print(f"Input {inputInt} not found")
        elif data["tally"] == "cut":
            self.mixBus.cut()
        elif data["tally"] == "auto":
            self.mixBus.setEffectType(self.transitionType)
            if self.transitionType == MIX_TYPE.STINGER:
                self.mixBus.startStinger()
            else:
                self.mixBus.startMix()
        elif data["tally"] == "transitionChange":
            self.setTransitionChange(int(data["input"]))

    def setTransitionChange(self, data):
        if data == 1:  # mix
            self.transitionType = MIX_TYPE.MIX
        elif data == 2:  # dip
            pass
        elif data == 3:  # wipe
            self.transitionType = MIX_TYPE.WIPE_LEFT
        elif data == 4:  # sting
            self.transitionType = MIX_TYPE.STINGER
        elif data == 5:  # dve
            self.transitionType = MIX_TYPE.DVE
        elif data == 6:  # still
            self.transitionType = MIX_TYPE.STILL

    def onMatrixSignal(self, data):
        print(f"Matrix signal: {data}")
        inputNumber = data["input"]
        inputName = data["inputName"]
        deviceType = data["deviceType"]
        if deviceType == "videoCapture":
            deviceIndex = int(data["deviceIndex"])
            self.createVideoCapture(inputNumber, inputName, deviceIndex)
        elif deviceType == "desktopCapture":
            screenIndex = int(data["screenIndex"])
            desktopCapture = ScreenCapture(self.synchObject, screen_index=screenIndex)
            self.set_matrix_value(inputNumber, desktopCapture)
        elif deviceType == "stillImage":
            path = data["path"]
            stillImage = ImageLoader(self.synchObject, path)
            self.set_matrix_value(inputNumber, stillImage)
        elif deviceType == "videoPlayer":
            pass
        elif deviceType == "colorGenerator":
            colorGenerator = ColorGenerator(self.synchObject)
            color = self.returnQColorFromDictionary(data["color"])
            colorGenerator.setColor(color)
            self.set_matrix_value(inputNumber, colorGenerator)
        elif deviceType == "noiseGenerator":
            noiseGenerator = RandomNoiseImageGenerator(self.synchObject)
            self.set_matrix_value(inputNumber, noiseGenerator)
        elif deviceType == "gradientGenerator":
            gradientType = data["gradientType"].lower()
            color1 = self.returnQColorFromDictionary(data["color1"]['color'])
            color2 = self.returnQColorFromDictionary(data["color2"]['color'])
            gradientGenerator = GradientGenerator(self.synchObject, gradient_type=gradientType, start_color=color1,
                                                  end_color=color2)
            self.set_matrix_value(inputNumber, gradientGenerator)
        elif deviceType == "smpteBarsGenerator":
            if data['smpte'] == 0:
                smpteBars = FullBarsGenerator(self.synchObject)
            else:
                smpteBars = SMPTEBarsGenerator(self.synchObject)
            self.set_matrix_value(inputNumber, smpteBars)
        elif deviceType == "checkerBoardGenerator":
            checkerBoard = CheckerBoardGenerator(self.synchObject)
            self.set_matrix_value(inputNumber, checkerBoard)
        else:
            print("NON VIDEO CAPTURE")

    @staticmethod
    def returnQColorFromDictionary(data):
        r = data["r"]
        g = data["g"]
        b = data["b"]
        color = QColor(int(r), int(g), int(b))
        return color

    def createVideoCapture(self, inputNumber, inputName, deviceIndex):
        videoCapture = VideoCaptureSimple(self.synchObject, input_index=deviceIndex)
        self.set_matrix_value(inputNumber, videoCapture)

    def updateInput(self, inputNumber, inputName, data):
        self.set_matrix_value(inputNumber, data)

