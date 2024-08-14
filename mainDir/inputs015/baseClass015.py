import time
import cv2
import numpy as np
from PyQt6.QtCore import *


class BaseClass015(QObject):
    """
    Classe base per la generazione di immagini. È una classe QObject, quindi può essere usata con i segnali e gli slot,
    ma non ha un'interfaccia grafica. Viene usata come template per costruire tutti gli input che generano immagini.
    Ogni input può trasformare la propria immagine in base a delle impostazioni, come la correzione gamma, il negativo,
    la scala di grigi, l'unsharp mask e il selfScreen.

    This class is the base class for generating images. It is a QObject class, so it can be used with signals and slots,
    but it does not have a graphical interface. It is used as a template to build all inputs that generate images.
    Each input can transform its image based on settings such as gamma correction, negative,
    grayscale, unsharp mask, and selfScreen.
    """

    clip_limit = 2.0
    tile_grid_size = (8, 8)
    gamma = 1.0
    isFrameInverted = False
    isFrameAutoScreen = False
    isFrameCLAHE = False
    isFrameHistogramEqualization = False
    isFrameCLAHEYUV = False
    isFrameHistogramEqualizationYUV = False
    isFlipped = False
    isBlurred = False
    screenMask = None
    isGrayScale = False
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
        self._frame = self.returnBlackFrame()
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

    def returnBlackFrame(self):
        """
        Restituisce un frame nero della risoluzione specificata.
        """
        return np.zeros((self.resolution.height(), self.resolution.width(), 3), dtype=np.uint8)

    def captureFrame(self):
        """
        Cattura un frame, aggiornando l'FPS e creando un'immagine nera della risoluzione specificata.
        """
        self.updateFps()

    def frameProcessor(self, frame):
        """
        Applica le varie trasformazioni al frame in base alle impostazioni correnti.
        :param frame: Frame da elaborare.
        :return: Frame elaborato.
        """
        if self.isFlipped:
            frame = self.flipFrame()
        if self.isFrameInverted:
            frame = self.invertFrame(frame)
        if self.isFrameAutoScreen:
            frame = self.autoScreenFrame(frame)
        if self.gamma != 1.0:
            frame = self.applyGammaByLut(frame, self.gamma)
        if self.isFrameCLAHE:
            frame = self.applyCLAHE(frame)
        if self.isFrameHistogramEqualization:
            frame = self.applyHistogramEqualization(frame)
        if self.isFrameCLAHEYUV:
            frame = self.applyCLAHEYUV(frame)
        if self.isFrameHistogramEqualizationYUV:
            frame = self.applyHistogramEqualizationYUV(frame)
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
        return self.frameProcessor(self._frame)

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
    def invertFrame(frame):
        """
        Applica l'effetto negativo al frame.
        :param frame: Frame da trasformare.
        :return: Frame con effetto negativo.
        """
        return cv2.bitwise_not(frame)

    @staticmethod
    def autoScreenFrame(image):
        """
        Automatically creates a screen frame.
        """
        inv1 = cv2.bitwise_not(image)
        mult = cv2.multiply(inv1, inv1, scale=1.0 / 255.0)
        return cv2.bitwise_not(mult).astype(np.uint8)

    @staticmethod
    def getRGBChannels(frame):
        """
        Returns the RGB channels of a frame.
        """
        return cv2.split(frame)

    @staticmethod
    def setRGBChannels(channels):
        """
        Sets the RGB channels of a frame.
        """
        return cv2.merge(channels)

    @staticmethod
    def applyGammaByLut(image, gamma):
        inv_gamma = 1.0 / gamma
        table = np.array([(i / 255.0) ** inv_gamma * 255
                          for i in range(256)]).astype(np.uint8)
        return cv2.LUT(image, table)

    @staticmethod
    def applyCLAHE(image, clip_limit=2.0, tile_grid_size=(8, 8)):
        """
        Applies the Contrast Limited Adaptive Histogram Equalization (CLAHE) to the image.
        """
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        return clahe.apply(image)

    @staticmethod
    def applyHistogramEqualization(image):
        """
        Applies the Histogram Equalization to the image.
        """
        return cv2.equalizeHist(image)

    @staticmethod
    def applyCLAHEYUV(image, clip_limit=2.0, tile_grid_size=(8, 8)):
        """
        Applies the Contrast Limited Adaptive Histogram Equalization (CLAHE) to the Y channel of the YUV image.
        """
        yuv_img = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        yuv_img[:, :, 0] = clahe.apply(yuv_img[:, :, 0])
        return cv2.cvtColor(yuv_img, cv2.COLOR_YUV2BGR)

    @staticmethod
    def applyHistogramEqualizationYUV(image):
        """
        Applies the Histogram Equalization to the Y channel of the YUV image.
        """
        yuv_img = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        yuv_img[:, :, 0] = cv2.equalizeHist(yuv_img[:, :, 0])
        return cv2.cvtColor(yuv_img, cv2.COLOR_YUV2BGR)

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

    def play(self):
        """
        Metodo play per la compatibilità con il VideoPlayerObject.
        """
        pass

    def setGammaCorrection(self, value):
        """
        Imposta il valore di correzione gamma.
        :param value: Valore della correzione gamma.
        """
        self.gamma = value

    def stop(self):
        """
        Ferma il frame processor se è in esecuzione. Inizialmente avevo pensato di usare un thread
        per il frame processor, poi poi varie propve ho deciso di non usarlo, preferendo solo metodi che non
        inficiassero la performance.

        Stops the frame processor if it is running. Initially I thought of using a thread
        for the frame processor, then after various tests I decided not to use it, preferring only methods that do not
        affect performance.
        """
        try:
            if hasattr(self, 'frame_processor') and self.frame_processor.isRunning():
                self.frame_processor.stop()
        except RuntimeError as e:
            print(f"Error stopping frame processor: {e}")

