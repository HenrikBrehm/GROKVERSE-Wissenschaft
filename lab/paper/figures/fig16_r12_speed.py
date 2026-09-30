"""Figure 16 (draft, CONFIRMATION block R12, manifest 8e6f9b3f; written in session 57 BEFORE any R12 result): does the speed-up of
Result 2 (R5, addition mod 113) carry over to addition mod 97 and multiplication mod 113? Same plot as fig10_r5_speed.py, one panel per
task, 20 fresh units each. Per unit and arm the bounded time b = min(stable event, 8000) (event: test accuracy >= 0.95 at s, s + 25 and
s + 50 after train accuracy >= 0.99); open markers = no event by 8000 (plotted at the bound). Arms: engineered E2 (target sets A and
B), uniform random R, per-output matched controls D (A and B). Lines join the arms of a unit; black bars are medians. The printed ratios
and Holm-adjusted verdicts come from the frozen summary. Reads only R12_summary.json. Output: fig16_r12_speed.png/.svg.
  python lab/paper/figures/fig16_r12_speed.py
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
ARMS = (("E2_0", "E2 (A)"), ("E2_1", "E2 (B)"), ("R", "random R"), ("D_0", "control D (A)"), ("D_1", "control D (B)"))
TASKS = (("add97", "addition mod 97"), ("mul113", "multiplication mod 113"))


def panel(ax: plt.Axes, rows: list[dict], h: dict, title: str, seed: int) -> None:
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
    rng = np.random.default_rng(seed)
    for j, (k, _) in enumerate(ARMS):
        col = C1 if k.startswith("E") else (MUTED if k == "R" else C2)
        t = np.array([r["times"][k][0] for r in rows], float)
        seen = np.array([r["times"][k][1] for r in rows], bool)
        jit = j + rng.uniform(-0.08, 0.08, len(rows))
        ax.scatter(jit[seen], t[seen], s=10, color=col, zorder=2)
        ax.scatter(jit[~seen], t[~seen], s=10, facecolors="none", edgecolors=col, zorder=2)
        ax.plot([j - 0.25, j + 0.25], [np.median(t)] * 2, color=INK, linewidth=1.4, zorder=3)
    ax.set_yscale("log")
    ax.set_ylim(150, 10000)
    ax.set_xticks(x, [lab for _, lab in ARMS], fontsize=7, color=INK)
    ax.tick_params(colors=MUTED, labelsize=7)
    ax.set_title(title, fontsize=8.5, color=INK)
    er, ed = h["H-ER"], h["H-ED"]
    ax.text(0.99, 0.02, f"R / E2(A): x{er['ratio_geo']:.1f} [{er['ratio_ci95'][0]:.1f}, {er['ratio_ci95'][1]:.1f}], {er['verdict']}\n"
            f"D / E2: x{ed['ratio_geo']:.1f} [{ed['ratio_ci95'][0]:.1f}, {ed['ratio_ci95'][1]:.1f}], {ed['verdict']}\n"
            f"n = {len(rows)} units; open markers: no event by 8000",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=6.5, color=MUTED)


def main() -> None:
    s = json.loads((LAB / "confirm/R12_summary.json").read_text(encoding="utf-8"))
    hyp = s["hypotheses"]
    if hyp.get("verdict") == "nicht auswertbar":
        raise SystemExit("R12 is 'nicht auswertbar': no figure")
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9), facecolor=SURFACE, sharey=True)
    for i, (ax, (tn, title)) in enumerate(zip(axes, TASKS)):
        rows = [r for r in s["rows"][tn] if not r.get("technical")]
        assert len(rows) == s["n_planned_per_task"] == 20, (tn, len(rows))
        for key, _ in ARMS:                               # medians must match the frozen descriptive block
            med = float(np.median([min(r["times"][key][0], 8000) for r in rows]))
            assert abs(med - hyp[tn]["descriptive"][key]["median_bounded"]) < 1e-9, (tn, key, med)
        panel(ax, rows, hyp[tn], title, 16 + i)
    axes[0].set_ylabel("steps to stable generalization (bounded at 8000)", fontsize=8.5, color=INK)
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(HERE / f"fig16_r12_speed.{ext}", dpi=200, facecolor=SURFACE)
    print("[fig16] written")


if __name__ == "__main__":
    main()
