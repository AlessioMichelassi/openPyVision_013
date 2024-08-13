import time
import cv2
import numpy as np
from PyQt6.QtCore import *


class BaseClass(QObject):
    """
    Classe base per la generazione di immagini. È una classe QObject, quindi può essere usata con i segnali e gli slot,
    ma non ha un'interfaccia grafica. Viene usata come template per costruire tutti gli input che generano immagini.
    Ogni input può trasformare la propria immagine in base a delle impostazioni, come la correzione gamma, il negativo,
    la scala di grigi, l'unsharp mask e il selfScreen.
    """
    _frame = None
    _gamma_correction = 1.0
    isGrayScale = False
    isNegative = False
    isSelfScreen = False
    isMaskedScreen = False
    isFlipped = False
    isBlurred = False
    screenMask = None
    flipType = 0
    _blurAmount = 40

    def __init__(self, synchObject, resolution=QSize(1920, 1080)):
        """
        Inizializza la classe base con un oggetto di sincronizzazione e una risoluzione.
        Connette il segnale di sincronizzazione alla funzione capture_frame.
        """
        super().__init__()
        self.synch_Object = synchObject
        self.resolution = resolution
        self.synch_Object.synch_SIGNAL.connect(self.captureFrame)
        self.start_time = time.time()
        self.frame_count = 0
        self.total_time = 0
        self.fps = 0
        self.last_update_time = time.time()

    def __del__(self):
        """
        Rilascia le risorse e ferma il frame processor.
        """
        # Force garbage collection
        self.frame_processor = None
        # Imposta su None tutte le variabili
        for key in self.__dict__.keys():
            self.__dict__[key] = None

    def setGammaCorrection(self, value):
        """
        Imposta il valore di correzione gamma.
        :param value: Valore della correzione gamma.
        """
        self._gamma_correction = value

    def stop(self):
        """
        Ferma il frame processor se è in esecuzione. Inizialmente avevo pensato di usare un thread
        per il frame processor, poi poi varie propve ho deciso di non usarlo, preferendo solo metodi che non
        inficiassero la performance.
        """
        try:
            if hasattr(self, 'frame_processor') and self.frame_processor.isRunning():
                self.frame_processor.stop()
        except RuntimeError as e:
            print(f"Error stopping frame processor: {e}")

    def captureFrame(self):
        """
        Cattura un frame, aggiornando l'FPS e creando un'immagine nera della risoluzione specificata.
        """
        self.updateFps()
        image = np.zeros((self.resolution.height(), self.resolution.width(), 3), dtype=np.uint8)
        self._frame = np.ascontiguousarray(image)

    def updateFps(self):
        """
        Aggiorna il valore di FPS (frame per secondo).
        """
        self.frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        if elapsed_time >= 1.0:  # Update FPS every second
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.last_update_time = current_time

    def flipFrame(self):
        """
        Ritorna il flip del frame.
        :param flipCode: es. 0: flip orizzontale, 1: flip verticale, -1: flip orizzontale e verticale.
        :return: Frame ribaltato.
        """
        return cv2.flip(self._frame, self.flipType)

    def setFlipType(self, flipType: int):
        """
        Imposta il tipo di flip da applicare al frame.
        :param flipType: Tipo di flip da applicare.
        """
        self.flipType = flipType

    @staticmethod
    def gammaCorrection(gamma: float):
        """
        Crea una Look-Up Table per la correzione di gamma.
        :param gamma: Valore di gamma.
        :return: Tabella di Look-Up per la correzione di gamma.
        """
        invGamma = 1.0 / gamma
        table = np.array([(i / 255.0) ** invGamma * 255 for i in range(256)]).astype("uint8")
        return table

    @staticmethod
    def negative(frame):
        """
        Applica l'effetto negativo al frame.
        :param frame: Frame da trasformare.
        :return: Frame con effetto negativo.
        """
        return cv2.bitwise_not(frame)

    @staticmethod
    def grayScale(frame):
        """
        Converte il frame in scala di grigi.
        :param frame: Frame da convertire.
        :return: Frame in scala di grigi.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.merge((gray, gray, gray))

    @staticmethod
    def applyUnSharpMask(image, amount=1.5, radius=1.0, threshold=0):
        """
        Applica l'Unsharp Mask al frame per aumentarne il contrasto.
        :param image: Immagine da elaborare.
        :param amount: Quantità di contrasto.
        :param radius: Raggio della sfocatura.
        :param threshold: Soglia.
        :return: Immagine con Unsharp Mask applicata.
        """
        blurred = cv2.GaussianBlur(image, (0, 0), radius)
        return cv2.addWeighted(image, 1 + amount, blurred, -amount, 0)

    @staticmethod
    def bitwiseScreenImage(frame):
        """
        Simula l'effetto di autoscreening preso dalla pellicola. Questo metodo aumenta la luminosità del frame
        senza introdurre rumore. IN pratica si moltiplicano insieme i due frame negativi, quindi parti scure e chiare
        rimangono simili mentre mentre le altre subiscono un boost. Purtroppo btiwise_and a quando pare non funziona
        su due immagini identiche. quindi ho lasciato la classe per un futuro upgrade.
        il gain che introdurrebbe rumore.
        :param frame: Frame da elaborare.
        :return: Frame con effetto autoscreening.
        """
        not_frame = cv2.bitwise_not(frame)
        # AND inversi
        and_result = cv2.bitwise_and(not_frame, not_frame)
        return cv2.bitwise_not(and_result)

    def oldSchoolScreen(self, frame):
        """
        Simula l'effetto screen con operazioni bitwise.
        :param frame: Frame da elaborare.
        :return: Frame con effetto screen.
        """
        not_image = cv2.bitwise_not(frame)
        screen_result = 255 - cv2.multiply(not_image, not_image, scale=1.0 / 255.0)

        if self.isMaskedScreen and self.screenMask is not None:
            print("Applying mask")
            mask = self.screenMask.getFrame()
            invMask = cv2.bitwise_not(mask)
            # Applica la maschera al frame originale e all'effetto screen
            masked_original = cv2.multiply(frame, invMask)
            masked_screen = cv2.multiply(screen_result, mask)
            result = cv2.add(masked_original, masked_screen).astype(np.uint8)

            return result

        return screen_result

    def boxBlur(self, image):
        # Applica un box blur utilizzando un kernel di dimensione ksize x ksize
        blurred_image = cv2.blur(image, (self._blurAmount, self._blurAmount))
        return blurred_image

    def setBlurAmount(self, amount: int):
        """
        Imposta l'amount della sfocatura.
        :param amount: Amount della sfocatura.
        """
        self._blurAmount = amount

    def frameProcessor(self, frame):
        """
        Applica le varie trasformazioni al frame in base alle impostazioni correnti.
        :param frame: Frame da elaborare.
        :return: Frame elaborato.
        """
        if self.isFlipped:
            frame = self.flipFrame()
        if self.isSelfScreen:
            frame = self.oldSchoolScreen(frame)
        if self._gamma_correction != 1.0:
            lut = self.gammaCorrection(self._gamma_correction)
            frame = cv2.LUT(frame, lut)
        if self.isNegative:
            frame = self.negative(frame)
        if self.isGrayScale:
            frame = self.grayScale(frame)
        if self.isBlurred:
            frame = self.boxBlur(frame)
        return frame

    def getFrame(self):
        """
        Ritorna il frame corrente.
        :return: Frame corrente.
        """
        return self._frame

    def play(self):
        """
        Metodo play per la compatibilità con il VideoPlayerObject.
        """
        pass

