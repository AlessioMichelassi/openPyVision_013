from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

"""
Questo widget è un helper per la classe matrix che permette di impostare i parametri del checkerboard.
si puà impostare il colore della scacchiera di default bianca e grigia, e la dimensione del singolo scacco.
"""


class CheckerboardWidget(QWidget):
    deviceChanged = pyqtSignal(dict, name="checkerboardChanged")
    checkerboardDictionary = {'darkColor': '127', 'lightColor': '0', 'CheckerSize': '40'}

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.darkColor = QLineEdit("127", self)
        self.lightColor = QLineEdit("0", self)
        self.CheckerSize = QLineEdit("40", self)
        for line_edit in (self.darkColor, self.lightColor, self.CheckerSize):
            line_edit.setValidator(QIntValidator(0, 255, self))
            layout.addWidget(line_edit)

        label = QLabel("DarkColor", self)
        layout.addWidget(label)
        layout.addWidget(self.darkColor)
        label = QLabel("LightColor", self)
        layout.addWidget(label)
        layout.addWidget(self.lightColor)
        label = QLabel("CheckerSize", self)
        layout.addWidget(label)
        layout.addWidget(self.CheckerSize)
        self.setLayout(layout)

        self.darkColor.returnPressed.connect(self.onCheckerboardChanged)
        self.lightColor.returnPressed.connect(self.onCheckerboardChanged)
        self.CheckerSize.returnPressed.connect(self.onCheckerboardChanged)

    def onCheckerboardChanged(self):
        darkColor = self.darkColor.text()
        lightColor = self.lightColor.text()
        CheckerSize = self.CheckerSize.text()
        self.checkerboardDictionary = {"darkColor": darkColor, "lightColor": lightColor, "CheckerSize": CheckerSize}
        self.deviceChanged.emit(self.checkerboardDictionary)

    def getCurrentWidgetParams(self):
        self.checkerboardDictionary['darkColor'] = self.darkColor.text()
        self.checkerboardDictionary['lightColor'] = self.lightColor.text()
        self.checkerboardDictionary['CheckerSize'] = self.CheckerSize.text()
        return self.checkerboardDictionary


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    checkerboard = CheckerboardWidget()
    checkerboard.deviceChanged.connect(print)
    checkerboard.show()
    sys.exit(app.exec())
