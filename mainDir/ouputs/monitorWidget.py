import sys
import cv2
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import *

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

        self.scene = GraphicSceneOverride012()
        self.view = GraphicViewOverride(self.scene)

        # il clean feed preso dal mixBus viene inserito in questo oggetto
        self.graphicObject = QGraphicsPixmapItem()
        self.scene.addItem(self.graphicObject)

        self.feedFrame = None
        self.rgbParade = None
        # inizializzazione dei pulsanti
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

        self.cmbViewportMode = QComboBox(self)
        self.initUI()
        self.initConnections()
        self.initRenderProperties()

        self.syncObject.synch_SIGNAL.connect(self.updateFrame)

    def closeEvent(self, event):
        super().closeEvent(event)

    def initUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(self.initViewPortButtons())
        mainLayout.addWidget(self.view)
        mainLayout.addLayout(self.initButtonsLayer())
        self.setLayout(mainLayout)

    def initViewPortButtons(self):
        """
        Inizializza i pulsanti per la gestione della viewPort.
        la graphicView può essere aggiornata in tre modi:
        - minimal: solo quando è necessario
        - smart: quando è necessario e in modo intelligente
        - full: sempre
        openGL è un'opzione che permette di usare la GPU per il rendering.
        SmoothPixmapTransformation permette di fare il rendering delle immagini in modo più fluido.
        Antialiasing permette di avere un rendering più pulito.
        Ovviamente siccome alcune opzioni possono essere pesanti, è possibile disattivarle.
        di default nel monitor di preview alcune voci sono disattivate.
        :return:
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
        :param text:
        :param slot:
        :return:
        """
        btn = QPushButton(text)
        btn.setStyleSheet(btnMonitorStyle)
        btn.setCheckable(True)
        btn.clicked.connect(slot)
        return btn

    def initRenderProperties(self):
        """
        Inizializza le proprietà di rendering della view.
        se isPrg è True, allora le opzioni di rendering sono più pesanti.
        :return:
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
        btn = QPushButton(text)
        btn.setFixedWidth(width)
        btn.clicked.connect(slot)
        return btn

    def initConnections(self):
        self.view.currentScaleChange.connect(self.setlblScale)

    def feedInput(self, inputNumpyFrame):
        self.feedFrame = inputNumpyFrame

    def getDirtyFrame(self):
        return self.scene.getDirtyFrame()

    def updateFrame(self):
        if self.feedFrame is None:
            frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        else:
            frame = self.processFrame(self.feedFrame)
        qImage = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_BGR888)
        self.graphicObject.setPixmap(QPixmap.fromImage(qImage))
        if self.rgbParade is not None:
            self.rgbParade.source = self.feedFrame

    def processFrame(self, frame):
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
        channels = cv2.split(frame)
        if len(channels) == 4:
            channels = channels[:3] + [channels[channel]]
        return cv2.merge([channels[channel]] * 3)

    def fitInView(self):
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def setRed(self):
        self.toggleColorChannel('Red')

    def setGreen(self):
        self.toggleColorChannel('Green')

    def setBlue(self):
        self.toggleColorChannel('Blue')

    def setRGBParade(self):
        self._isRed = self._isGreen = self._isBlue = False
        if self.rgbParade is None:
            self.rgbParade = RGBParade(self.feedFrame)
            self.scene.addItem(self.rgbParade)
        else:
            self.scene.removeItem(self.rgbParade)
            self.rgbParade = None

    def setWaveform(self):
        self.toggleColorChannel('Waveform')

    def toggleColorChannel(self, color):
        setattr(self, f'_is{color}', not getattr(self, f'_is{color}'))
        if getattr(self, f'_is{color}'):
            for other_color in ['Red', 'Green', 'Blue', 'Alpha']:
                if other_color != color:
                    setattr(self, f'_is{other_color}', False)

    def setAutoFit(self):
        self.fitInView()

    def setlblScale(self, scale):
        self.lblSize.setText(f'{scale:.4f}')

    def setViewportMode(self, index):
        modes = [QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate,
                 QGraphicsView.ViewportUpdateMode.SmartViewportUpdate,
                 QGraphicsView.ViewportUpdateMode.FullViewportUpdate]
        self.view.setViewportUpdateMode(modes[index])

    def setAntialiasing(self):
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing, self.btnAntialiasing.isChecked())

    def setSmoothPixmapTransformation(self):
        self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, self.btnSmootPixmapTransformation.isChecked())

    def setOpenGL(self):
        self.view.turnOnOpenGL(self.btnOpenGL.isChecked())

    def updateFps(self, fps):
        self.lblFps.setText(f"FPS: {fps:.2f}")


if __name__ == '__main__':
    from mainDir.inputs.synchObject import SynchObject
    from mainDir.inputs.generator_bars_EBU import FullBarsGenerator

    def updateMonitor():
        monitor.feedInput(input1.getFrame())
        monitor.updateFps(input1.fps)

    app = QApplication(sys.argv)
    synchObject = SynchObject()
    input1 = FullBarsGenerator(synchObject)
    monitor = MonitorWidget012(synchObject, isPrg=False)
    monitor.setFixedSize(1280, 720)
    synchObject.synch_SIGNAL.connect(updateMonitor)
    monitor.show()
    sys.exit(app.exec())
