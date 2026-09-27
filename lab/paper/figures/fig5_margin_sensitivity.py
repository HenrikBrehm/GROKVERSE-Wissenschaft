"""Figure 5 (draft): K2-function - margin sensitivity D (drop along own targets minus mean drop along four control sets, equal-norm W_E
step 0.02 ||X||) per seed and seed mean with 95 % bootstrap CI, from the frozen summaries P2d (c0cd65f, add 113, 4000 steps) and P2e
(3c484ef, mul 113 and add 97, 8000 steps). Blocks differ in step budget and seeds; compare magnitudes only qualitatively. Limit (EXP-068):
the sensitivity follows the energy distribution in W_E. Output: fig5_margin_sensitivity.png/.svg.
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


def main() -> None:
    d = json.loads((LAB / "confirm/P2d_summary.json").read_text(encoding="utf-8"))
    e = json.loads((LAB / "confirm/P2e_summary.json").read_text(encoding="utf-8"))
    arms = [("add mod 113 (P2d, 4000 steps)", [r["D"] for r in d["rows"] if not r.get("technical")], d["mean"], d["ci95"]),
            ("mul mod 113 (P2e, 8000 steps)", [r["D"] for r in e["rows"]["mul113"] if not r.get("technical")],
             e["tasks"]["mul113"]["mean"], e["tasks"]["mul113"]["ci95"]),
            ("add mod 97 (P2e, 8000 steps)", [r["D"] for r in e["rows"]["add97"] if not r.get("technical")],
             e["tasks"]["add97"]["mean"], e["tasks"]["add97"]["ci95"])]
    for _, v, m, _ in arms:
        assert abs(np.mean(v) - m) < 1e-9, "per-seed values do not reproduce the frozen mean"
    fig, ax = plt.subplots(figsize=(5.4, 2.8), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    rng = np.random.default_rng(5)
    for y, (name, v, m, ci) in enumerate(arms):
        ax.plot(v, y + rng.uniform(-0.15, 0.15, len(v)), "o", color=SERIES, alpha=0.35, markersize=4, markeredgewidth=0)
        ax.hlines(y, ci[0], ci[1], color=SERIES, linewidth=2, zorder=3)
        ax.plot([m], [y], "D", color=SERIES, markersize=7, markeredgewidth=0, zorder=4)
        ax.annotate(f"{m:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]", (m, y), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=7, color=MUTED)
    ax.axvline(0, color=MUTED, linewidth=1)
    ax.set_yticks(range(len(arms)), [a[0] for a in arms], fontsize=7.5, color=INK)
    ax.invert_yaxis()
    ax.set_xlabel("D: extra margin drop along own targets vs controls (logits)", fontsize=8.5, color=INK)
    ax.set_title("Margin sensitivity along the steered frequencies (20 fresh seeds per task)", fontsize=9, color=INK, loc="right")
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=7.5)
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(HERE / f"fig5_margin_sensitivity.{ext}", dpi=200, facecolor=SURFACE)
    print("[fig5] written", flush=True)


if __name__ == "__main__":
    main()
