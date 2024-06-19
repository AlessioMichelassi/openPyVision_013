from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class ScreenCaptureWidget(QWidget):
    deviceChanged = pyqtSignal(dict, name="ScreenCaptureChanged")
    screenCaptureDictionary = {'screenIndex': 0, 'screenName': '\\\\.\\DISPLAY1'}

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)

        label = QLabel("Select Screen", self)
        layout.addWidget(label)

        self.cmbScreen = QComboBox(self)
        self.screenList = self.getAvailableScreens()
        self.cmbScreen.addItems(self.screenList)
        self.cmbScreen.currentIndexChanged.connect(self.onScreenChanged)
        layout.addWidget(self.cmbScreen)

        self.setLayout(layout)

    def getAvailableScreens(self):
        screens = QGuiApplication.screens()
        screen_names = [screen.name() for screen in screens]
        return screen_names

    def onScreenChanged(self, index):
        screen_name = self.cmbScreen.itemText(index)
        self.screenCaptureDictionary = {"screenIndex": index, "screenName": screen_name}
        self.deviceChanged.emit(self.screenCaptureDictionary)

    def getDictionary(self):
        return self.screenCaptureDictionary


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    screenCaptureWidget = ScreenCaptureWidget()
    screenCaptureWidget.deviceChanged.connect(print)
    screenCaptureWidget.show()
    sys.exit(app.exec())
