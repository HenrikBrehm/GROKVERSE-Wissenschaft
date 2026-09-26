"""Unit check for rfm.py: analytic Jacobian (as used in agop) vs finite differences; frequency
measure on a circulant matrix. Run through guarded_run.py."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rfm  # noqa: E402


def test_jacobian() -> None:
    rng = np.random.default_rng(0)
    n, d, o = 7, 5, 3
    X = rng.normal(size=(n, d))
    A = rng.normal(size=(d, d))
    M = A @ A.T / d
    al = rng.normal(size=(n, o))
    x = X[2]
    f = lambda z: rfm.kernel(z[None], X, M) @ al          # noqa: E731
    eps = 1e-6
    Jfd = np.stack([(f(x + eps * np.eye(d)[j]) - f(x - eps * np.eye(d)[j]))[0] / (2 * eps) for j in range(d)], 1)
    Kb = rfm.kernel(x[None], X, M)
    Ka = Kb @ al
    Jan = -(Ka[:, :, None] * (x[None] @ M)[:, None, :]
            - np.tensordot(Kb[:, :, None] * al[None], X @ M, axes=([1], [0]))) / rfm.L2
    assert np.abs(Jfd - Jan[0]).max() < 1e-6, np.abs(Jfd - Jan[0]).max()


def test_freq_power_circulant() -> None:
    a = np.arange(rfm.P)
    C = np.cos(2 * np.pi * 7 * (a[:, None] - a[None, :]) / rfm.P)       # circulant, frequency 7
    pw = rfm.freq_power_block(C)
    assert int(np.argmax(pw)) + 1 == 7 and pw[6] > 0.99 * pw.sum()


if __name__ == "__main__":
    test_jacobian(); print("ok test_jacobian")
    test_freq_power_circulant(); print("ok test_freq_power_circulant")
