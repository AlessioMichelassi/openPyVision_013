import cv2
import noise
import numpy as np

shape = (1080, 1920)
scale = 100.0
octaves = 6
persistence = 0.5
lacunarity = 2.0

world = np.zeros(shape)
for i in range(shape[0]):
    for j in range(shape[1]):
        world[i][j] = noise.pnoise2(i / scale,
                                    j / scale,
                                    octaves=octaves,
                                    persistence=persistence,
                                    lacunarity=lacunarity,
                                    repeatx=1024,
                                    repeaty=1024,
                                    base=0)

world = (world + 1) / 2
world = np.uint8(world * 255)
world = np.stack((world, world, world), axis=2)

cv2.imshow('Perlin Noise', world)
cv2.waitKey(0)