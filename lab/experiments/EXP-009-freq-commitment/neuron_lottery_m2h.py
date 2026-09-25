"""EXP-009 exploratory (post hoc): per-neuron frequency lottery in the two-hot MLP (m2h).

For each hidden neuron j, spectrum of its a-token input weights W_in[:p, j] at step 0 and 25k.
Neurons with a dominant final frequency (share > 0.5): does the final frequency rank high in the
SAME neuron's init spectrum? Chance: normalized rank 0.5, argmax match 1/56.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

from commitment import GROUPS, N_FREQ, SEEDS

HERE = Path(__file__).resolve().parent
P, DOMINANT_SHARE = 113, 0.5


def neuron_spectra(run_dir: Path, step: int) -> np.ndarray:
    sd = torch.load(run_dir / f"ckpt_step{step:06d}.pt", weights_only=True, map_location="cpu")
    w = sd["W_in"][:P].double().numpy()
    return (np.abs(np.fft.rfft(w, axis=0)) ** 2)[1:N_FREQ + 1]      # (56, d_mlp)


def main() -> None:
    out = []
    for s in SEEDS:
        d = Path(str(GROUPS["m2h"]).format(s=s))
        f0, f1 = neuron_spectra(d, 0), neuron_spectra(d, 25_000)
        keep = f1.max(0) / f1.sum(0) > DOMINANT_SHARE
        fin = f1.argmax(0)
        match = float((f0.argmax(0) == fin)[keep].mean())
        rank = (f0 > f0[fin, np.arange(f0.shape[1])]).sum(0)[keep] / (N_FREQ - 1)
        out.append({"seed": s, "n_dominant": int(keep.sum()), "argmax_match": match,
                    "mean_norm_init_rank": float(rank.mean())})
        print(out[-1])
    (HERE / "neuron_lottery_m2h.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
