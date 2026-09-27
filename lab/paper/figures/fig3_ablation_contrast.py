"""Figure 3 (draft): ablation contrast R = acc(W_E without the NEW targets) - acc(W_E without the OLD targets) after a data switch,
per seed (mean over both switch directions) and seed mean, from the frozen summaries of three confirmation blocks:
N29 (087e042: switch at t = 25 vs 50), N29b (db31564) and N29c (3c9cb63), both with the switch at t = 50: no reset / attention or MLP reset (N29b), no reset / W_Q,W_K or W_V,W_O reset (N29c).
R > 0: the final model relies on the OLD frequencies. Blocks use different fresh seeds; compare within a block only. Output: fig3_ablation_contrast.png/.svg.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
SERIES, INK, MUTED, SURFACE, GRID = "#2a78d6", "#0b0b0b", "#52514e", "#fcfcfb", "#d9d8d3"


def rows(block: str) -> list[dict]:
    s = json.loads((LAB / "confirm" / f"{block}_summary.json").read_text(encoding="utf-8"))
    return [r for r in s["rows"] if not r.get("technical")]


def main() -> None:
    n29, n29b, n29c = rows("N29"), rows("N29b"), rows("N29c")
    arms = [("N29", "switch at 25", [r["new25"] - r["old25"] for r in n29]),
            ("N29", "switch at 50", [r["new50"] - r["old50"] for r in n29]),
            ("N29b", "no reset", [r["R_normal"] for r in n29b]),
            ("N29b", "MLP reset", [r["R_rsmlp"] for r in n29b]),
            ("N29b", "attention reset", [r["R_rsattn"] for r in n29b]),
            ("N29c", "no reset", [r["R_normal"] for r in n29c]),
            ("N29c", "W_Q,W_K reset", [r["R_rsqk"] for r in n29c]),
            ("N29c", "W_V,W_O reset", [r["R_rsvo"] for r in n29c])]
    fig, ax = plt.subplots(figsize=(6.4, 4.4), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    rng = np.random.default_rng(3)
    ys, labels, prev = [], [], None
    y = 0.0
    for block, name, vals in arms:
        if prev is not None and block != prev:
            y += 0.6                                              # gap between blocks
        ys.append(y)
        labels.append(f"{block} · {name}")
        v = np.asarray(vals, dtype=float)
        ax.plot(v, y + rng.uniform(-0.18, 0.18, len(v)), "o", color=SERIES, alpha=0.35, markersize=4, markeredgewidth=0)
        ax.plot([v.mean()], [y], "D", color=SERIES, markersize=8, markeredgewidth=0, zorder=3)
        ax.annotate(f"{v.mean():+.2f}", (v.mean(), y), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=7, color=MUTED)
        prev, y = block, y + 1.0
    ax.axvline(0, color=MUTED, linewidth=1)
    ax.set_yticks(ys, labels, fontsize=7.5, color=INK)
    ax.invert_yaxis()
    ax.set_xlim(-1.05, 1.05)
    ax.set_xlabel("R = acc(without new targets) − acc(without old targets)\nR > 0: final model relies on the old frequencies", color=INK, fontsize=8.5)
    ax.set_title("Ablation contrast after a switch (dots: 20 seeds per arm; diamond: mean)", color=INK, fontsize=9, loc="right")
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=7.5)
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(HERE / f"fig3_ablation_contrast.{ext}", dpi=200, facecolor=SURFACE)
    print("[fig3] written", flush=True)


if __name__ == "__main__":
    main()
