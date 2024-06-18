import time
from enum import Enum

import numpy as np
import cv2
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.inputs.generator_bars_EBU import FullBarsGenerator
from mainDir.inputs.generator_bars_SMPTE import SMPTEBarsGenerator
from mainDir.inputs.imageLoader_Stinger import StingerLoader


class MIX_TYPE(Enum):
    NONE = 0
    MIX = 1
    WIPE_LEFT = 2
    WIPE_RIGHT = 3
    WIPE_BOTTOM = 4
    WIPE_TOP = 5
    STINGER = 6
    STILL = 7
    DIP = 8
    DVE = 9


class MixBus014(QObject):
    """
    MixBus014 è il cuore del mixer video e permette di mixare due oggetti input.
    Di default resituisce tramite getMix una tupla: preview, program.
    Se l'effetto è impostato su MIX, restituisce:
    preview, cv2.addWeighted(_preview_frame, self._fade, _program_frame, 1 - self._fade, 0)
    dove previewFrame è il frame di preview e programFrame è il frame di program.
    fade è una variabile che viene aumentata di una certa quantità per un certo periodo di tempo tramite
    un QTimer che viene fatto partire generalmente quando si preme il pulsante auto o quando
    si usa la slide bar per fare il mix.
    """
    effectDuration = 500
    lastProgram = None
    errorSignal = pyqtSignal(dict)

    def __init__(self, syncObject, parent=None):
        super().__init__(parent)
        self.preview_input = FullBarsGenerator(syncObject)
        self.program_input = SMPTEBarsGenerator(syncObject)
        self.still = None

        self.synch_object = syncObject
        self._mixType = MIX_TYPE.MIX
        self.is_mixing = False

        self._fade = 0.0
        self.stingerIndex = 0
        self.fade_step = 0.01
        self.blend_width = 50  # Adjust blend width as needed
        self.effect_TIMER = QTimer(self)
        self.effect_TIMER.timeout.connect(self.updateEffect)
        self.stingerObject = StingerLoader(self.synch_object, r"C:\pythonCode\openPyVision_013\testSequence")

        # Connect stinger's switching signal to the cut method
        self.stingerObject.switching_SIGNAL.connect(self.cutOnSwithing)

    def __del__(self):
        try:
            self.preview_input.stop()
            self.program_input.stop()
        except AttributeError:
            pass

    @staticmethod
    def returnBlack():
        """
        Ritorna un frame nero in fullHD.
        Questa funzione viene utilizzata nel caso in cui non sia presente uno o nessun degli input.
        :return: an array np
        """
        return np.zeros((1080, 1920, 3), dtype=np.uint8)

    def _getFrame(self, input_source):
        """
        La funzione _getFrame restituisce il frame dell'input sorgente e nel caso in cui
        l'input sorgente non sia presente restituisce un frame nero.
        :param input_source: l'input
        :return: il frame corrente dell'input
        """
        try:
            return input_source.getFrame()
        except AttributeError:
            return self.returnBlack()

    def setPreviewInput(self, videoObject):
        """
        Imposta l'input di preview.
        :param videoObject:
        :return:
        """
        self.preview_input = videoObject

    def setProgramInput(self, videoObject):
        """
        Imposta l'input di program.
        :param videoObject:
        :return:
        """
        self.program_input = videoObject

    def setStill(self, videoObject):
        """
        Imposta l'immagine di tappo.
        :param videoObject:
        :return:
        """
        self.still = videoObject

    def setEffectType(self, mixType):
        """
        Imposta il tipo di effetto.
        :param mixType:
        :return:
        """
        self._mixType = mixType

    def getEffectType(self):
        """
        Restituisce il tipo di effetto.
        :return:
        """
        return self._mixType

    def cut(self):
        """
        Cut, inverte gli input.
        :return:
        """
        self.preview_input, self.program_input = self.program_input, self.preview_input

    def getMix(self):
        """
        Dati due input preview e program restituisce il mix dei due input.
        Di default restituisce una tupla preview, program.
        :return:
        """
        preview_frame = self._getFrame(self.preview_input)
        program_frame = self._getFrame(self.program_input)
        if not self.is_mixing:
            # is_mixing viene attivata solo quando si chiama startMix in questo modo
            # si evita di avere carichi di lavoro indesiderati.
            return preview_frame, program_frame
        else:
            if self._mixType == MIX_TYPE.MIX:
                return preview_frame, self._mixFrames(preview_frame, program_frame)
            elif self._mixType == MIX_TYPE.STINGER:
                return preview_frame, self._mixStinger(preview_frame, program_frame, self.stingerObject)
            elif self._mixType == MIX_TYPE.STILL:
                if self.still is None:
                    self.errorSignal.emit({"error": "No still image loaded."})
                    return preview_frame, program_frame
                return preview_frame, self.still.getFrame()

    def _mixFrames(self, _preview_frame, _program_frame):
        """
        Helper function for getMix. Mixa due frame usando come valore per l'opacità
        _fade che va sempre da 0 a 1.
        :param _preview_frame: il frame di preview
        :param _program_frame: il frame di program
        :return: il mix dei due frame
        """
        return cv2.addWeighted(_preview_frame, self._fade, _program_frame, 1 - self._fade, 0)

    def _mixStinger(self, _preview_frame, _program_frame, _stingerObject):
        """
        Lo stinger è una sequenza di immagini con alpha channel che di solito viene usata per
        introdurre replay, per terminare lo stream, per introdurre un ospite, per lo stacco pubblicitario, ecc.
        Facendo un pò di esperimenti, ho scoperto che la soluzione migliore per compositare due immagini di cui una
        ha un alpha channel è usare la bitwise_and operation perchè operano su singoli bit.
        in pratica viene estratto il canale alpha, con il bitwise_not si inverte il canale alpha, quindi si moltiplica
        l'alpha invertito per l'immagine di background e l'alpha per l'immagine di overlay.
        Si sommano i due risultati e si ottiene il mix. L'oggetto stinger ha una funzione getFillAndKey che restituisce
        una tupla (bgr, alpha) dove alpha è monocanale.
        :param _preview_frame: il frame di preview
        :param _program_frame: il frame di program
        :param _stingerObject: l'oggetto Stinger
        :return:
        """
        overlay_img, alpha = _stingerObject.getFillAndKey()
        overlay_alpha = cv2.merge((alpha, alpha, alpha))
        inva = cv2.bitwise_not(alpha)
        background_alpha = cv2.merge((inva, inva, inva))
        # Apply bitwise_and operation for alpha blending
        overlay = cv2.bitwise_and(overlay_img, overlay_alpha)
        background = cv2.bitwise_and(_program_frame, background_alpha)
        # Add the overlay and background
        result = cv2.add(overlay, background)
        return result

    def _mixStill(self, frameToMix):
        """
        Nel mixer si può usare un'immagine di tappo, un logo per mettere che di solito viene usata
        in pausa il mix, per terminare lo stream, nel caso di problemi tecnici, ecc.
        :param frameToMix: il frame da mixare
        :return: il mix del logo con il frame o solamente lo still frame nel caso in cui l'opacità sia 0
        """
        still_frame = self._getFrame(self.still)
        if self._fade != 0.0:
            return cv2.addWeighted(frameToMix, self._fade, still_frame, 1 - self._fade, 0)
        else:
            return frameToMix, still_frame

    def startMix(self):
        """
        Fa partire il timer per fare il mix.
        fadeStep è la quantità di opacità che viene aumentata per un certo periodo di tempo.
        :param duration:
        :return:
        """
        self._fade = 0.0
        self.is_mixing = True
        self.fade_step = 1.0 / (self.effectDuration / (1000 / self.synch_object.fps))
        self.effect_TIMER.start(1000 // self.synch_object.fps)

    def updateEffect(self):
        """
        Aggiorna l'effetto di mixaggio. Se l'opacità è 1.0 allora si ferma il timer e si resetta l'opacità
        e chiama il cut per invertire i due input, in questo modo il fade è monodirezionale, va sempre da 0 a 1
        e non c'è bisogno di invertire la logica.
        :return:
        """
        if self.is_mixing:
            self._fade += self.fade_step
            if self._fade >= 1.0:
                self._fade = 1.0
                self.is_mixing = False
                self.effect_TIMER.stop()
                self._fade = 0.0
                self.cut()

    def startStinger(self):
        self.stingerIndex = 0
        self.lastProgram = self.program_input
        self.is_mixing = True
        self.stingerObject.startAnimation()

    def updateStinger(self):
        pass

    def cutOnSwithing(self):
        self.cut()
        print("Cutting on switching signal")