from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

"""
Questa classe è un helper per ottenere pulsanti che lampeggiano a una certa frequenza per un certo tempo.
Sono utili per dare indicazioni visiva circa il fatto che ad esempio l'esecuzione di un certo effetto è in corso.

    Impostazione dei Colori: 
                La funzione setColors consente di impostare i colori del pulsante in fase di pressione e rilascio.
    Contrasto del Colore: 
                La funzione getContrastingColor calcola il miglior contrasto tra il testo e lo sfondo.
    Stile del Pulsante: 
                La funzione getStyleSheet crea lo stile del pulsante in base ai colori forniti.
    Lampeggio: 
                Le funzioni startBlinking, stopBlinking e _toggleBlink gestiscono il comportamento 
                del lampeggio del pulsante.
    Timeout del Lampeggio: 
                La funzione setBlinkingTimeOut imposta un timeout per fermare il lampeggio dopo un certo periodo.
"""


class BlinkingButton(QPushButton):
    borderPressed = ""
    borderUnPressed = ""
    colorPressed = ""
    colorUnPressed = ""

    def __init__(self, text, blinkColor="rgb(255,128,10)", blinkInterval=50, blinkingTimeOut=100, parent=None):
        super(BlinkingButton, self).__init__(text, parent)
        self.blinkColor = QColor(blinkColor)
        self.normalColor = QColor("lightgrey")
        self.blinkInterval = blinkInterval
        self.blinkTimerTimeout = blinkingTimeOut
        self.blinkTimer = QTimer(self)
        self.blinkTimer.timeout.connect(self._toggleBlink)
        self.stopTimer = QTimer(self)
        self.stopTimer.timeout.connect(self.stopBlinking)
        self.isBlinkOn = False
        self.blinkingIndex = 0
        self.setColors()
        self.setStyleSheet(self.getStyleSheet(self.normalColor, self.borderUnPressed, self.colorUnPressed))

    def setSize(self, width, height):
        """
        Setta le dimensioni del pulsante
        :param width: larghezzza
        :param height: altezza
        :return:
        """
        self.setFixedSize(width, height)

    def setColors(self, blinkColor=QColor(255, 128, 10), btnUnPressedColor="lightgrey"):
        """
        Setta i colori del pulante in fase di pressione e rilascio
        nel caso in cui non siano specificati i colori setta il bordo più curo di 50
        rispetto al colore dello sfondo e il testo con un colore a alto contrasto rispetto allo sfondo
        :return:
        """
        if blinkColor:
            self.blinkColor = QColor(blinkColor)
        if btnUnPressedColor:
            self.normalColor = QColor(btnUnPressedColor)
        self.borderPressed = self.blinkColor.darker(150).name()
        self.borderUnPressed = self.normalColor.darker(150).name()
        self.colorPressed = self.getContrastingColor(self.blinkColor).name()
        self.colorUnPressed = self.getContrastingColor(self.normalColor).name()

    @staticmethod
    def getContrastingColor(color):
        """
        Ritorna il colore con il miglior contrasto
        :param color: il colore di riferimento
        :return:
        """
        yiq = ((color.red() * 299) + (color.green() * 587) + (color.blue() * 114)) / 1000
        return QColor("black") if yiq >= 128 else QColor("white")

    @staticmethod
    def getStyleSheet(bgColor, borderColor, textColor):
        """
        Ritorna lo stile del pulsante
        :param bgColor: il colore dello sfondo
        :param borderColor: il colore del bordo
        :param textColor: il colore del testo
        :return:
        """
        return f"""
        QPushButton {{
            background-color: {bgColor.name()};
            border: 2px solid {borderColor};
            border-radius: 5px;
            color: {textColor};
        }}
        """

    def _returnStyleSheet(self):
        """
        Quando il pulsante non lampeggia viene assegnato un colore di default
        al pulsante premuto/non premuto
        :return:
        """
        style = f"""
        QPushButton:pressed  {{
            background-color: {self.blinkColor.name()};
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

    def setBlinkingSpeed(self, interval):
        """
        Setta la velocità del lampeggio
        :param interval:
        :return:
        """
        self.blinkInterval = interval
        self.blinkTimer.setInterval(self.blinkInterval)

    def setBlinkingTimeOut(self, timeout):
        """
        Setta il timeout del lampeggio
        :param timeout:
        :return:
        """
        self.blinkTimerTimeout = timeout

    def startBlinking(self):
        """
        fa partire il timer del lampeggio
        :return:
        """
        self.blinkingIndex = 0
        self.blinkTimer.start(self.blinkInterval)
        self.stopTimer.start(int(self.blinkTimerTimeout * 100))  # Convert to milliseconds

    def stopBlinking(self):
        """
        Ferma il timer del lampeggio
        :return:
        """
        self.blinkTimer.stop()
        self.stopTimer.stop()
        self.setStyleSheet(self._returnStyleSheet())
        self.isBlinkOn = False

    def _toggleBlink(self):
        """
        Inverte i colori durante il lampeggio
        :return:
        """
        self.isBlinkOn = not self.isBlinkOn
        self.blinkingIndex += self.blinkInterval / 1000.0
        if self.isBlinkOn:
            self.setStyleSheet(self.getStyleSheet(self.blinkColor, self.borderPressed, self.colorPressed))
        else:
            self.setStyleSheet(self.getStyleSheet(self.normalColor, self.borderUnPressed, self.colorUnPressed))

        if 0 < self.blinkTimerTimeout <= self.blinkingIndex:
            self.stopBlinking()


# TEST CLASS
class TestBlinkingButton(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blinking Button Test")
        self.setGeometry(100, 100, 400, 200)
        self.setLayout(QVBoxLayout())
        self.blinkingButton = BlinkingButton("Blinking Button")
        self.layout().addWidget(self.blinkingButton)
        self.blinkingButton.setBlinkingSpeed(200)
        self.blinkingButton.setBlinkingTimeOut(5)  # 5 seconds timeout
        self.blinkingButton.startBlinking()


if __name__ == "__main__":
    app = QApplication([])
    test = TestBlinkingButton()
    test.show()
    app.exec()
