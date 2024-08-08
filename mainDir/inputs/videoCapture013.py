import sys
import time

import cv2
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.inputs.baseClass import BaseClass
from mainDir.inputs.synchObject import SynchObject
from mainDir.inputs.deviceProperties.deviceUpdaterThread import DeviceUpdater

"""
La classe VideoCapture è una sottoclasse di BaseClass e rappresenta un'entità che cattura i frame da una sorgente video
usa la libreria OpenCV per catturare i frame da una webcam o da una scheda di acquisizione. OpenCV non ha un sistema per
ottenere il nome della periferica, quindi si usa ffmpeg per ottenere le informazioni sui dispositivi. Queste informazioni 
vengono reperite usando la classe DeviceUpdater, che è un thread che esegue un comando ffmpeg per ottenere le informazioni
sui dispositivi audio e video disponibili. Se il dispositivo è noto, perchè ad esempio è stato già selezionato da una combo
box, tipo quella di matrixWidget si può passare il dizionario altrimenti il dizionario viene calcolato automaticamente.

Il dizionario serve per sapere se il dispositivo è una webcam o una scheda di acquisizione. Mentre il dispositivo di 
acquisizione ha generalmente un'interfaccia grafica creata dal produttore per impostare i parametri di acquisizione,
la web cam non li ha. Se la webcam è un pò datata, potrebbe fra l'altro non supportare l'acquisizione con con driver
diversi da DShow (quindi non ha una latenza ottimizzata). In alternativa si può usare forceDShow=True per forzare l'uso 
di Dshow e saltare la ricerca dei dispositivi.


"""


class VideoCapture013(BaseClass):
    needResizing = False

    def __init__(self, synchObject, cameraIndex=0, deviceDictionary=None, forceDShow=False,
                 resolution=QSize(1920, 1080)):
        super().__init__(synchObject, resolution)
        self.cameraIndex = cameraIndex
        self.target_resolution = (resolution.height(), resolution.width())
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)
        self.camera = None
        if not forceDShow:
            if deviceDictionary is None:
                self.devices_dictionary = {}
                self.updater = DeviceUpdater()
                self.updater.finished.connect(self.update_devices)
                self.updater.start()
            else:
                self.devices_dictionary = deviceDictionary
                self.initCamera(cameraIndex)
        else:
            self.initCamera(cameraIndex, cv2.CAP_DSHOW)

    def update_devices(self, devices):
        print(f"Devices: {devices}")
        self.devices_dictionary = devices
        for key in self.devices_dictionary.keys():
            if key == self.cameraIndex:
                print(f"Camera {self.cameraIndex} found")
                if self.devices_dictionary[self.cameraIndex]['video']:
                    if "webcam" in self.devices_dictionary[self.cameraIndex]['name'].lower():
                        print(f"Initializing webcam {self.cameraIndex}")
                        self.initCamera(self.cameraIndex, cv2.CAP_DSHOW)
                        self.set_camera_properties()
                    self.initCamera(self.cameraIndex)

    def initCamera(self, cameraIndex, api=cv2.CAP_ANY):
        self.camera = cv2.VideoCapture(cameraIndex, api)

    def openDefaultSettingsInterface(self):
        self.camera.set(cv2.CAP_PROP_SETTINGS, 1)

    def set_camera_properties(self):
        success = True
        # Imposta la risoluzione e il frame rate, se possibile
        if not self.camera.set(cv2.CAP_PROP_FPS, 60):
            print("Failed to set FPS to 60")
            success = False
        if not self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_resolution[1]):
            print(f"Failed to set frame width to {self.target_resolution[1]}")
            success = False
        if not self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_resolution[0]):
            print(f"Failed to set frame height to {self.target_resolution[0]}")
            success = False

        if success:
            print(f"Camera properties set to {self.target_resolution[1]}x{self.target_resolution[0]} at 60 FPS")
        else:
            print("Failed to set one or more camera properties")

    def stop(self):
        super().stop()
        # No specific resources to release for ColorGenerator

    def captureFrame(self):
        if self.camera:

            frame_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            frame_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            if frame_width != self.target_resolution[1] or frame_height != self.target_resolution[0]:
                self._frame = cv2.resize(self.camera.read()[1], self.target_resolution, interpolation=cv2.INTER_AREA)
            else:
                self._frame = self.camera.read()[1]

        self.updateFps()

    def getFrame(self):
        return self._frame



