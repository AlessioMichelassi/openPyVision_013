from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class NoiseGeneratorWidget(QWidget):
    deviceChanged = pyqtSignal(dict, name="NoiseGeneratorChanged")
    NoiseGeneratorDictionary = {}

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        label = QLabel("NoiseType", self)
        layout.addWidget(label)
        self.cmbNoiseType = QComboBox(self)
        self.NoiseTypeList = ["Random", "GaussianNoise", "SaltAndPepperNoise"]
        self.cmbNoiseType.addItems(self.NoiseTypeList)
        layout.addWidget(self.cmbNoiseType)
        label = QLabel("NoiseIntensity", self)
        layout.addWidget(label)
        self.NoiseIntensity = QLineEdit("0.1", self)
        self.NoiseIntensity.setValidator(QDoubleValidator(0, 1, 2, self))
        layout.addWidget(self.NoiseIntensity)
        self.setLayout(layout)

        self.cmbNoiseType.currentIndexChanged.connect(self.onNoiseTypeChanged)
        self.NoiseIntensity.textChanged.connect(self.onNoiseIntensityChanged)

    def onNoiseTypeChanged(self):
        noiseType = self.cmbNoiseType.currentText()
        self.NoiseGeneratorDictionary = {"noiseType": noiseType, "noiseIntensity": self.NoiseIntensity.text()}
        self.deviceChanged.emit(self.NoiseGeneratorDictionary)

    def onNoiseIntensityChanged(self):
        noiseType = self.cmbNoiseType.currentText()
        self.NoiseGeneratorDictionary = {"noiseType": noiseType, "noiseIntensity": self.NoiseIntensity.text()}
        self.deviceChanged.emit(self.NoiseGeneratorDictionary)

    def getDictionary(self):
        return self.NoiseGeneratorDictionary


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    noiseGenerator = NoiseGeneratorWidget()
    noiseGenerator.deviceChanged.connect(print)
    noiseGenerator.show()
    sys.exit(app.exec())
