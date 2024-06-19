from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLineEdit


class LblWidget(QLineEdit):
    lblStyle = """
                QLineEdit {
                    background-color: rgb(20, 20, 25);
                    border: 1px solid rgb(0, 0, 80);
                    border-radius: 5px;
                    color: rgb(153, 204, 255);
                    font-weight: bold;
                    font-size: 12px;
                }
                """

    def __init__(self, name, index, size, parent=None):
        super().__init__(parent)
        if name == "Input":
            self.name = f"Input_{index}"
            self.setText(self.name)
        else:
            self.name = name
            self.setText(self.name)
        self.setObjectName(f"lblInput_{index}")
        self.setBaseSize(size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(self.lblStyle)
        self.setReadOnly(True)
        self.returnPressed.connect(self.onReturnPressed)  # Connect the returnPressed signal to the method

    def mouseDoubleClickEvent(self, event):
        self.setReadOnly(False)

    def focusOutEvent(self, event):
        self.setReadOnly(True)
        self.setObjectName(self.text())  # Update the object name when focus is lost

    def onReturnPressed(self):
        self.setObjectName(self.text())
        self.name = self.text()
        self.setReadOnly(True)

