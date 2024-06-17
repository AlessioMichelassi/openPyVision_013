import numpy as np
import cv2
from PyQt6.QtCore import QSize
from mainDir.inputs.baseClass import BaseClass


class GrainNoiseImageGenerator(BaseClass):
    def __init__(self, synchObject, resolution=QSize(1920, 1080), grain_size=3, r_speed=2, g_speed=1, b_speed=3):
        super().__init__(synchObject, resolution)
        self.grain_size = grain_size
        self.r_speed = r_speed
        self.g_speed = g_speed
        self.b_speed = b_speed
        self.r_offset = 2
        self.g_offset = 0
        self.b_offset = 4
        self._frame = self.generate_noise()

    def generate_noise(self):
        height, width = self.resolution.height(), self.resolution.width()
        grain_shape = (height // self.grain_size, width // self.grain_size)

        r_noise = np.random.randint(10, 200, grain_shape, dtype=np.uint8)
        g_noise = np.random.randint(10, 200, grain_shape, dtype=np.uint8)
        b_noise = np.random.randint(10, 200, grain_shape, dtype=np.uint8)

        r_noise = np.kron(r_noise, np.ones((self.grain_size, self.grain_size), dtype=np.uint8))
        g_noise = np.kron(g_noise, np.ones((self.grain_size, self.grain_size), dtype=np.uint8))
        b_noise = np.kron(b_noise, np.ones((self.grain_size, self.grain_size), dtype=np.uint8))

        r_noise = np.roll(r_noise, self.r_offset, axis=1)
        g_noise = np.roll(g_noise, self.g_offset, axis=0)
        b_noise = np.roll(b_noise, self.b_offset, axis=0)

        grain_noise = np.dstack((b_noise, g_noise, r_noise))

        self._frame = grain_noise

        self.r_offset = (self.r_offset + self.r_speed) % width
        self.g_offset = (self.g_offset + self.g_speed) % height
        self.b_offset = (self.b_offset + self.b_speed) % height
        return grain_noise

    def stop(self):
        super().stop()

    def capture_frame(self):
        self._frame = self.generate_noise()
        self.update_fps()

    def getFrame(self):
        return self._frame
