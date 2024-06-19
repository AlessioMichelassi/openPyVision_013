from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.widgets.generics.colorLabel import ColorLabel


class GradientGeneratorWidget(QWidget):
    deviceChanged = pyqtSignal(dict, name="gradientGeneratorChanged")
    gradientGeneratorDictionary = {"gradientType": "Radial", "color1": {"color": {"r": 255, "g": 255, "b": 255}},
                                   "color2": {"color": {"r": 0, "g": 0, "b": 0}}}  # Default values

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        label = QLabel("GradientType", self)
        layout.addWidget(label)
        self.cmbGradientType = QComboBox(self)
        self.GradientTypeList = ["Radial", "Horizontal", "Vertical", "Diagonal"]
        self.cmbGradientType.addItems(self.GradientTypeList)
        self.cmbGradientType.currentIndexChanged.connect(self.onGradientTypeChanged)
        layout.addWidget(self.cmbGradientType)
        label = ColorLabel(QColor(255, 255, 255), self)
        label.deviceChanged.connect(self.onColor1Changed)
        layout.addWidget(label)
        label = ColorLabel(QColor(0, 0, 0), self)
        label.deviceChanged.connect(self.onColor2Changed)
        layout.addWidget(label)
        self.setLayout(layout)

    def getGradientDictionary(self):
        return self.gradientGeneratorDictionary

    def onColor1Changed(self, colorDictionary):
        self.gradientGeneratorDictionary["color1"] = colorDictionary

    def onColor2Changed(self, colorDictionary):
        self.gradientGeneratorDictionary["color2"] = colorDictionary

    def onGradientTypeChanged(self, index):
        self.gradientGeneratorDictionary["gradientType"] = self.GradientTypeList[index]

    def getDictionary(self):
        return self.gradientGeneratorDictionary


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    gradientGenerator = GradientGeneratorWidget()
    gradientGenerator.deviceChanged.connect(print)
    gradientGenerator.show()
    sys.exit(app.exec())
