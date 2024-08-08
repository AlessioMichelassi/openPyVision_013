import os
import random

import numpy as np
import cv2
import threading
from PyQt6.QtCore import QSize
from mainDir.inputs.baseClass import BaseClass
import noise


class PerlinNoiseImageGenerator(BaseClass):
    noiseCacheDir = "noise_cache"

    def __init__(self, synchObject, resolution=QSize(1920, 1080), res=(8, 8), num_noise_images=10, min_ready_frames=2,
                 max_cache_size=100, scale=100.0, octaves=6, persistence=0.5, lacunarity=2.0):
        super().__init__(synchObject, resolution)
        self.res = res
        self.num_noise_images = num_noise_images
        self.min_ready_frames = min_ready_frames
        self.max_cache_size = max_cache_size
        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
        self.noise_cache = []
        self.current_index = 0
        self.generating_noise = True
        self.stop_thread = False

        # Create noise cache directory if it doesn't exist
        os.makedirs(self.noiseCacheDir, exist_ok=True)
        self.load_noise_cache()

        self.noise_generation_thread = threading.Thread(target=self.generate_noise_cache)
        self.noise_generation_thread.start()

    def load_noise_cache(self):
        cache_files = sorted([f for f in os.listdir(self.noiseCacheDir) if f.endswith('.png')])
        for file in cache_files:
            img = cv2.imread(os.path.join(self.noiseCacheDir, file))
            if img is not None:
                self.noise_cache.append(img)
        if len(self.noise_cache) >= self.min_ready_frames:
            self.generating_noise = False

    def generate_perlin_noise_2d(self, shape, octaves=6, persistence=0.5, lacunarity=2.0, repeatx=1024, repeaty=1024,
                                 base=0):
        height, width = shape
        world = np.zeros((height, width))
        for i in range(height):
            for j in range(width):
                world[i][j] = noise.pnoise2(i / self.scale,
                                            j / self.scale,
                                            octaves=octaves,
                                            persistence=persistence,
                                            lacunarity=lacunarity,
                                            repeatx=repeatx,
                                            repeaty=repeatx,
                                            base=base)
        world = (world + 1) / 2
        return world

    def generate_noise_cache(self):
        while len(self.noise_cache) < self.max_cache_size and not self.stop_thread:
            noise_img = self.generate_perlin_noise_2d((self.resolution.height(), self.resolution.width()),
                                                      base=random.randint(0, 6))
            noise_normalized = (noise_img * 255).astype(np.uint8)
            noise_bgr = cv2.cvtColor(noise_normalized, cv2.COLOR_GRAY2BGR)
            self.noise_cache.append(noise_bgr)
            cv2.imwrite(f"{self.noiseCacheDir}/noise_{len(self.noise_cache)}.png", noise_bgr)
            if len(self.noise_cache) >= self.min_ready_frames:
                self.generating_noise = False

    def generate_noise(self):
        if len(self.noise_cache) >= self.min_ready_frames:
            self._frame = self.noise_cache[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.noise_cache)
        else:
            self._frame = np.zeros((self.resolution.height(), self.resolution.width(), 3), dtype=np.uint8)

    def stop(self):
        super().stop()
        self.stop_thread = True
        if self.noise_generation_thread.is_alive() and threading.current_thread() != self.noise_generation_thread:
            self.noise_generation_thread.join()

    def captureFrame(self):
        self.generate_noise()
        self.updateFps()

    def getFrame(self):
        return self._frame

    def __del__(self):
        self.stop()
