from PyQt6.QtCore import *
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import *

from mainDir.widgets.generics.lblWidget import LblWidget
from mainDir.widgets.videoWidgets.matrixWidgets.NoiseGenerator import NoiseGeneratorWidget
from mainDir.widgets.videoWidgets.matrixWidgets.VideoCaptureWidget import VideoCaptureWidget
from mainDir.widgets.videoWidgets.matrixWidgets.checkerboardWidget import CheckerboardWidget
from mainDir.widgets.videoWidgets.matrixWidgets.colorWidget import ColorWidget
from mainDir.widgets.videoWidgets.matrixWidgets.gradientGenerator import GradientGeneratorWidget
from mainDir.widgets.videoWidgets.matrixWidgets.playlistWidget import PlaylistControlWidget
from mainDir.widgets.videoWidgets.matrixWidgets.screenCaptureWidget import ScreenCaptureWidget
from mainDir.widgets.videoWidgets.matrixWidgets.smpteWidget import SmpteWidget
from mainDir.widgets.videoWidgets.matrixWidgets.stillLoader import StillLoaderWidget


class MatrixWidget(QWidget):
    """
    MatrixWidget class to manage multiple input sources for video and image processing.
    Provides UI components to select, configure, and activate different types of inputs.
    """
    matrix_Signal = pyqtSignal(dict, name="matrix_SIGNAL")

    def __init__(self, parent=None):
        """
        Initialize the MatrixWidget.

        :param parent: The parent widget.
        """
        super().__init__(parent)
        self.current_index = 0
        self.setLayout(QVBoxLayout())

        self.generator_list = ["Select input", "videoCapture", "desktopCapture", "stillImage", "videoPlayer",
                               "colorGenerator", "noiseGenerator", "gradientGenerator", "smpteBarsGenerator",
                               "checkerBoardGenerator"]
        main_layout = QGridLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        main_layout.setSpacing(5)  # Reduce spacing between widgets

        self.combo_boxes = []
        self.stacked_widgets = []
        self.active_checkboxes = []

        for i in range(1, 9):  # 8 inputs
            label = QLabel(f"Input_{i}")
            label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            label.setFixedSize(100, 30)

            combo = QComboBox(self)
            combo.setFixedSize(150, 30)
            combo.addItems(self.generator_list)
            combo.currentIndexChanged.connect(self.inputComboBoxChanged)

            stacked_widget = QStackedWidget()
            stacked_widget.addWidget(QLabel("Select an option"))  # Default placeholder
            stacked_widget.addWidget(VideoCaptureWidget())  # Index 1 videoCapture
            stacked_widget.addWidget(ScreenCaptureWidget())  # Index 2 desktopCapture
            stacked_widget.addWidget(StillLoaderWidget())  # Index 3 stillImage
            stacked_widget.addWidget(PlaylistControlWidget())  # Index 4 videoPlayer
            stacked_widget.addWidget(ColorWidget())  # Index 5 colorGenerator
            stacked_widget.addWidget(NoiseGeneratorWidget())  # Index 6 NoiseGenerator
            stacked_widget.addWidget(GradientGeneratorWidget())  # Index 7 gradientGenerator
            stacked_widget.addWidget(SmpteWidget())  # Index 8 smpteBarsGenerator
            stacked_widget.addWidget(CheckerboardWidget())  # Index 9 checkerBoardGenerator
            stacked_widget.setFixedSize(300, 40)

            btnInputAssign = QCheckBox("Active")
            btnInputAssign.setFixedSize(70, 40)

            main_layout.addWidget(label, i, 0, Qt.AlignmentFlag.AlignLeft)
            main_layout.addWidget(combo, i, 1, Qt.AlignmentFlag.AlignLeft)
            main_layout.addWidget(stacked_widget, i, 2, Qt.AlignmentFlag.AlignLeft)
            main_layout.addWidget(btnInputAssign, i, 3, Qt.AlignmentFlag.AlignLeft)

            self.combo_boxes.append(combo)
            self.stacked_widgets.append(stacked_widget)
            self.active_checkboxes.append(btnInputAssign)

            # Connect the checkbox to a toggle function
            btnInputAssign.toggled.connect(lambda state, c=combo, s=stacked_widget: self.toggleCapture(state, c, s))

        self.layout().addLayout(main_layout)

    def inputComboBoxChanged(self, index):
        """
        Handle changes in the input combo box selection.

        :param index: The index of the selected item in the combo box.
        """
        if index == 0:
            return  # "Select input" selected, do nothing
        sender = self.sender()
        stack_index = self.combo_boxes.index(sender)
        stacked_widget = self.stacked_widgets[stack_index]
        stacked_widget.setCurrentIndex(index)  # Set to the corresponding widget
        self.current_index = index

    def toggleCapture(self, state, comboBox, stacked_widget):
        """
        Handle toggling of the active checkbox to enable or disable the input.

        :param state: The state of the checkbox (True for checked, False for unchecked).
        :param comboBox: The combo box associated with the input.
        :param stacked_widget: The stacked widget containing the input configuration widgets.
        """
        index = comboBox.currentIndex()
        deviceName = comboBox.itemText(index)
        lblWidget = self.findChild(QLabel, f"lbl_{self.combo_boxes.index(comboBox) + 1}")
        lblName = lblWidget.text() if lblWidget else "Unknown"

        current_widget = stacked_widget.currentWidget()
        widget_params = current_widget.getDictionary() if hasattr(current_widget, 'getDictionary') else {}

        input_index = self.combo_boxes.index(comboBox) + 1  # Correct the input index
        if state:
            self.matrix_Signal.emit({
                "input": input_index,
                "inputName": lblName,
                "deviceType": deviceName,
                "deviceName": index,
                **widget_params
            })
        else:
            self.matrix_Signal.emit({
                "input": input_index,
                "inputName": lblName,
                "deviceType": None,
                "deviceName": None,
                **widget_params
            })


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MatrixWidget()
    window.matrix_Signal.connect(print)
    window.show()
    sys.exit(app.exec())
