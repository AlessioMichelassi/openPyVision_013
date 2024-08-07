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
from mainDir.inputs.videoCapture013 import VideoCapture013
from mainDir.mixBus.mixBus_014 import MixBus014, MIX_TYPE
from mainDir.ouputs.monitorWidget import MonitorWidget012
from mainDir.widgets.mixingKeyboard_012 import MixerPanelWidget_012
from mainDir.widgets.videoWidgets.matrixWidget import MatrixWidget


class VideoMixerUI(QWidget):
    """
    The VideoMixerUI class provides a user interface for managing video inputs,
    transitions, and effects. It includes monitors for preview and program outputs,
    a mixer panel, and a matrix for selecting input sources.
    """

    transitionDictionary = {
        "mix": "Mix",
        "wipe": "Wipe_Left",
        "sting": "stinger",
        "dve": "DVE",
        "still": "Still"
    }
    transitionType = None

    def __init__(self):
        """
        Initialize the VideoMixerUI.
        """
        super().__init__()
        self.setWindowTitle('openPyVision Mixer 0.1.3')

        # Initialize variables
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
        """
        Set up the user interface layout and widgets.
        """
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
        """
        Set up the initial geometry and sizes for the splitters and the main window.
        """
        self.setFixedSize(1920, 1080)
        self.top_bottom_splitter.setSizes([652, 400])
        self.bottom_splitter.setSizes([1139, 753])

    def initConnections(self):
        """
        Initialize signal-slot connections.
        """
        self.top_bottom_splitter.splitterMoved.connect(self.print_sizes)
        self.bottom_splitter.splitterMoved.connect(self.print_sizes)
        QTimer.singleShot(500, self.delayedInit)
        self.mixerPanel.tally_SIGNAL.connect(self.onMixerPanelSignal)
        self.matrixWidget.matrix_Signal.connect(self.onMatrixSignal)
        self.synchObject.synch_SIGNAL.connect(self.displayFrame)

    @property
    def matrix(self) -> dict:
        """
        Get the current matrix dictionary.
        :return: The current matrix dictionary.
        """
        return self._matrix

    @matrix.setter
    def matrix(self, value):
        """
        Set the matrix dictionary.
        :param value: The new matrix dictionary.
        """
        self._matrix = value

    def set_matrix_value(self, index, value):
        """
        Set a specific value in the matrix dictionary.
        :param index: The index to set.
        :param value: The value to set at the specified index.
        """
        self._matrix[index] = value

    def delayedInit(self):
        """
        Perform delayed initialization tasks.
        """
        self.monitor_preview.setAutoFit()
        self.monitor_program.setAutoFit()

    def print_sizes(self, pos, index):
        """
        Print the sizes of the widgets in the splitters.
        :param pos: The position of the splitter.
        :param index: The index of the splitter.
        """
        print("Top-Bottom Splitter Sizes:")
        print(f"Top Widget: {self.top_bottom_splitter.widget(0).size()}")
        print(f"Bottom Widget: {self.top_bottom_splitter.widget(1).size()}")
        print("Bottom Splitter Sizes:")
        print(f"Left Bottom Widget: {self.bottom_splitter.widget(0).size()}")
        print(f"Right Bottom Widget: {self.bottom_splitter.widget(1).size()}")
        print("-" * 50)

    def displayFrame(self):
        """
        Display the current frame on the preview and program monitors.
        """
        prw, prg = self.mixBus.getMix()
        self.monitor_program.feedInput(prg)
        self.monitor_preview.feedInput(prw)
        self._dirtyFrame = self.monitor_program.getDirtyFrame()

    def getDirtyFrame(self):
        """
        Get the dirty frame from the monitor program.
        :return: The dirty frame as a numpy array.
        """
        if self._dirtyFrame is not None:
            return self._dirtyFrame
        else:
            return np.zeros((1080, 1920, 3), dtype=np.uint8)

    def onMixerPanelSignal(self, data):
        """
        Handle the signal from the mixer panel.
        :param data: The data from the mixer panel.
        """
        print(f"Data: {data}")
        if data["tally"] == "previewChange":
            inputInt = int(data["input"])
            if self.matrix[inputInt] is not None:
                videoInput = self.matrix[inputInt]
                self.mixBus.setPreviewInput(videoInput)
            else:
                print(f"Input {inputInt} not found")
        elif data["tally"] == "programChange":
            inputInt = int(data["input"])
            if self.matrix[inputInt] is not None:
                videoInput = self.matrix[inputInt]
                self.mixBus.setProgramInput(videoInput)
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
        """
        Set the transition type based on the input data.
        :param data: The input data to determine the transition type.
        """
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
        """
        Handle the matrix signal by creating and setting the appropriate input based on the device type.
        :param data: Dictionary containing the input data.
        """
        print(f"Matrix signal: {data}")
        inputNumber = data["input"]
        inputName = data["inputName"]
        deviceType = data["deviceType"]
        if deviceType is None:
            self.unplugFromMatrix(inputNumber)
        if deviceType == "videoCapture":
            self.handleVideoCapture(inputNumber, inputName, data)
        elif deviceType == "desktopCapture":
            self.handleDesktopCapture(inputNumber, data)
        elif deviceType == "stillImage":
            self.handleStillImage(inputNumber, data)
        elif deviceType == "videoPlayer":
            self.handleVideoPlayer(inputNumber, data)
        elif deviceType == "colorGenerator":
            self.handleColorGenerator(inputNumber, data)
        elif deviceType == "noiseGenerator":
            self.handleNoiseGenerator(inputNumber)
        elif deviceType == "gradientGenerator":
            self.handleGradientGenerator(inputNumber, data)
        elif deviceType == "smpteBarsGenerator":
            self.handleSmpteBarsGenerator(inputNumber, data)
        elif deviceType == "checkerBoardGenerator":
            self.handleCheckerBoardGenerator(inputNumber)
        else:
            print("Unknown device type")

        # Check if the input is in preview or program and update monitors
        self.updatePreviewProgram(inputNumber)

    def handleVideoCapture(self, inputNumber, inputName, data):
        """
        Create and set a video capture in the matrix.
        :param inputNumber: The input index.
        :param inputName: The input name.
        :param data: The input data.
        """
        deviceIndex = int(data["deviceIndex"])
        self.createVideoCapture(inputNumber, inputName, deviceIndex)

    def handleDesktopCapture(self, inputNumber, data):
        """
        Create and set a desktop capture in the matrix.
        :param inputNumber: The input index.
        :param data: The input data.
        """
        screenIndex = int(data["screenIndex"])
        desktopCapture = ScreenCapture(self.synchObject, screen_index=screenIndex)
        self.set_matrix_value(inputNumber, desktopCapture)

    def handleStillImage(self, inputNumber, data):
        """
        Create and set a still image in the matrix.
        :param inputNumber: The input index.
        :param data: The input data.
        """
        path = data["path"]
        stillImage = ImageLoader(self.synchObject, path)
        self.set_matrix_value(inputNumber, stillImage)

    def handleVideoPlayer(self, inputNumber, data):
        """
        Handle the video player input.
        :param inputNumber: The input index.
        :param data: The input data.
        """
        # Implementation for handling video player
        pass

    def handleColorGenerator(self, inputNumber, data):
        """
        Create and set a color generator in the matrix.
        :param inputNumber: The input index.
        :param data: The input data.
        """
        colorGenerator = ColorGenerator(self.synchObject)
        color = self.returnQColorFromDictionary(data["color"])
        colorGenerator.setColor(color)
        self.set_matrix_value(inputNumber, colorGenerator)

    def handleNoiseGenerator(self, inputNumber):
        """
        Create and set a noise generator in the matrix.
        :param inputNumber: The input index.
        """
        noiseGenerator = RandomNoiseImageGenerator(self.synchObject)
        self.set_matrix_value(inputNumber, noiseGenerator)

    def handleGradientGenerator(self, inputNumber, data):
        """
        Create and set a gradient generator in the matrix.
        :param inputNumber: The input index.
        :param data: The input data.
        """
        gradientType = data["gradientType"].lower()
        color1 = self.returnQColorFromDictionary(data["color1"]['color'])
        color2 = self.returnQColorFromDictionary(data["color2"]['color'])
        gradientGenerator = GradientGenerator(self.synchObject, gradient_type=gradientType, start_color=color1,
                                              end_color=color2)
        self.set_matrix_value(inputNumber, gradientGenerator)

    def handleSmpteBarsGenerator(self, inputNumber, data):
        """
        Create and set an SMPTE bars or FullBars generator in the matrix.
        :param inputNumber: The input index.
        :param data: The input data.
        """
        print(f"Data: {data}")
        if data['deviceType'] == 0:
            smpteBars = FullBarsGenerator(self.synchObject)
        else:
            smpteBars = SMPTEBarsGenerator(self.synchObject)
        self.set_matrix_value(inputNumber, smpteBars)

    def handleCheckerBoardGenerator(self, inputNumber):
        """
        Create and set a checkerboard generator in the matrix.
        :param inputNumber: The input index.
        """
        checkerBoard = CheckerBoardGenerator(self.synchObject)
        self.set_matrix_value(inputNumber, checkerBoard)

    def updatePreviewProgram(self, inputNumber):
        """
        Update what is in program and preview based on the matrix input change signal.
        Checks that the input is enabled in the mixer panel to prevent black screens.
        :param inputNumber: The number of the input to check.
        """
        if self.mixerPanel.btnDictionary["preview"] == inputNumber:
            dictio = {"tally": "previewChange", "input": inputNumber}
            self.mixerPanel.tally_SIGNAL.emit(dictio)
        if self.mixerPanel.btnDictionary["program"] == inputNumber:
            dictio = {"tally": "programChange", "input": inputNumber}
            self.mixerPanel.tally_SIGNAL.emit(dictio)
        if inputNumber not in self.mixerPanel._btnEnabled:
            self.mixerPanel.enableButton(inputNumber)

    def unplugFromMatrix(self, inputNumber):
        """
        Remove the input from the matrix.
        :param inputNumber: The input index to remove.
        """
        blackImage = ColorGenerator(self.synchObject)
        blackImage.setColor(QColor(0, 0, 0))
        self.set_matrix_value(inputNumber, blackImage)
        self.updatePreviewProgram(inputNumber)
        self.matrix[inputNumber] = None
        self.mixerPanel.disableButton(inputNumber)
        print(f"debug {inputNumber} {self.matrix}")
        print(f"debug {self.mixerPanel._btnEnabled}")

    @staticmethod
    def returnQColorFromDictionary(data):
        """
        Convert a dictionary with color information to a QColor object.
        :param data: The dictionary containing the color data.
        :return: The QColor object.
        """
        r = data["r"]
        g = data["g"]
        b = data["b"]
        color = QColor(int(r), int(g), int(b))
        return color

    def createVideoCapture(self, inputNumber, inputName, deviceIndex):
        """
        Create a video capture and set it in the matrix.
        :param inputNumber: The input index.
        :param inputName: The input name.
        :param deviceIndex: The device index for the video capture.
        """
        videoCapture = VideoCapture013(self.synchObject, deviceIndex)
        self.set_matrix_value(inputNumber, videoCapture)
        print(f"debug: {inputNumber} {inputName} {deviceIndex} {self.matrix}")

    def updateInput(self, inputNumber, inputName, data):
        """
        Update the input in the matrix.
        :param inputNumber: The input index.
        :param inputName: The input name.
        :param data: The input data.
        """
        self.set_matrix_value(inputNumber, data)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = VideoMixerUI()
    window.show()
    app.exec()
