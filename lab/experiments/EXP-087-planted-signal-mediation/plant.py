"""EXP-087: additive W_E interventions applied right after the (unchanged) init.

Pure numpy, no torch RNG consumed, so data order and all other weights stay identical to the baseline run.

plant_delta:  sum_k alpha * (b_cos_k u_k^T + b_sin_k v_k^T) on the number rows W_E[:p], with b_* the orthonormal
              DFT columns of ``fourier_basis`` and u_k, v_k random unit vectors from an own stream (not the init seed).
              The delta has power exactly 2 alpha^2 at each target frequency and 0 elsewhere (incl. DC).
              alpha = sqrt(c * median_k P0(k) / 2): the planted delta alone carries c times the median init power.
noise_delta:  norm control R+N: a random zero-mean (over numbers) matrix with the same Frobenius norm as the plant
              delta, spread over all frequencies.
Written in session 39 (2026-09-28) before any EXP-087 run; not yet wired into freq_ban.py (trainer locked by R4).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "EXP-001-freq-ban"))
from freq_ban import fourier_basis, freq_columns, freq_power  # noqa: E402

PLANT_SALT = 8700   # stream key (PLANT_SALT, seed, kind); kind 0 = plant directions, 1 = noise


def alpha_for(W0: np.ndarray, c: float) -> float:
    if not (np.isfinite(c) and c > 0):
        raise ValueError("plant multiplier c must be finite and > 0")
    p = W0.shape[0]
    return float(np.sqrt(c * np.median(freq_power(W0, fourier_basis(p))) / 2))


def _unit(rng: np.random.Generator, d: int) -> np.ndarray:
    x = rng.standard_normal(d)
    return x / np.linalg.norm(x)


def plant_delta(W0: np.ndarray, freqs: list[int], c: float, seed: int) -> np.ndarray:
    p, d = W0.shape
    K = (p - 1) // 2
    if not freqs or len(set(freqs)) != len(freqs) or min(freqs) < 1 or max(freqs) > K:
        raise ValueError(f"plant targets must be distinct in 1..{K}")
    basis = fourier_basis(p)
    alpha = alpha_for(W0, c)
    rng = np.random.default_rng([PLANT_SALT, seed, 0])
    delta = np.zeros((p, d))
    for k in sorted(freqs):
        ccol, scol = freq_columns([k])
        delta += alpha * (np.outer(basis[:, ccol], _unit(rng, d)) + np.outer(basis[:, scol], _unit(rng, d)))
    return delta


def noise_delta(W0: np.ndarray, norm: float, seed: int) -> np.ndarray:
    p, d = W0.shape
    x = np.random.default_rng([PLANT_SALT, seed, 1]).standard_normal((p, d))
    x -= x.mean(axis=0, keepdims=True)
    return x * (norm / np.linalg.norm(x))


def selftest() -> None:
    rng = np.random.default_rng(0)
    p, d = 113, 128
    W0 = rng.standard_normal((p, d)) * 0.1
    basis = fourier_basis(p)
    tg = [3, 17, 40, 41, 55]
    dl = plant_delta(W0, tg, 2.0, seed=5)
    pw = freq_power(dl, basis)
    a = alpha_for(W0, 2.0)
    assert np.allclose(pw[[k - 1 for k in tg]], 2 * a * a), "target power != 2 alpha^2"
    assert np.allclose(np.delete(pw, [k - 1 for k in tg]), 0, atol=1e-20), "power leaked to other frequencies"
    assert np.allclose(dl.mean(axis=0), 0, atol=1e-12), "plant changed the DC part"
    assert np.isclose(pw[tg[0] - 1], 2.0 * np.median(freq_power(W0, basis))), "c * median calibration wrong"
    assert np.array_equal(dl, plant_delta(W0, tg, 2.0, seed=5)), "not deterministic"
    assert not np.allclose(dl, plant_delta(W0, tg, 2.0, seed=6)), "seed does not change directions"
    nz = noise_delta(W0, np.linalg.norm(dl), seed=5)
    assert np.isclose(np.linalg.norm(nz), np.linalg.norm(dl)) and np.allclose(nz.mean(axis=0), 0, atol=1e-12)
    pn = freq_power(nz, basis)
    assert pn[[k - 1 for k in tg]].sum() / pn.sum() < 0.3, "noise concentrated on targets"
    for bad in ([], [0], [57], [3, 3]):
        try:
            plant_delta(W0, bad, 1.0, 0)
        except ValueError:
            continue
        raise AssertionError(f"accepted bad targets {bad}")
    print("[plant] selftest ok")


if __name__ == "__main__":
    selftest()
