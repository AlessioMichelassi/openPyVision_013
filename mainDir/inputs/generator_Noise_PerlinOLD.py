import os
import numpy as np
import cv2
from PyQt6.QtCore import QSize
from mainDir.inputs.baseClass import BaseClass


class PerlinNoiseImageGenerator(BaseClass):
    noiseCacheDir = "perlinNoise_cache_OLD"

    def __init__(self, synchObject, resolution=QSize(1920, 1080), res=(8, 8), num_noise_images=10):
        super().__init__(synchObject, resolution)
        self.res = res
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

    def fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def lerp(self, t, a, b):
        return a + t * (b - a)

    def generate_perlin_noise_2d(self, shape, res):
        delta = (res[0] / shape[0], res[1] / shape[1])
        grid = np.mgrid[0:res[0]:delta[0], 0:res[1]:delta[1]].transpose(1, 2, 0) % 1

        gradients = np.random.randn(res[0] + 1, res[1] + 1, 2)
        gradients /= np.linalg.norm(gradients, axis=2, keepdims=True)

        d = (shape[0] // res[0], shape[1] // res[1])
        g00 = gradients[0:-1, 0:-1].repeat(d[0], axis=0).repeat(d[1], axis=1)
        g10 = gradients[1:, 0:-1].repeat(d[0], axis=0).repeat(d[1], axis=1)
        g01 = gradients[0:-1, 1:].repeat(d[0], axis=0).repeat(d[1], axis=1)
        g11 = gradients[1:, 1:].repeat(d[0], axis=0).repeat(d[1], axis=1)

        n00 = np.sum(np.dstack([grid[:, :, 0], grid[:, :, 1]]) * g00, 2)
        n10 = np.sum(np.dstack([grid[:, :, 0] - 1, grid[:, :, 1]]) * g10, 2)
        n01 = np.sum(np.dstack([grid[:, :, 0], grid[:, :, 1] - 1]) * g01, 2)
        n11 = np.sum(np.dstack([grid[:, :, 0] - 1, grid[:, :, 1] - 1]) * g11, 2)

        t = self.fade(grid)
        noise = np.sqrt(2) * self.lerp(t[:, :, 1],
                                       self.lerp(t[:, :, 0], n00, n10),
                                       self.lerp(t[:, :, 0], n01, n11))
        return noise

    def generate_noise_cache(self, num_images):
        height, width = self.resolution.height(), self.resolution.width()
        new_noise_cache = []
        for index in range(num_images):
            noise = self.generate_perlin_noise_2d((height, width), self.res)
            noise_normalized = ((noise - noise.min()) / (noise.max() - noise.min()) * 255).astype(np.uint8)
            noise_bgr = cv2.cvtColor(noise_normalized, cv2.COLOR_GRAY2BGR)
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

    def captureFrame(self):
        self.generate_noise()
        self.updateFps()

    def getFrame(self):
        return self._frame
