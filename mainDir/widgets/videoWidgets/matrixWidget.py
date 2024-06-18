from PyQt6.QtCore import *
from PyQt6.QtWidgets import *




class MatrixWidget(QWidget):
    matrixSignal = pyqtSignal(dict, name="matrixSignal")
    width = 200
    height = 40
    scaleFactor = 0.5

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_index = 0
        self.setLayout(QVBoxLayout())

        self.generator_list = ["Select input", "videoCapture", "desktopCapture", "stillImage", "videoPlayer",
                               "colorGenerator", "noiseGenerator", "gradientGenerator", "smpteBarsGenerator",
                               "checkerBoardGenerator"]
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)  # Ridurre i margini
        main_layout.setSpacing(0)  # Ridurre la spaziatura tra i widget
        self.combo_boxes = []
        self.stacked_widgets = []

        for i in range(1, 9):  # 8 inputs
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)  # Ridurre i margini
            layout.setSpacing(0)  # Ridurre la spaziatura tra i widget

            label = LblWidget("Input", i, QSize(
                int(self.width * self.scaleFactor),
                int(self.height * self.scaleFactor)))
            label.setObjectName(f"lbl_{i}")
            combo = self.createBaseComboDevice()
            combo.setObjectName(f"input_{i}")
            stacked_widget = self.createStackedWidget(label)
            btnInputAssign = QCheckBox("Active")
            btnInputAssign.setFixedSize(int(self.width // 2 * self.scaleFactor),
                                        int(self.height * self.scaleFactor))

            layout.addWidget(label)
            layout.addWidget(combo)
            layout.addWidget(btnInputAssign)
            layout.addWidget(stacked_widget)

            main_layout.addLayout(layout)
            self.combo_boxes.append(combo)
            self.stacked_widgets.append(stacked_widget)

            # Connect the checkbox to a toggle function
            btnInputAssign.toggled.connect(lambda state, c=combo, s=stacked_widget: self.toggleCapture(state, c, s))

        self.layout().addLayout(main_layout)

    def createBaseComboDevice(self):
        baseComboDevice = QComboBox(self)
        baseComboDevice.setFixedSize(int(self.width * self.scaleFactor),
                                     int(self.height * self.scaleFactor))
        baseComboDevice.addItems(self.generator_list)
        baseComboDevice.currentIndexChanged.connect(self.inputComboBoxChanged)
        return baseComboDevice

    def createStackedWidget(self, label):
        # Placeholder for dynamic widgets
        stacked_widget = QStackedWidget()
        stacked_widget.addWidget(QLabel("Select an option"))  # Default placeholder
        stacked_widget.addWidget(VideoCaptureWidget())  # Index 1 videoCapture
        stacked_widget.addWidget(ScreenCaptureWidget())  # Index 2 desktopCapture
        stacked_widget.addWidget(StillLoaderWidget())  # Index 3 stillImage
        stacked_widget.addWidget(ColorWidget())  # Index 4 videoPlayer
        stacked_widget.addWidget(ColorWidget())  # Index 5 colorGenerator
        stacked_widget.addWidget(NoiseGeneratorWidget())  # Index 6 NoiseGenerator
        stacked_widget.addWidget(GradientGeneratorWidget())  # Index 7 gradientGenerator
        stacked_widget.addWidget(SmpteWidget())  # Index 8 smpteBarsGenerator
        stacked_widget.addWidget(CheckerboardWidget())  # Index 9 checkerBoardGenerator
        return stacked_widget

    def inputComboBoxChanged(self, index):
        if index == 0:
            return  # "Select input" selected, do nothing
        sender = self.sender()
        stack_index = self.combo_boxes.index(sender)
        stacked_widget = self.stacked_widgets[stack_index]
        stacked_widget.setCurrentIndex(index)  # Set to the corresponding widget
        self.current_index = index

    def toggleCapture(self, state, comboBox, stacked_widget):
        index = comboBox.currentIndex()
        deviceName = comboBox.itemText(index)
        lblWidget = self.findChild(LblWidget, f"lbl_{self.combo_boxes.index(comboBox) + 1}")
        lblName = lblWidget.name if lblWidget else "Unknown"

        current_widget = stacked_widget.currentWidget()
        widget_params = current_widget.getDictionary() if hasattr(current_widget, 'getDictionary') else {}

        input_index = self.combo_boxes.index(comboBox) + 1  # Correct the input index
        if state:
            self.matrixSignal.emit({
                "input": input_index,
                "inputName": lblName,
                "deviceType": deviceName,
                "deviceName": index,
                **widget_params
            })
        else:
            self.matrixSignal.emit({
                "input": input_index,
                "inputName": lblName,
                "deviceType": None,
                "deviceName": None,
                **widget_params
            })

    def onDeviceChanged(self, dictio):
        print(dictio)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MatrixWidget()
    window.matrixSignal.connect(print)
    window.show()
    sys.exit(app.exec())
