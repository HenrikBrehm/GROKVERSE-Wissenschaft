"""Figure 0 (draft, session 30): the setup. (a) Training-pair masks of one P1 seed (add mod 113, seed 1000, manifest 733e829), arranged
by left operand a and output c = a + b mod p: arm R (eps = 0, a uniform random 30 % split) and arm F (eps = 2, five prescribed targets).
(b) Their centred coherent mask spectra M0c (share per frequency; F's targets marked). (c) Schematic of the switch protocol (no data).
Split files only, no training. Output: fig0_setup.png/.svg.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "confirm"))
from P1_posthoc_within import m0c_add  # noqa: E402

SERIES, OTHER, INK, MUTED, SURFACE = "#2a78d6", "#b9b8b1", "#0b0b0b", "#52514e", "#fcfcfb"
SPL, P = LAB / "confirm" / "splits", 113
STEM = "confirm_exp1_eps2.0_add113_seed1000_{arm}"


def mask_ac(idx: np.ndarray) -> np.ndarray:
    """Rows: left operand a; columns: output c = a + b mod p."""
    a, b = idx // P, idx % P
    m = np.zeros((P, P))
    m[a, (a + b) % P] = 1
    return m


def style(ax) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=7)


def main() -> None:
    arms = {}
    for arm in ("R", "F"):
        meta = json.loads((SPL / f"{STEM.format(arm=arm)}.json").read_text(encoding="utf-8"))
        assert meta["manifest_commit"] == "733e829" and meta["n_train"] == 3831
        arms[arm] = (np.load(SPL / f"{STEM.format(arm=arm)}.npy"), meta)
    targets = set(arms["F"][1]["targets"])
    cmap = LinearSegmentedColormap.from_list("mask", [SURFACE, SERIES])
    fig = plt.figure(figsize=(7.0, 6.2), facecolor=SURFACE)
    gs = fig.add_gridspec(3, 2, height_ratios=[2.2, 1.4, 0.8], hspace=0.55, wspace=0.25)
    titles = {"R": "(a) random split (arm R, ε = 0)", "F": "(a) engineered split (arm F, ε = 2)"}
    for col, arm in enumerate(("R", "F")):
        ax = fig.add_subplot(gs[0, col])
        ax.imshow(mask_ac(arms[arm][0]), cmap=cmap, interpolation="nearest", aspect="equal")
        ax.set_title(titles[arm], fontsize=8, color=INK, loc="left")
        ax.set_xlabel("output c = a + b mod 113", fontsize=7.5, color=INK)
        ax.set_ylabel("left operand a", fontsize=7.5, color=INK)
        style(ax)
    k = np.arange(1, (P - 1) // 2 + 1)
    colors = [SERIES if kk in targets else OTHER for kk in k]
    for col, arm in enumerate(("R", "F")):
        ax = fig.add_subplot(gs[1, col])
        m = m0c_add(arms[arm][0], P)
        ax.bar(k, m / m.sum(), width=0.7, color=colors, linewidth=0)
        ax.set_title(f"(b) mask spectrum M0c, arm {arm} (share)", fontsize=8, color=INK, loc="left")
        ax.set_xlabel("frequency k (blue: F's five targets)", fontsize=7.5, color=INK)
        style(ax)
    ax = fig.add_subplot(gs[2, :])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.barh(0.5, 18, left=1, height=0.45, color=SERIES, linewidth=0)
    ax.barh(0.5, 79, left=20, height=0.45, color=OTHER, linewidth=0)
    ax.text(10, 0.5, "split A\nt = 25 or 50 steps", ha="center", va="center", fontsize=6.5, color=SURFACE)
    ax.text(59.5, 0.5, "pair-disjoint split B, 2000 or 4000 further steps (optimizer state kept)", ha="center", va="center",
            fontsize=7, color=INK)
    ax.annotate("switch (reset arms: named tensors back to init,\ntheir AdamW state cleared)", xy=(19.5, 0.25), xytext=(22, -0.35),
                fontsize=6.5, color=MUTED, arrowprops={"arrowstyle": "-", "color": MUTED, "lw": 0.8})
    ax.set_title("(c) switch protocol (both directions A→B and B→A per seed)", fontsize=8, color=INK, loc="left")
    for ext in ("png", "svg"):
        fig.savefig(HERE / f"fig0_setup.{ext}", dpi=200, facecolor=SURFACE, bbox_inches="tight")
    shares = {a: float(m0c_add(arms[a][0], P)[sorted(t - 1 for t in targets)].sum() / m0c_add(arms[a][0], P).sum()) for a in arms}
    print("[fig0] written; F targets", sorted(targets), "M0c target share", {a: round(v, 3) for a, v in shares.items()}, flush=True)


if __name__ == "__main__":
    main()
