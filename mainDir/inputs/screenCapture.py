
import cv2
import dxcam
import numpy as np
from PyQt6.QtCore import *
from mainDir.inputs.baseClass import BaseClass


# Questa classe gestisce la cattura dello schermo
class ScreenCapture(BaseClass):

    def __init__(self, synchObject, screen_index, resolution=QSize(1920, 1080), region=None, targetFps=60):
        super(ScreenCapture, self).__init__(synchObject, resolution)
        self.targetFps = targetFps  # FPS target per la cattura dello schermo
        self.screenIndex = screen_index  # Indice dello schermo da catturare
        self.target_resolution = (resolution.width(), resolution.height())  # Risoluzione target per il frame
        self.region = region  # Regione dello schermo da catturare (opzionale)
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)  # Frame iniziale vuoto
        self.camera = None  # Oggetto camera
        self.needs_resize = False  # Flag per indicare se è necessario ridimensionare il frame
        self.initCamera(screen_index)  # Inizializza la camera

    def initCamera(self, screen_index):
        # Inizializza la camera per catturare lo schermo
        try:
            screens = dxcam.device_info()  # Ottiene le informazioni sugli schermi disponibili
            print(f"Available screens: {screens}")
            if screen_index >= len(screens):
                raise IndexError(f"Screen index {screen_index} out of range. Available screens: {len(screens)}")
            self.camera = dxcam.create(output_idx=screen_index, output_color="BGR", max_buffer_len=512)
            self.camera.start(target_fps=self.targetFps, video_mode=True)
            self.synch_Object.synch_SIGNAL.connect(self.capture_frame)
            QTimer.singleShot(1000, self.checkSize)  # Controlla la dimensione del frame dopo 1 secondo
        except Exception as e:
            print(f"Failed to open screen source {screen_index}: {e}")
            try:
                self.camera = dxcam.create(output_idx=0, output_color="BGR", max_buffer_len=512)
                self.camera.start(target_fps=self.targetFps, video_mode=True)
                self.synch_Object.synch_SIGNAL.connect(self.capture_frame)
                QTimer.singleShot(1000, self.checkSize)
            except Exception as e:
                print(f"Failed to fallback to screen source 0: {e}")

    def checkSize(self):
        # Controlla se il frame deve essere ridimensionato
        if self.camera:
            frame = self.camera.get_latest_frame()
            if frame is not None:
                if frame.shape[:2] != (1080, 1920):  # Controlla solo l'altezza e la larghezza
                    print("Resizing frame")
                    self.needs_resize = True
                else:
                    print("No resizing needed")
        else:
            print("Camera not initialized")

    def __del__(self):
        # Pulisce le risorse quando l'oggetto viene distrutto
        self.stop()

    def stop(self):
        # Ferma la cattura dello schermo e rilascia le risorse
        if self.camera:
            try:
                self.camera.stop()
            except Exception as e:
                print(f"Error releasing camera: {e}")
            self.camera = None
        super().stop()

    def capture_frame(self):
        # Cattura un frame dallo schermo
        self.update_fps()
        if self.camera:
            frame = self.camera.get_latest_frame()
            if frame is not None:
                if self.needs_resize:
                    frame = cv2.resize(frame, self.target_resolution)
                self._frame = frame
        else:
            print("Camera not initialized")

    def getFrame(self):
        # Restituisce il frame processato
        return self.frameProcessor(self._frame)



