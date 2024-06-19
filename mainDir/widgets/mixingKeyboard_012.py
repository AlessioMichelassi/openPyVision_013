from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.widgets.generics.blinkingButton import BlinkingButton
from mainDir.widgets.generics.btnStyle import sliderStyle, lblStyle, btnGreenStyle, btnRedStyle, btnTransitionStyle, \
    btnKeyStyle, btnCutStyle, btnSpecialStyle
from mainDir.widgets.generics.widgetCreatorHelper import WidgetHelper

"""
Mixer Panel Widget è un widget con la tastiera del mixer.
"""


class MixerPanelWidget_012(QWidget):
    tally_SIGNAL = pyqtSignal(dict, name="btnClicked_SIGNAL")
    height = 60
    width = 100
    factor = 0.65
    blinkingTime = 100
    labelNames = ["input1", "input2", "input3", "input4", "input5", "input6", "input7", "input8", "input9", "input10",
                  "input11", "input12", "input13", "input14", "input15", "input16"]
    downStreamKeyNames = ["key1", "key2", "key3"]
    btnEnabled = [1, 2, 9]
    btnDictionary = {"preview": 1, "program": 2,
                     "transition": 0, "key": False, "key2": False, "key3": False,
                     "lbl_1": "input1", "lbl_2": "input2", "lbl_3": "input3", "lbl_4": "input4",
                     "lbl_5": "input5", "lbl_6": "input6", "lbl_7": "input7", "lbl_8": "input8",
                     "lbl_9": "input9", "lbl_10": "input10", "lbl_11": "input11", "lbl_12": "input12",
                     "lbl_13": "input13", "lbl_14": "input14", "lbl_15": "input15", "lbl_16": "input16", }
    isFadeInverted = False

    def __init__(self, parent=None):
        super(MixerPanelWidget_012, self).__init__(parent)
        """
        Qui vengono inizializzate le variabili di istanza della classe
        widget che verranno utilizzati come pulsanti e lo slider
        """
        self.labels = []
        self.btnsPreview = []
        self.btnsProgram = []
        self.btnsTransition = []
        self.btnCuts = []
        self.btnKeys = []
        self.btnCtrl = QPushButton("Ctrl")
        self.btnArrowLeft = QPushButton("<-")
        self.btnArrowRight = QPushButton("->")
        self.btnShift = QPushButton("Shift")
        self.btnAuto = BlinkingButton("AUTO")
        self.btnCut = BlinkingButton("CUT")
        self.slider = QSlider(Qt.Orientation.Vertical)
        self.slider.setStyleSheet(sliderStyle)
        self.initUI()
        self.initConnections()
        self.fadeDuration = 1000  # durata totale del movimento del fade in millisecondi
        self.fadeTimer = QTimer()
        self.fadeTimer.setInterval(100)
        self.fadeTimer.timeout.connect(self.onAutoChange)
        self.blinkCount = 0
        self.btnAuto.setBlinkingSpeed(100)  # velocità del lampeggio in millisecondi
        self.btnAuto.setBlinkingTimeOut(self.fadeDuration / 100)  # timeout del lampeggio uguale alla durata del fade

        # setta il banco di pulsanti iniziale
        self.restoreButtonState()
        self.updateLabelsAndButtons(False)
        # setta il pulsante di transizione iniziale MIX
        self.btnsTransition[0].setChecked(True)

    def initUI(self):
        self._createButtonsAndLabels()
        self.initLayout()

    def _createButtonsAndLabels(self):
        btn_width = int(self.width * self.factor)
        btn_height = int(self.height * self.factor)

        self.labels = WidgetHelper.createWidgetRow(QLineEdit, self.labels, 8, None,
                                                   btn_width, int(btn_height * 0.5),
                                                   style=lblStyle, setCheckable=False,
                                                   prefix="lbl", showText=True)
        self.btnsPreview = WidgetHelper.createWidgetRow(QPushButton, self.btnsPreview, 8, self.onPreviewClicked,
                                                        btn_width, btn_height,
                                                        style=btnGreenStyle, setCheckable=True,
                                                        prefix="prw", showText=False)
        self.btnsProgram = WidgetHelper.createWidgetRow(QPushButton, self.btnsProgram, 8, self.onProgramClicked,
                                                        btn_width, btn_height,
                                                        style=btnRedStyle, setCheckable=True,
                                                        prefix="prg", showText=False)

        transitionList = ["MIX", "DIP", "WIPE", "STING", "DVE", "STILL"]
        self.btnsTransition = WidgetHelper.createWidgetRow(QPushButton, self.btnsTransition, 6,
                                                           self.onTransitionButtonClicked, int(btn_width * 0.6),
                                                           int(btn_height * 0.6), btnTransitionStyle,
                                                           namesList=transitionList, setCheckable=True,
                                                           prefix="", showText=True)

        keyList = ["KEY1", "KEY2", "KEY3"]
        self.btnsKeys = WidgetHelper.createWidgetRow(QPushButton, self.btnKeys, 3, self.onKeyButtonClicked,
                                                     int(btn_width * 0.6), int(btn_height * 0.6), btnKeyStyle,
                                                     namesList=keyList, setCheckable=True,
                                                     prefix="KEY", showText=True)

        WidgetHelper.set_button_style(self.btnAuto, btnCutStyle, btn_width, btn_height, "btnAuto", self.btnCuts)
        WidgetHelper.set_button_style(self.btnCut, btnCutStyle, btn_width, btn_height, "btnCut", self.btnCuts)
        WidgetHelper.set_button_style(self.btnCtrl, btnSpecialStyle, btn_width, btn_height, "btnShiftLeft",
                                      isCheckable=True)
        WidgetHelper.set_button_style(self.btnArrowLeft, btnSpecialStyle, btn_width, btn_height, "btnArrowLeft",
                                      isCheckable=True)
        WidgetHelper.set_button_style(self.btnArrowRight, btnSpecialStyle, btn_width, btn_height, "btnArrowRight",
                                      isCheckable=True)
        WidgetHelper.set_button_style(self.btnShift, btnSpecialStyle, btn_width, btn_height, "btnShiftRight",
                                      isCheckable=True)

    def initLayout(self):
        """
        Inizializza il layout della finestra
        :return:
        """
        mainLayout = QHBoxLayout()
        leftLayout = self.initLeftLayout()
        rightLayout = self.initRightLayout()
        mainLayout.addLayout(leftLayout)
        mainLayout.addWidget(self.slider)
        mainLayout.addLayout(rightLayout)
        self.setLayout(mainLayout)

    def initLeftLayout(self):
        """
        Crea la griglia per il layout dei pulsanti di preview e di program
        a questi sono inclusi il pulsante di shift che serve per selezionare
        gli input da 9 a 16 e il pulsante di controllo per le operazioni speciali.
        I pulsanti con le frecce, nel caso in cui sia presente un 50:50, 70:30 o 30:70
        servono per selezionare in quale casella se quella di destra o sinistra deve essere
        messo l'input che si seleziona.
        :return:
        """
        gridLayout = QGridLayout()

        gridLayout.addWidget(self.btnCtrl, 2, 0)
        gridLayout.addWidget(self.btnArrowLeft, 1, 0)

        for i, (lbl, btn) in enumerate(zip(self.labels, self.btnsPreview)):
            gridLayout.addWidget(lbl, 0, i + 1)
            gridLayout.addWidget(btn, 1, i + 1)

        for i, btn in enumerate(self.btnsProgram):
            gridLayout.addWidget(btn, 2, i + 1)

        gridLayout.addWidget(self.btnArrowRight, 1, len(self.btnsPreview) + 1)
        gridLayout.addWidget(self.btnShift, 2, len(self.btnsPreview) + 1)
        gridLayout.addWidget(self.slider, 0, len(self.btnsPreview) + 2, 6, 1)

        return gridLayout

    def initRightLayout(self):
        """
        Nel right layout sono presenti i pulsanti di transizione, di key e i pulsanti
        per selezionare il cut o la transizione auto.
        :return:
        """
        transitionLayout = QGridLayout()

        for i, btn in enumerate(self.btnsKeys):
            transitionLayout.addWidget(btn, 0, i)

        for i, btn in enumerate(self.btnsTransition):
            row = (i // 3) + 1
            col = i % 3
            transitionLayout.addWidget(btn, row, col)

        autoAndCutLayout = QHBoxLayout()
        autoAndCutLayout.addWidget(self.btnAuto)
        autoAndCutLayout.addWidget(self.btnCut)
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(transitionLayout)
        mainLayout.addLayout(autoAndCutLayout)
        return mainLayout

    def initConnections(self):
        """
        inizializza le connessione tra i pulsanti e le funzioni che devono essere chiamate
        :return:
        """
        self.btnAuto.clicked.connect(self.onAutoClicked)
        self.btnCut.clicked.connect(self.onCutClicked)
        self.btnShift.clicked.connect(self.onShiftClicked)
        self.slider.valueChanged.connect(self.onFadeChange)

    def onPreviewClicked(self):
        """
        Quando viene premuto un pulsante di preview viene emesso un segnale che contiene un dizionario
        del tipo:
                {"tally": "previewChange", "input": numero del pulsante}
        il numero dell'input viene ricavato dal nome del pulsante che è messo nel formato "input_numero",
        nel caso in cui sia premuto il tasto shift al numero viene aggiungo 8 in modo da selezionare
        gli input da 9 a 16.
        :return:
        """
        button = self.sender()
        number = int(button.objectName().split("_")[1])
        if self.btnShift.isChecked():
            number += 8
        if number in self.btnEnabled:
            dictio = {"tally": "previewChange", "input": number}
            self.tally_SIGNAL.emit(dictio)
            for btn in self.btnsPreview:
                if btn != button:
                    btn.setChecked(False)
                else:
                    btn.setChecked(True)
            self.btnDictionary["preview"] = number
        else:
            button.setChecked(False)

    def onProgramClicked(self):
        """
            Quando viene premuto un pulsante di program viene emesso un segnale che contiene un dizionario
            del tipo:
                    {"tally": "previewChange", "input": numero del pulsante}
            il numero dell'input viene ricavato dal nome del pulsante che è messo nel formato "input_numero",
            nel caso in cui sia premuto il tasto shift al numero viene aggiungo 8 in modo da selezionare
            gli input da 9 a 16.
            :return:
        """
        button = self.sender()
        number = int(button.objectName().split("_")[1])
        if self.btnShift.isChecked():
            number += 8
        if number in self.btnEnabled:
            if button.isChecked():
                pass
            else:
                button.setChecked(False)
            dictio = {"tally": "programChange", "input": number}
            self.tally_SIGNAL.emit(dictio)
            for btn in self.btnsProgram:
                if btn != button:
                    btn.setChecked(False)
                else:
                    btn.setChecked(True)
            self.btnDictionary["program"] = number
        else:
            button.setChecked(False)

    def onTransitionButtonClicked(self):
        """
        Quando premiamo il pulsante della transizione viene emesso un dizionario che setta il tipo di transizione
        che verrà eseguita premendo il pulsante auto o muovendo lo slider.
        Ogni pulsante ha un menù accessibile premendo il tasto destro che permette di stabilire ad esempio il tipo di
        wipe se leftToRight, rightToLeft, topToBottom, bottomToTop, centerToEdges, il tipo di Dve, il tipo di sting etc
        etc
        Le transizioni avvenendo a livello di mixBus vengono registrate nel clean feed.
        :return:
        """
        button = self.sender()
        number = int(button.objectName().split("_")[1])
        dictio = {"tally": "transitionChange", "input": number}
        self.tally_SIGNAL.emit(dictio)
        for btn in self.btnsTransition:
            if btn != button:
                btn.setChecked(False)
            else:
                btn.setChecked(True)
        self.btnDictionary["transition"] = number

    def onKeyButtonClicked(self):
        """
        I pulsanti Key sono usati per inserire la grafica in sovraimpressione.
        Generalmente key1 è per i sottopancia, il key 2 per i sottotitoli o il ticker e il key 3 per i bug o i loghi.
        Essendo inseriti dalla graphicScenes non vengono registrati nel clean feed ovvero nel segnale preso direttamente dal mixBus.
        :return:
        """
        button = self.sender()
        number = int(button.objectName().split("_")[1])
        dictio = {"tally": "keyChange", "input": number}
        self.tally_SIGNAL.emit(dictio)

    def onAutoClicked(self):
        """
        Quando viene premuto il pulsante auto viene emesso un segnale che contiene un dizionario
        del tipo:
                {"tally": "auto"}
        e viene fatto partire il timer per il lampeggio del pulsante.
        :return:
        """
        dictio = {"tally": "auto"}
        self.tally_SIGNAL.emit(dictio)
        self.btnAuto.startBlinking()
        self.blinkCount = 0
        self.fadeTimer.start()

    def onCutClicked(self):
        """
        Emette il segnale di cut tramite il dizionario del tally e inverte quello che era in program con la preview
        :return:
        """
        dictio = {"tally": "cut"}
        self.tally_SIGNAL.emit(dictio)
        self.swapPreviewProgram()

    def onFadeChange(self, value):
        """
        Emette un segnale di fade tramite il dizionario del tally con il valore del fade normalizzato 0-1
        :param value:
        :return:
        """
        value = value / 100
        dictio = {"tally": "fade", "input": value}
        self.tally_SIGNAL.emit(dictio)

    def setFadeValue(self, value):
        value = int(value * 100)
        if self.isFadeInverted:
            value = 100 - value
        self.slider.setValue(value)

    def onShiftClicked(self):
        """
        Quando viene premuto lo shift, viene mostrata la seconda parte
        dell'interfaccia con gli input da 9 a 16. Viegono usate due helper function
        per settare/ripristinare i pulsanti e le label.
        updateLabelsAndButtons(shift) permette di cambiare i nomi delle label
        e restoreButtonState permette di ripristinare lo stato dei pulsanti. quindi se è premuto l'input 9
        e sono non è premuto shift, l'input in preview è visualizzato solo premendo shift.
        :return:
        """
        if self.btnShift.isChecked():
            self.updateLabelsAndButtons(shift=True)
        else:
            self.updateLabelsAndButtons(shift=False)
        self.restoreButtonState()

    def updateLabelsAndButtons(self, shift):
        if shift:
            new_labels = self.labelNames[8:]
        else:
            new_labels = self.labelNames[:8]

        for i, lbl in enumerate(self.labels):
            lbl.setText(new_labels[i])

    def restoreButtonState(self):
        for btn in self.btnsPreview:
            number = int(btn.objectName().split("_")[1])
            if self.btnShift.isChecked():
                number += 8
            if number == self.btnDictionary["preview"]:
                btn.setChecked(True)
            else:
                btn.setChecked(False)
        for btn in self.btnsProgram:
            number = int(btn.objectName().split("_")[1])
            if self.btnShift.isChecked():
                number += 8
            if number == self.btnDictionary["program"]:
                btn.setChecked(True)
            else:
                btn.setChecked(False)

    def swapPreviewProgram(self):
        """
        inverte i pulsante di program con quello di preview
        :return:
        """
        prw = self.btnDictionary["preview"]
        prg = self.btnDictionary["program"]
        self.btnDictionary["preview"] = prg
        self.btnDictionary["program"] = prw
        self.restoreButtonState()

    def onAutoChange(self):
        self.blinkCount += 1
        self.slider.blockSignals(True)
        step = 100 / (self.fadeDuration / self.fadeTimer.interval())
        if self.isFadeInverted:
            self.slider.setValue(100 - int(self.blinkCount * step))
        else:
            self.slider.setValue(int(self.blinkCount * step))
        if self.blinkCount * self.fadeTimer.interval() >= self.fadeDuration:
            self.fadeTimer.stop()
            self.slider.blockSignals(False)
            self.btnAuto.setStyleSheet(btnCutStyle)
            self.swapPreviewProgram()
            self.isFadeInverted = not self.isFadeInverted


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    win = MixerPanelWidget_012()
    win.show()
    win.tally_SIGNAL.connect(print)
    sys.exit(app.exec())
