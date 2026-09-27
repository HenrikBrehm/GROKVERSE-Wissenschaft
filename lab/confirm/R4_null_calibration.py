"""R4 null calibration (session 30, before any R4 run): similarity of W_E power spectra between study runs that share neither init nor split
(seeds 0-9 of training/runs/txf_add_p113_wd1.0_frac0.3_seed{s}_arch25k, 45 pairs) at steps 0, 2000, 8000, with the R4 measures.
Sets the R4 MDEs (about 1/3 of the null SD) and the choice of cosine only after grokking. Only loads stored checkpoints (no training).

  python lab/confirm/R4_null_calibration.py
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lab" / "tools"))
from confirm_r4 import MEASURES, N_FREQ, P, PAIRS, PRIMARY  # noqa: E402

RUN = ROOT / "training/runs/txf_add_p113_wd1.0_frac0.3_seed{s}_arch25k/ckpt_step{t:06d}.pt"


def power(W: np.ndarray) -> np.ndarray:
    t = np.arange(P)
    B = np.concatenate([np.stack([np.cos(2 * np.pi * k * t / P), np.sin(2 * np.pi * k * t / P)], 1) for k in range(1, N_FREQ + 1)], 1)
    B /= np.linalg.norm(B, axis=0)
    return ((B.T @ W) ** 2).reshape(N_FREQ, 2, -1).sum(axis=(1, 2))


def load_we(s: int, t: int) -> np.ndarray:
    ck = torch.load(str(RUN).format(s=s, t=t), map_location="cpu", weights_only=False)
    sd = ck.get("model", ck)
    sd = sd.get("model_state", sd)
    return sd["W_E"].numpy().astype(np.float64)[:P]


def main() -> None:
    for t in (0, 2000, 8000):
        S = {s: power(load_we(s, t)) for s in range(10)}
        for name, f in MEASURES.items():
            v = np.array([f(S[a], S[b]) for a, b in itertools.combinations(range(10), 2)])
            print(f"step {t:5d} {name:4s} mean {v.mean():+.3f} sd {v.std(ddof=1):.3f}")
        # Codex recheck s30: SD of the crossed-design UNIT statistic under the null. Four unrelated runs fill the four cells
        # (init index, split index); Delta = mean(split pairs) - mean(none pairs), over all ordered 4-tuples of the 10 runs
        # (overlapping, so this is a resampling estimate, not 5040 independent units).
        for name, f in MEASURES.items():
            d = []
            for q in itertools.permutations(range(10), 4):
                cell = dict(zip([(0, 0), (0, 1), (1, 0), (1, 1)], q))
                sim = {k: np.mean([f(S[cell[a]], S[cell[b]]) for a, b in pp]) for k, pp in PAIRS.items()}
                d.append(sim["split"] - sim["none"])
            d = np.array(d)
            print(f"step {t:5d} {name:4s} unit-Delta null: mean {d.mean():+.4f} sd {d.std(ddof=1):.3f}")


if __name__ == "__main__":
    main()
