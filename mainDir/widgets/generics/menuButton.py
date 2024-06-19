from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor


class CustomButton(QPushButton):
    def __init__(self, text, mainColor=QColor(255, 128, 10), parent=None):
        super(CustomButton, self).__init__(text, parent)
        self.mainColor = QColor(mainColor)
        self.normalColor = QColor("lightgrey")
        self._setColors()
        self.setStyleSheet(self._returnStyleSheet())

    def setSize(self, width, height):
        self.setFixedSize(width, height)

    def _setColors(self):
        self.borderPressed = self.mainColor.darker(150).name()
        self.borderUnPressed = self.normalColor.darker(150).name()
        self.colorPressed = self._getContrastingColor(self.mainColor).name()
        self.colorUnPressed = self._getContrastingColor(self.normalColor).name()

    def _returnStyleSheet(self):
        """
        Quando il pulsante non lampeggia viene assegnato un colore di default
        al pulsante premuto/non premuto
        :return:
        """
        style = f"""
        QPushButton:pressed  {{
            background-color: {self.mainColor.name()};
            border: 2px solid {self.borderPressed};
            border-radius: 5px;
            color: {self.colorPressed};
        }}
        QPushButton:!pressed {{
            background-color: {self.normalColor.name()};
            border: 2px solid {self.borderUnPressed};
            border-radius: 5px;
            color: {self.colorUnPressed};
        }}
        """
        return style

    @staticmethod
    def _getContrastingColor(color):
        yiq = ((color.red() * 299) + (color.green() * 587) + (color.blue() * 114)) / 1000
        return QColor("black") if yiq >= 128 else QColor("white")

    @staticmethod
    def _getStyleSheet(bgColor, borderColor, textColor):
        return f"""
        QPushButton {{
            background-color: {bgColor.name()};
            border: 2px solid {borderColor};
            border-radius: 5px;
            color: {textColor};
        }}
        """


class ContextMenuButton(CustomButton):
    def __init__(self, text, options, mainColor=QColor(255, 128, 10), parent=None):
        super(ContextMenuButton, self).__init__(text, mainColor, parent)
        self.options = options
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openContextMenu)

    def openContextMenu(self, position):
        menu = QMenu()
        for option in self.options:
            action = menu.addAction(option)
            action.triggered.connect(lambda _, opt=option: self.setObjectName(opt))
        menu.exec_(self.mapToGlobal(position))


# TEST CLASS
class TestContextMenuButton(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Context Menu Button Test")
        self.setGeometry(100, 100, 400, 200)
        self.setLayout(QVBoxLayout())
        options = ["WipeLeft", "WipeRight", "WipeUp", "WipeDown"]
        self.contextMenuButton = ContextMenuButton("Wipe", options)
        self.contextMenuButton.setSize(100, 50)  # Set button size
        self.layout().addWidget(self.contextMenuButton)


if __name__ == "__main__":
    app = QApplication([])
    test = TestContextMenuButton()
    test.show()
    app.exec_()
