from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from mainDir.widgets.generics.comboDevice import ComboDevice


class VideoCaptureWidget(QWidget):
    deviceChanged = pyqtSignal(dict, name="videoCaptureChanged")
    deviceDictionary = {'deviceIndex': 0, 'deviceName': 'None'}
    currentIndex = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        label = QLabel("VideoCapture", self)
        self.cmbVideoCapture = ComboDevice(self)
        layout.addWidget(label)
        layout.addWidget(self.cmbVideoCapture)
        self.setLayout(layout)
        self.cmbVideoCapture.deviceChanged.connect(self.onDeviceChanged)

    def onDeviceChanged(self, dictio):
        self.deviceDictionary = dictio
        self.deviceChanged.emit(dictio)

    def getDictionary(self):
        return self.deviceDictionary

    def setIndex(self):
        self.cmbVideoCapture.setSelectedDevice(0)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    videoCaptureWidget = VideoCaptureWidget()
    videoCaptureWidget.deviceChanged.connect(print)
    videoCaptureWidget.show()
    sys.exit(app.exec())