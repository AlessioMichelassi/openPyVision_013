from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class SmpteWidget(QWidget):
    deviceChanged = pyqtSignal(int, name="smpteWidgetChanged")
    smpteDictionary = {}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cmbSmpte = QComboBox(self)
        self.smpteList = ["EBU bars", "Smpte Bars"]
        self.cmbSmpte.addItems(self.smpteList)
        self.initUI()
        self.initConnections()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self.cmbSmpte)
        self.setLayout(layout)

    def initConnections(self):
        self.cmbSmpte.currentIndexChanged.connect(self.onSmpteChanged)

    def onSmpteChanged(self, index):
        self.smpteDictionary = {"smpte": index}
        self.deviceChanged.emit(index)

    def getDictionary(self):
        return self.smpteDictionary
