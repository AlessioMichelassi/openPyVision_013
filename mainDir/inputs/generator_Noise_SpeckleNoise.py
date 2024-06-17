import os
import numpy as np
import cv2
from PyQt6.QtCore import QSize
from mainDir.inputs.baseClass import BaseClass


class SpeckleNoiseImageGenerator(BaseClass):
    noiseCacheDir = "speckle_noise_cache"
    """il rumore speckle è una forma di rumore che può essere modellata usando il rumore gaussiano. Il rumore speckle 
    è comunemente osservato nelle immagini radar e nelle immagini acquisite tramite ultrasuoni. Viene generato 
    moltiplicando ogni pixel dell'immagine da un valore casuale generato da una distribuzione gaussiana, il che crea 
    un effetto di granulosità o speckle.

Nel contesto del codice che hai condiviso, viene utilizzato un rumore gaussiano per simulare il rumore speckle. Il 
rumore viene aggiunto all'immagine originale e il risultato è normalizzato per garantire che i valori dei pixel siano 
compresi tra 0 e 255.
"""

    def __init__(self, synchObject, resolution=QSize(1920, 1080), num_noise_images=10):
        super().__init__(synchObject, resolution)
        self.num_noise_images = num_noise_images
        self.noise_cache = []
        self.current_index = 0

        # Create noise cache directory if it doesn't exist
        os.makedirs(self.noiseCacheDir, exist_ok=True)
        self.load_noise_cache()
        if len(self.noise_cache) < self.num_noise_images:
            self.noise_cache.extend(self.generate_noise_cache(self.num_noise_images - len(self.noise_cache)))

        self.generate_noise()

    def load_noise_cache(self):
        cache_files = sorted([f for f in os.listdir(self.noiseCacheDir) if f.endswith('.png')])
        for file in cache_files:
            img = cv2.imread(os.path.join(self.noiseCacheDir, file))
            if img is not None:
                self.noise_cache.append(img)

    def save_noise_to_cache(self, noise_bgr, index):
        cv2.imwrite(f"{self.noiseCacheDir}/noise_{index}.png", noise_bgr)

    def generate_noise_image(self):
        height, width = self.resolution.height(), self.resolution.width()

        # Create a blank image with all pixels set to 1
        image = np.ones((height, width, 3), dtype=np.float32)

        # Add speckle noise
        noise = np.random.normal(0, 1, (height, width, 3))  # Gaussian noise
        speckle_noise = image + image * noise

        # Normalize the image to the range [0, 255]
        speckle_noise = cv2.normalize(speckle_noise, None, 0, 255, cv2.NORM_MINMAX)
        speckle_noise = speckle_noise.astype(np.uint8)

        return speckle_noise

    def generate_noise_cache(self, num_images):
        new_noise_cache = []
        for index in range(num_images):
            noise_bgr = self.generate_noise_image()
            self.save_noise_to_cache(noise_bgr, len(self.noise_cache) + index)
            new_noise_cache.append(noise_bgr)
        return new_noise_cache

    def generate_noise(self):
        if len(self.noise_cache) == 0:
            self._frame = np.zeros((self.resolution.height(), self.resolution.width(), 3), dtype=np.uint8)
        else:
            if self.current_index >= len(self.noise_cache):
                self.current_index = 0
            self._frame = self.noise_cache[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.noise_cache)

    def stop(self):
        super().stop()

    def capture_frame(self):
        self.generate_noise()
        self.update_fps()

    def getFrame(self):
        return self._frame
