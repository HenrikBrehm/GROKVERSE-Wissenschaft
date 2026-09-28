"""Figure 10 (draft, CONFIRMED block, short paper Result 2): engineered splits generalize earlier (R5, manifest 12a2db4, 20 fresh
units, addition mod 113, GPU). Per unit and arm the bounded time b = min(stable event, 8000) (event: test accuracy >= 0.95 at s,
s + 25 and s + 50 after train accuracy >= 0.99); open markers = no event by 8000 (plotted at the bound). Arms: uniform random split R,
engineered E1, E2 (target sets A and B), E8, and the per-output matched controls D (for A and B). Lines join the arms of a unit.
Geometric-mean ratios of the registered contrasts are printed from the frozen summary. Reads only R5_summary.json.
Output: fig10_r5_speed.png/.svg.
  python lab/paper/figures/fig10_r5_speed.py
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
C1, C2, INK, MUTED, SURFACE, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#fcfcfb", "#d9d8d3"
ARMS = (("E8_0", "E8"), ("E2_0", "E2 (A)"), ("E2_1", "E2 (B)"), ("E1_0", "E1"), ("R", "random R"), ("D_0", "control D (A)"),
        ("D_1", "control D (B)"))


def main() -> None:
    r5 = json.loads((LAB / "confirm/R5_summary.json").read_text(encoding="utf-8"))
    rows = [r for r in r5["rows"] if not r.get("technical")]
    h = r5["hypotheses"]
    assert h["n"] == len(rows) == r5["n_planned"] == 20
    for key, _ in ARMS:                                   # medians must match the frozen descriptive block
        med = float(np.median([r["times"][key][0] for r in rows]))
        assert abs(med - h["descriptive"][key]["median_bounded"]) < 1e-9, (key, med)
    fig, ax = plt.subplots(figsize=(7.6, 3.9), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    x = np.arange(len(ARMS))
    for r in rows:
        ax.plot(x, [r["times"][k][0] for k, _ in ARMS], color=GRID, linewidth=0.7, zorder=1)
    rng = np.random.default_rng(10)
    for j, (k, _) in enumerate(ARMS):
        col = C1 if k.startswith("E") else (MUTED if k == "R" else C2)
        t = np.array([r["times"][k][0] for r in rows], float)
        seen = np.array([r["times"][k][1] for r in rows], bool)
        jit = j + rng.uniform(-0.08, 0.08, len(rows))
        ax.scatter(jit[seen], t[seen], s=10, color=col, zorder=2)
        ax.scatter(jit[~seen], t[~seen], s=10, facecolors="none", edgecolors=col, zorder=2)
        ax.plot([j - 0.25, j + 0.25], [np.median(t)] * 2, color=INK, linewidth=1.4, zorder=3)
    ax.set_yscale("log")
    ax.set_ylim(250, 10000)
    ax.set_xticks(x, [lab for _, lab in ARMS], fontsize=7.5, color=INK)
    ax.tick_params(colors=MUTED, labelsize=7.5)
    ax.set_ylabel("steps to stable generalization (bounded at 8000)", fontsize=8.5, color=INK)
    ax.text(0.99, 0.02, f"R / E2(A): x{h['H-ER']['ratio_geo']:.1f}, D / E2: x{h['H-ED']['ratio_geo']:.1f} (geometric means, 20/20 units)\n"
            "open markers: no event by 8000", transform=ax.transAxes, ha="right", va="bottom", fontsize=7, color=MUTED)
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(HERE / f"fig10_r5_speed.{ext}", dpi=200, facecolor=SURFACE)
    print("[fig10] written")


if __name__ == "__main__":
    main()
