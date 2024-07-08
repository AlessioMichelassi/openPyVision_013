import time

import numpy as np


def MMM(A, B):
    C = np.zeros((A.n_rows, B.n_columns))
    for row in range(A.n_rows):
        for col in range(B.n_columns):
            for inner in range(A.n_inner):
                C[row, col] = C[row, col] + A[row, inner] * B[inner, col]
    return C

def gigaFlopCalc(n):
    flop = 2 * n ** 3 - n ** 2
    return flop / 1_000_000_000

x = np.random.randn(1920, 1920).astype(np.float32)
y = np.random.randn(1920, 1920).astype(np.float32)
start = time.time_ns()
z = np.dot(x, y)
end = time.time_ns() - start
print(f"Time: {end} ns - {end / 1_000_000} ms")
print(f"Flops: {gigaFlopCalc(1920)}")
