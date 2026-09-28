"""Figure 12 (draft, EXPLORATION, post hoc on seen data; appendix candidate, not a confirmed result): R1 steering size over
time. Left: Delta_pow (seed means) of the four R1 lr/wd cells (15 seeds each) and the P1 preset (50 seeds) against optimizer
steps. Right: the same against t * lr * wd in preset units (tau). Only points with tau <= 2000 are available for the cells
(the preset stops at 2000). Registered reading of the post hoc: "partial" (misfit at tau < 250, where the preset is only
known at steps 0 and 250; dashed segment). Reads only lab/confirm/R1_posthoc_lrwd_time_s44.json.
Output: fig12_r1_lrwd_time.png/.svg.
  python lab/paper/figures/fig12_r1_lrwd_time.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
INK, MUTED, SURFACE, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#d9d8d3"
CELLS = {"lr5e-4": ("lr 5e-4", "#8fb7ea", "o"), "lr2e-3": ("lr 2e-3", "#2a78d6", "o"),
         "wd0.3": ("wd 0.3", "#f4a57f", "s"), "wd3": ("wd 3", "#eb6834", "s")}


def main() -> None:
    d = json.loads((LAB / "confirm/R1_posthoc_lrwd_time_s44.json").read_text(encoding="utf-8"))
    pre = sorted((int(k), v) for k, v in d["preset_curve"].items())
    assert pre[0] == (0, 0.0) and abs(pre[-1][1] - 8.236) < 1e-3
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.4), facecolor=SURFACE, sharey=True)
    for ax, key, xlabel in ((axes[0], "t", "optimizer steps t"), (axes[1], "tau", "t · lr · wd  (preset units)")):
        ax.set_facecolor(SURFACE)
        ax.grid(color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(MUTED)
        ax.plot([s for s, _ in pre[1:]], [v for _, v in pre[1:]], color=INK, linewidth=1.6, label="preset (P1, n = 50)", zorder=3)
        ax.plot([0, 250], [0, pre[1][1]], color=INK, linewidth=1.0, linestyle="--", zorder=3)
        for cell, (lab, col, mk) in CELLS.items():
            rows = d["cells"][cell]
            ax.plot([r[key] for r in rows], [r["cell_mean"] for r in rows], color=col, marker=mk, markersize=3.5,
                    linewidth=1.0, label=f"{lab} (n = 15)", zorder=2)
        ax.set_xlim(0, 2100)
        ax.set_xlabel(xlabel, fontsize=8.5, color=INK)
        ax.tick_params(colors=MUTED, labelsize=7.5)
    axes[0].set_ylabel("Δ_pow (seed mean)", fontsize=8.5, color=INK)
    axes[0].legend(fontsize=7, frameon=False, loc="upper left")
    m = d["mean_abs_log_ratio"]
    axes[1].text(0.98, 0.03, f"mean |log ratio| to preset: {m['tau']:.3f} (τ) vs {m['steps']:.3f} (steps)\n"
                 "post hoc, exploration; dashed: preset interpolated", transform=axes[1].transAxes, ha="right", va="bottom",
                 fontsize=6.8, color=MUTED)
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(HERE / f"fig12_r1_lrwd_time.{ext}", dpi=200, facecolor=SURFACE)
    print("[fig12] written")


if __name__ == "__main__":
    main()
