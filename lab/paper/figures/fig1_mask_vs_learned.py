"""Figure 1 (draft): for one engineered split (EXP-016, seed 10, arm F, add mod 113) the mask spectrum M0 of the training set
(computed from the split file, no weights) and the learned W_E power spectrum at step 2000 (stored run). Two stacked panels on the same
frequency axis (different quantities, no dual axis); the five prescribed target frequencies are marked. Exploration-era data (EXP-016 is a
pilot); the held-out confirmation is Figure 2. Output: fig1_mask_vs_learned.png/.svg.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
from make_split import mask_power  # noqa: E402

SERIES, OTHER, INK, MUTED, SURFACE = "#2a78d6", "#b9b8b1", "#0b0b0b", "#52514e", "#fcfcfb"
E16 = LAB / "experiments/EXP-016-engineered-split"
SEED, P = 10, 113


def main() -> None:
    idx = np.load(E16 / f"splits/split_seed{SEED}_eps2.0.npy")
    T = set(json.loads((E16 / f"splits/split_seed{SEED}_eps2.0.json").read_text(encoding="utf-8"))["targets"])
    run = E16 / f"raw/EXP-016_baseline_seed{SEED}_thr4_split_seed{SEED}_eps2.0"
    res = json.loads((run / "result.json").read_text(encoding="utf-8"))
    assert res["status"] == "completed" and res["steps_completed"] == 2000
    steps = list(np.load(run / "spectra_steps.npy"))
    learned = np.load(run / "spectra.npy")[steps.index(2000)]
    m0 = mask_power(idx, "add", P)
    k = np.arange(1, len(m0) + 1)
    colors = [SERIES if kk in T else OTHER for kk in k]
    fig, axes = plt.subplots(2, 1, figsize=(6.4, 3.8), sharex=True, facecolor=SURFACE)
    for ax, vals, title in ((axes[0], m0 / m0.sum(), "Mask spectrum M0 of the training pairs (share)"),
                            (axes[1], learned / learned.sum(), "Learned W$_E$ power at step 2000 (share)")):
        ax.set_facecolor(SURFACE)
        ax.bar(k, vals, width=0.7, color=colors, linewidth=0)
        ax.set_title(title, fontsize=8.5, color=INK, loc="left")
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(MUTED)
        ax.tick_params(colors=MUTED, labelsize=7.5)
    axes[1].set_xlabel("frequency k (blue: the five prescribed targets of this split)", fontsize=8.5, color=INK)
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(HERE / f"fig1_mask_vs_learned.{ext}", dpi=200, facecolor=SURFACE)
    print("[fig1] written; targets", sorted(T), "top-5 learned", sorted((np.argsort(-learned)[:5] + 1).tolist()), flush=True)


if __name__ == "__main__":
    main()
