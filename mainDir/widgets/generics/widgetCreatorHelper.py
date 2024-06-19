from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


class WidgetHelper:
    @staticmethod
    def createWidgetRow(widgetType, widgetList, numbers, functionCall,
                        width, height, style=None, namesList=None,
                        setCheckable=True, prefix="", showText=True):
        """
        Crea una riga di widget e li configura con dimensioni e segnali.
        """
        widgets = []
        widgetsNameList = []
        for i in range(numbers):
            name = namesList[i] if namesList else f""
            if prefix:
                name = f"{prefix}"
            if showText:
                widget = widgetType(name)
            else:
                widget = widgetType()
            widget.setFixedSize(width, height)
            widget.setObjectName(f"{name}_{i + 1}")
            if style:
                widget.setStyleSheet(style)
            if isinstance(widget, QLineEdit):
                widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if isinstance(widget, QPushButton):
                widget.setCheckable(setCheckable)
                if functionCall:
                    widget.clicked.connect(functionCall)
            widgetList.append(widget)
            widgets.append(widget)
            print(f"created: {widget.objectName()}")
        return widgets

    @staticmethod
    def set_button_style(btn, style, width, height, name, widgetList=None, isCheckable=False):
        btn.setStyleSheet(style)
        btn.setFixedSize(width, height)
        btn.setObjectName(name)
        if widgetList is not None:
            widgetList.append(btn)
        if isCheckable:
            btn.setCheckable(True)

