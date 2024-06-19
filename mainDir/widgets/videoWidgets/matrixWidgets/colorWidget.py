from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.widgets.generics.colorLabel import ColorLabel


class ColorWidget(QWidget):
    deviceChanged = pyqtSignal(dict, name="colorChanged")
    colorDictionary = {'color': {'r': 255, 'g': 0, 'b': 0}}

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.r = QLineEdit("255", self)
        self.g = QLineEdit("0", self)
        self.b = QLineEdit("0", self)
        for line_edit in (self.r, self.g, self.b):
            line_edit.setValidator(QIntValidator(0, 255, self))
            layout.addWidget(line_edit)
        self.color_preview = ColorLabel(QColor(255, 0, 0), self)
        self.color_preview.deviceChanged.connect(self.changeColor)
        layout.addWidget(self.color_preview)
        self.setLayout(layout)
        self.update_preview()
        self.r.returnPressed.connect(self.update_preview)
        self.g.returnPressed.connect(self.update_preview)
        self.b.returnPressed.connect(self.update_preview)

    def update_preview(self):
        r = int(self.r.text())
        g = int(self.g.text())
        b = int(self.b.text())
        self.color_preview.setStyleSheet(f"background-color: rgb({r}, {g}, {b})")
        self.colorDictionary = {"color": {"r": r, "g": g, "b": b}}
        self.deviceChanged.emit(self.colorDictionary)

    def changeColor(self, colorDictionary):
        self.colorDictionary = colorDictionary
        self.r.setText(str(colorDictionary["color"]["r"]))
        self.g.setText(str(colorDictionary["color"]["g"]))
        self.b.setText(str(colorDictionary["color"]["b"]))
        self.update_preview()

    def getDictionary(self):
        r = int(self.r.text())
        g = int(self.g.text())
        b = int(self.b.text())
        return {"color": {"r": r, "g": g, "b": b}}


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    colorWidget = ColorWidget()
    colorWidget.deviceChanged.connect(print)
    colorWidget.show()
    sys.exit(app.exec())