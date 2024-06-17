import numpy as np
import matplotlib.pyplot as plt


def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)


def lerp(t, a, b):
    return a + t * (b - a)


def grad(hash, x, y, z):
    h = hash & 15
    u = x if h < 8 else y
    v = y if h < 4 else (x if h in (12, 14) else z)
    return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)


def generate_perlin_noise_2d(shape, res):
    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    grid = np.mgrid[0:res[0]:delta[0], 0:res[1]:delta[1]].transpose(1, 2, 0) % 1
    gradients = np.random.randn(res[0] + 1, res[1] + 1, 2)
    gradients /= np.linalg.norm(gradients, axis=2, keepdims=True)

    g00 = gradients[0:-1, 0:-1].repeat(d[0], axis=0).repeat(d[1], axis=1)
    g10 = gradients[1:, 0:-1].repeat(d[0], axis=0).repeat(d[1], axis=1)
    g01 = gradients[0:-1, 1:].repeat(d[0], axis=0).repeat(d[1], axis=1)
    g11 = gradients[1:, 1:].repeat(d[0], axis=0).repeat(d[1], axis=1)

    n00 = np.sum(np.dstack([grid[:, :, 0], grid[:, :, 1]]) * g00, 2)
    n10 = np.sum(np.dstack([grid[:, :, 0] - 1, grid[:, :, 1]]) * g10, 2)
    n01 = np.sum(np.dstack([grid[:, :, 0], grid[:, :, 1] - 1]) * g01, 2)
    n11 = np.sum(np.dstack([grid[:, :, 0] - 1, grid[:, :, 1] - 1]) * g11, 2)

    t = fade(grid)
    return np.sqrt(2) * lerp(t[:, :, 1], lerp(t[:, :, 0], n00, n10), lerp(t[:, :, 0], n01, n11))


shape = (1920, 1080)
res = (20, 20)

noise = generate_perlin_noise_2d(shape, res)

plt.imshow(noise, cmap='gray')
plt.colorbar()
plt.title("Perlin Noise")
plt.show()
