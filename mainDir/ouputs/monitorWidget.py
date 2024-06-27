import sys
import cv2
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import *

from mainDir.inputs.videoCapture013 import VideoCapture013
from mainDir.ouputs.mainOut_Viewer import CV_MainOutViewer
from mainDir.widgets.generics.btnStyle import btnMonitorStyle
from mainDir.widgets.graphicEngine.graphicSceneOverride012 import GraphicSceneOverride012
from mainDir.widgets.graphicEngine.graphicViewOverride import GraphicViewOverride
from mainDir.widgets.videoWidgets.rgbParade import RGBParade


class MonitorWidget012(QWidget):
    """
    MonitorWidget012 class is a QWidget che mostra un frame video in un QGraphicsView.
    La QGraphicView permette di fare zoom e pan del frame video, oltre a semplificare alcuni processi
    come il rendering di immagini e testi. Da varie prove, fatte misurando lo screen capture di un cronometro
    rispetto all'output del cronometro stesso, la differenza è di circa 0,043 secondi ovvero con un frame rate di 60 fps
    la differenza è di circa 2,6 frame. Questo significa che il monitor è in grado di visualizzare un frame video
    più o meno in tempo reale.

    La graphic view è stata quindi sovrascritta in modo da permettere di fare zoom e pan del frame video.
    in pratica usando la funzione feedInput si può passare un frame video al monitor e questo verrà visualizzato
    nel monitor stesso. il render della scena è invece accessibile tramite getDirtyFrame. Per ottenere il clean feed
    si prende direttamente dal mixBus con il metodo getMix che ritorna preview, mix.
    """
    btnAntialiasing = None
    btnSmootPixmapTransformation = None
    btnOpenGL = None

    def __init__(self, _syncObject, isPrg, parent=None):
        super(MonitorWidget012, self).__init__(parent)
        self._resolution = QSize(1920, 1080)
        self.isPrg = isPrg
        self.syncObject = _syncObject

        # Creazione della scena grafica e della vista grafica
        self.scene = GraphicSceneOverride012()
        self.view = GraphicViewOverride(self.scene)

        # Il clean feed preso dal mixBus viene inserito in questo oggetto
        self.graphicObject = QGraphicsPixmapItem()
        self.scene.addItem(self.graphicObject)

        self.feedFrame = None
        self.rgbParade = None

        # Inizializzazione dei pulsanti
        self.btnFitInView = QPushButton("Fit in View")
        self.btnRed = self.createButton("R", self.setRed)
        self.btnGreen = self.createButton("G", self.setGreen)
        self.btnBlue = self.createButton("B", self.setBlue)
        self.btnRGBParade = self.createButton("RGB Parade", self.setRGBParade)
        self.btnWaveform = self.createButton("Waveform", self.setWaveform)
        self.lblSize = QLabel("1.0")
        self.lblCPU = QLabel("CPU Usage")
        self.lblFps = QLabel("FPS: 0")

        self._isRed = False
        self._isGreen = False
        self._isBlue = False
        self._isAlpha = False
        self._isRGBParade = False
        self._isWaveform = False

        # Lista di pulsanti per i toggle
        self.toggleButtons = [
            (self.btnRed, 'Red'),
            (self.btnGreen, 'Green'),
            (self.btnBlue, 'Blue'),
            (self.btnRGBParade, 'RGBParade'),
            (self.btnWaveform, 'Waveform')
        ]

        self.cmbViewportMode = QComboBox(self)
        self.initUI()
        self.initConnections()
        self.initRenderProperties()

        # Collegamento del segnale di sincronizzazione all'aggiornamento del frame
        self.syncObject.synch_SIGNAL.connect(self.updateFrame)

    def closeEvent(self, event):
        """
        Gestisce l'evento di chiusura della finestra.
        :param event: Evento di chiusura
        :return: None
        """
        super().closeEvent(event)

    def initUI(self):
        """
        Inizializza l'interfaccia utente, organizzando i layout e aggiungendo widget.
        :return: None
        """
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(self.initViewPortButtons())
        mainLayout.addWidget(self.view)
        mainLayout.addLayout(self.initButtonsLayer())
        self.setLayout(mainLayout)

    def initViewPortButtons(self):
        """
        Inizializza i pulsanti per la gestione della viewPort.
        La graphicView può essere aggiornata in tre modi:
        - minimal: solo quando è necessario
        - smart: quando è necessario e in modo intelligente
        - full: sempre
        OpenGL è un'opzione che permette di usare la GPU per il rendering.
        SmoothPixmapTransformation permette di fare il rendering delle immagini in modo più fluido.
        Antialiasing permette di avere un rendering più pulito.
        Ovviamente siccome alcune opzioni possono essere pesanti, è possibile disattivarle.
        Di default nel monitor di preview alcune voci sono disattivate.
        :return: Layout dei pulsanti
        """
        self.cmbViewportMode.addItems(["minimal", "smart", "full"])
        self.cmbViewportMode.currentIndexChanged.connect(self.setViewportMode)

        self.btnAntialiasing = self.createButton("Antialiasing", self.setAntialiasing)
        self.btnSmootPixmapTransformation = self.createButton("Smooth Pixmap Transformation",
                                                              self.setSmoothPixmapTransformation)
        self.btnOpenGL = self.createButton("OpenGL", self.setOpenGL)

        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.cmbViewportMode)
        btnLayout.addWidget(self.btnAntialiasing)
        btnLayout.addWidget(self.btnSmootPixmapTransformation)
        btnLayout.addWidget(self.btnOpenGL)
        btnLayout.addItem(spacer)
        return btnLayout

    @staticmethod
    def createButton(text, slot):
        """
        Utility function per creare un pulsante con uno stile specifico.
        :param text: Testo del pulsante
        :param slot: Funzione da chiamare al clic del pulsante
        :return: QPushButton
        """
        btn = QPushButton(text)
        btn.setStyleSheet(btnMonitorStyle)
        btn.setCheckable(True)
        btn.clicked.connect(slot)
        return btn

    def initRenderProperties(self):
        """
        Inizializza le proprietà di rendering della view.
        Se isPrg è True, allora le opzioni di rendering sono più pesanti.
        :return: None
        """
        self.view.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        if self.isPrg:
            self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            self.view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
            self.btnSmootPixmapTransformation.setChecked(True)
            self.btnAntialiasing.setChecked(True)
            self.cmbViewportMode.setCurrentIndex(2)
        else:
            self.view.setRenderHint(QPainter.RenderHint.Antialiasing, False)
            self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
            self.view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate)
            self.btnSmootPixmapTransformation.setChecked(False)
            self.btnAntialiasing.setChecked(False)
            self.cmbViewportMode.setCurrentIndex(0)

        self.view.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontSavePainterState, True)
        self.view.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True)
        self.view.setViewport(QOpenGLWidget())
        self.btnOpenGL.setChecked(True)

    def initButtonsLayer(self):
        """
        Inizializza i pulsanti del livello inferiore dell'interfaccia utente.
        :return: Layout dei pulsanti
        """
        self.btnFitInView.clicked.connect(self.fitInView)
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.lblFps)
        lbl = QLabel("Scale:")
        buttonLayout.addWidget(lbl)
        buttonLayout.addWidget(self.lblSize)
        buttonLayout.addItem(spacer)
        buttonLayout.addWidget(self.btnRed)
        buttonLayout.addWidget(self.btnGreen)
        buttonLayout.addWidget(self.btnBlue)
        if not self.isPrg:
            buttonLayout.addWidget(self.btnRGBParade)
            buttonLayout.addWidget(self.btnWaveform)
        buttonLayout.addWidget(self.btnFitInView)
        return buttonLayout

    @staticmethod
    def createColorButton(text, slot, width):
        """
        Utility function per creare un pulsante di colore con una larghezza specifica.
        :param text: Testo del pulsante
        :param slot: Funzione da chiamare al clic del pulsante
        :param width: Larghezza del pulsante
        :return: QPushButton
        """
        btn = QPushButton(text)
        btn.setFixedWidth(width)
        btn.clicked.connect(slot)
        return btn

    def initConnections(self):
        """
        Inizializza le connessioni dei segnali.
        :return: None
        """
        self.view.currentScaleChange.connect(self.setlblScale)

    def feedInput(self, inputNumpyFrame):
        """
        Fornisce un frame di input da visualizzare nel monitor.
        :param inputNumpyFrame: Frame di input
        :return: None
        """
        self.feedFrame = inputNumpyFrame

    def getDirtyFrame(self):
        """
        Restituisce il frame sporco della scena.
        :return: Frame sporco
        """
        return self.scene.getDirtyFrame()

    def updateFrame(self):
        """
        Aggiorna il frame visualizzato nel monitor.
        :return: None
        """
        if self.feedFrame is None:
            frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        else:
            frame = self.processFrame(self.feedFrame)
        qImage = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_BGR888)
        self.graphicObject.setPixmap(QPixmap.fromImage(qImage))
        if self.rgbParade is not None:
            self.rgbParade.source = self.feedFrame

    def processFrame(self, frame):
        """
        Elabora il frame di input per visualizzare solo il canale selezionato.
        :param frame: Frame di input
        :return: Frame elaborato
        """
        if self._isRed:
            frame = self.extractChannel(frame, 0)
        elif self._isGreen:
            frame = self.extractChannel(frame, 1)
        elif self._isBlue:
            frame = self.extractChannel(frame, 2)
        elif self._isAlpha and frame.shape[2] == 4:
            frame = self.extractChannel(frame, 3)
        return frame

    @staticmethod
    def extractChannel(frame, channel):
        """
        Estrae un canale specifico dal frame.
        :param frame: Frame di input
        :param channel: Canale da estrarre
        :return: Frame con solo il canale estratto
        """
        channels = cv2.split(frame)
        if len(channels) == 4:
            channels = channels[:3] + [channels[channel]]
        return cv2.merge([channels[channel]] * 3)

    def fitInView(self):
        """
        Adatta la vista al contenuto della scena.
        :return: None
        """
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def setRed(self):
        """
        Attiva/disattiva la visualizzazione del canale rosso.
        :return: None
        """
        self.toggleColorChannel('Red')

    def setGreen(self):
        """
        Attiva/disattiva la visualizzazione del canale verde.
        :return: None
        """
        self.toggleColorChannel('Green')

    def setBlue(self):
        """
        Attiva/disattiva la visualizzazione del canale blu.
        :return: None
        """
        self.toggleColorChannel('Blue')

    def setRGBParade(self):
        """
        Attiva/disattiva la visualizzazione del grafico RGB Parade.
        :return: None
        """
        self.toggleColorChannel('RGBParade')

    def setWaveform(self):
        """
        Attiva/disattiva la visualizzazione del grafico Waveform.
        :return: None
        """
        self.toggleColorChannel('Waveform')

    def toggleColorChannel(self, color):
        """
        Attiva/disattiva la visualizzazione di un canale colore specifico.
        Disattiva tutti gli altri canali.
        :param color: Colore da attivare/disattivare
        :return: None
        """
        # Disattiva tutti i pulsanti tranne quello selezionato
        for btn, col in self.toggleButtons:
            if col != color:
                btn.setChecked(False)
                setattr(self, f'_is{col}', False)
            else:
                setattr(self, f'_is{col}', not getattr(self, f'_is{col}'))
                btn.setChecked(getattr(self, f'_is{col}'))

    def setAutoFit(self):
        """
        Adatta automaticamente la vista al contenuto della scena.
        :return: None
        """
        self.fitInView()

    def setlblScale(self, scale):
        """
        Imposta l'etichetta della scala.
        :param scale: Scala attuale
        :return: None
        """
        self.lblSize.setText(f'{scale:.4f}')

    def setViewportMode(self, index):
        """
        Imposta la modalità di aggiornamento della viewport.
        :param index: Indice della modalità
        :return: None
        """
        modes = [QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate,
                 QGraphicsView.ViewportUpdateMode.SmartViewportUpdate,
                 QGraphicsView.ViewportUpdateMode.FullViewportUpdate]
        self.view.setViewportUpdateMode(modes[index])

    def setAntialiasing(self):
        """
        Attiva/disattiva l'antialiasing.
        :return: None
        """
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing, self.btnAntialiasing.isChecked())

    def setSmoothPixmapTransformation(self):
        """
        Attiva/disattiva la trasformazione fluida delle pixmap.
        :return: None
        """
        self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, self.btnSmootPixmapTransformation.isChecked())

    def setOpenGL(self):
        """
        Attiva/disattiva l'uso di OpenGL per il rendering.
        :return: None
        """
        self.view.turnOnOpenGL(self.btnOpenGL.isChecked())

    def updateFps(self, fps):
        """
        Aggiorna l'etichetta degli FPS.
        :param fps: Valore degli FPS
        :return: None
        """
        self.lblFps.setText(f"FPS: {fps:.2f}")


if __name__ == '__main__':
    from mainDir.inputs.synchObject import SynchObject
    from mainDir.inputs.generator_bars_EBU import FullBarsGenerator

    def updateMonitor():
        """
        Aggiorna il monitor con il frame corrente e il valore degli FPS.
        :return: None
        """
        monitor.feedInput(input1.getFrame())
        monitor.updateFps(input1.fps)
        mainOut.feedFrame(monitor.getDirtyFrame())

    app = QApplication(sys.argv)
    synchObject = SynchObject()
    input1 = VideoCapture013(synchObject, 7)
    monitor = MonitorWidget012(synchObject, isPrg=False)
    monitor.setFixedSize(1280, 720)
    mainOut = CV_MainOutViewer(input1.getFrame())
    synchObject.synch_SIGNAL.connect(updateMonitor)
    monitor.show()
    sys.exit(app.exec())
