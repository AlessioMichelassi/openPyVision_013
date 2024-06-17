import os
import numpy as np
import cv2
from PyQt6.QtCore import QSize
from mainDir.inputs.baseClass import BaseClass


class GaussianNoiseImageGenerator(BaseClass):

    def __init__(self, synchObject, resolution=QSize(1920, 1080), num_noise_images=10):
        super().__init__(synchObject, resolution)
        self.num_noise_images = num_noise_images
        self.noise_cache = []
        self.current_index = 0

        if len(self.noise_cache) < self.num_noise_images:
            self.noise_cache.extend(self.generate_noise_cache(self.num_noise_images - len(self.noise_cache)))

        self.generate_noise()

    def generate_noise_image(self):
        height, width = self.resolution.height(), self.resolution.width()
        gauss = np.random.normal(0, 1, (height, width, 3))
        return gauss.reshape(height, width, 3)

    def generate_noise_cache(self, num_images):
        new_noise_cache = []
        for index in range(num_images):
            noise_bgr = self.generate_noise_image()
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
