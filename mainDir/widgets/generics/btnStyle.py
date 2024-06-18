# Stile per lo slider
sliderStyle = """
QSlider::groove:vertical {
    background: lightgray;
    width: 2px;
    border: 1px solid #bbb;
    border-radius: 4px;
}

QSlider::handle:vertical {
    background: gray;
    border: 1px solid lightgray;
    height: 20px;
    width: 70px;
    margin: -1px -50px;
    border-radius: 2px;
}
"""

# Stile dei pulsanti verdi (checkable)
btnGreenStyle = """ 
QPushButton:checked {
    background-color: rgb(0, 153, 30);
    border: 1px solid rgb(51, 255, 0);
    border-radius: 5px;
}
QPushButton:!checked {
    background-color: lightgrey;
    color: black;
    border: 2px solid #444;
    border-radius: 5px;
}
"""

# Stile dei pulsanti rossi (checkable)
btnRedStyle = """
QPushButton:checked {
    background-color: rgb(153, 20, 20);
    border: 1px solid rgb(255, 20, 20);
    border-radius: 5px;
    color: white;
}
QPushButton:!checked {
    background-color: lightgrey;
    color: black;
    border: 2px solid #444;
    border-radius: 5px;
}
"""

# Stile dei pulsanti di transizione (checkable)
btnTransitionStyle = """
QPushButton:!checked {
    background-color: lightgrey;
    color: black;
    border: 2px solid #444;
    border-radius: 5px;
}
QPushButton:checked {
    background-color: orange;
    color: black;
    border-radius: 5px;
}
"""

btnKeyStyle = """
QPushButton:!checked {
    background-color: rgb(221, 87, 28);
    border: 2px solid rgb(255, 99, 71);
    color: black;
    border-radius: 5px;
}
QPushButton:checked {
    background-color: rgb(250, 20, 20);
    border: 2px solid rgb(255, 99, 71);
    color: white;
    border-radius: 5px;
}
"""

btnSpecialStyle = """
QPushButton:!checked {
    background-color: lightgrey;
    color: black;
    border: 2px solid #444;
    border-radius: 5px;
}
QPushButton:checked {
    background-color: rgb(70, 20, 130);
    border: 1px solid rgb(20, 20, 255);
    color: white;
    border-radius: 5px;
}
"""

btnCutStyle = """
QPushButton:pressed {
    background-color: rgb(153, 20, 20);
    border: 2px solid rgb(255, 20, 20);
    border-radius: 5px;
    color: white;
}
QPushButton:!pressed {
    background-color: lightgrey;
    color: black;
    border: 2px solid #444;
    border-radius: 5px;
}
"""

# Stile delle etichette L
lblStyle = """
QLineEdit {
    background-color: rgb(40, 40, 40);
    color: rgb(100, 100, 220);
    font-weight: bold;
    border: 2px solid #444;
    text-align: center;
    border-radius: 5px;
}
"""

btnMonitorStyle = """
QPushButton:checked {
    background-color: rgb(255, 165, 20);
    border: 1px solid rgb(255, 99, 71);
    border-radius: 2px;
    color: rgb(0, 0, 0);
}
QPushButton:!checked {
}
"""
