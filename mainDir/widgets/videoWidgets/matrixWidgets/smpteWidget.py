from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class SmpteWidget(QWidget):
    """
    Questo widget viene usato nella matrice per selezionare il tipo di smpte da visualizzare.
    Attualmente ce n'è di due tipi: EBU bars e Smpte Bars.
    """
    deviceChanged = pyqtSignal(int, name="smpteWidgetChanged")
    smpteDictionary = {"smpteIndex": "0", "smpteName": "EBU bars"}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cmbSmpte = QComboBox(self)
        self.smpteList = ["option", "EBU bars", "Smpte Bars"]
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
        if index == 0:  # Segnaposto selezionato
            self.smpteDictionary = {"smpteIndex": "", "smpteName": ""}
        else:
            self.smpteDictionary = {"smpteIndex": index - 1, "smpteName": self.cmbSmpte.itemText(index)}
        self.deviceChanged.emit(index)

    def getDictionary(self):
        return self.smpteDictionary


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    screenCaptureWidget = SmpteWidget()
    screenCaptureWidget.deviceChanged.connect(print)
    screenCaptureWidget.show()
    sys.exit(app.exec())
