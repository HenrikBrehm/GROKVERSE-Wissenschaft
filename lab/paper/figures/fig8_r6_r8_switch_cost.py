"""Figure 8 (draft, CONFIRMED blocks, section 3.8): the time signature of the lock-in on fresh seeds. add mod 113, GPU.
Left: R6 (manifest 5b2bca6, 30 seeds 2800-2829): switch cost C(t) = per-seed mean over both directions of log2 b(switch at t) -
log2 b(destination split only), b = first test accuracy >= 0.95 bounded at 2000 steps from step 0; mean with 95 % bootstrap CI over
seeds; below, the median persistence pi(t) of the same runs (R6 summary). Right: R8 (manifest d79f97d, 25 seeds 3100-3124): per-seed
cost of a switch at t = 25 to other targets (C_AB) and to the same targets with new pairs (C_AA2), lines join the two values of a seed.
Reads only the frozen summaries (R6_summary.json, R8_summary.json). Output: fig8_r6_r8_switch_cost.png/.svg.
  python lab/paper/figures/fig8_r6_r8_switch_cost.py
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
C1, C2, INK, MUTED, SURFACE, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#fcfcfb", "#d9d8d3"   # palette slots 1, 2


def boot_ci(v: np.ndarray, rng: np.random.Generator, n: int = 10000) -> tuple[float, float]:
    m = rng.choice(v, (n, len(v)), replace=True).mean(1)
    return float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))


def style(a: plt.Axes) -> None:
    a.set_facecolor(SURFACE)
    a.grid(axis="y", color=GRID, linewidth=0.6)
    a.set_axisbelow(True)
    for side in ("top", "right"):
        a.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        a.spines[side].set_color(MUTED)
    a.tick_params(colors=MUTED, labelsize=7.5)


def main() -> None:
    r6 = json.loads((LAB / "confirm/R6_summary.json").read_text(encoding="utf-8"))
    r8 = json.loads((LAB / "confirm/R8_summary.json").read_text(encoding="utf-8"))
    assert r6["n_valid"] == r6["n_planned"] == 30 and r8["result"]["n_valid"] == r8["n_planned"] == 25
    ts = sorted(int(t) for t in r6["secondary"]["mean_C"])
    rows6 = [r for r in r6["rows"] if r["valid"]]
    rng = np.random.default_rng(37)
    C = {t: np.array([r["C"][str(t)] for r in rows6]) for t in ts}
    mean = np.array([C[t].mean() for t in ts])
    assert np.allclose(mean, [r6["secondary"]["mean_C"][str(t)] for t in ts])
    ci = np.array([boot_ci(C[t], rng) for t in ts])
    pi = np.array([r6["secondary"]["median_pi"][str(t)] for t in ts])
    rows8 = [r for r in r8["rows"] if r["valid"]]
    cab, caa = np.array([r["C_AB"] for r in rows8]), np.array([r["C_AA2"] for r in rows8])

    fig = plt.figure(figsize=(8.4, 4.6), facecolor=SURFACE)
    gs = fig.add_gridspec(2, 2, width_ratios=[3, 2], height_ratios=[3, 2], wspace=0.32, hspace=0.12)
    ax, bx, cx = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[:, 1])
    for a in (ax, bx, cx):
        style(a)

    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.fill_between(ts, ci[:, 0], ci[:, 1], color=C1, alpha=0.18, linewidth=0)
    ax.plot(ts, mean, color=C1, linewidth=2, marker="o", markersize=5, markeredgecolor=SURFACE, markeredgewidth=1.5)
    ax.set_ylabel("switch cost C(t) [log2]", color=INK, fontsize=8)
    ax.set_title("R6: a switch at step t delays grokking (30 fresh seeds)", color=INK, fontsize=8.5, loc="left")
    ax.tick_params(labelbottom=False)
    bx.axhline(0.5, color=GRID, linewidth=0.8, linestyle="--")
    bx.plot(ts, pi, color=MUTED, linewidth=2, marker="o", markersize=4)
    bx.set_ylabel("median π(t)", color=INK, fontsize=8)
    bx.set_xlabel("switch step t", color=INK, fontsize=8)
    bx.set_xticks(ts)
    ax.set_xticks(ts)

    for a_, b_ in zip(cab, caa):
        cx.plot([0, 1], [a_, b_], color=GRID, linewidth=0.8, zorder=1)
    cx.scatter(np.zeros_like(cab), cab, s=28, color=C2, edgecolor=SURFACE, linewidth=1.5, zorder=3)
    cx.scatter(np.ones_like(caa), caa, s=28, color=C1, edgecolor=SURFACE, linewidth=1.5, zorder=3)
    cx.axhline(0, color=MUTED, linewidth=0.8)
    cx.set_xticks([0, 1], ["other targets\n(A→B)", "same targets,\nnew pairs (A→A2)"], fontsize=7.5, color=INK)
    cx.set_xlim(-0.4, 1.4)
    cx.set_ylabel("switch cost at t = 25 [log2]", color=INK, fontsize=8)
    d = r8["result"]["H1"]
    cx.set_title(f"R8: only a change of targets costs\nD = +{d['mean']:.2f} [{d['ci95'][0]:.2f}, {d['ci95'][1]:.2f}], "
                 f"{d['n_positive']}/25 seeds", color=INK, fontsize=8.5, loc="left")
    for ext in ("png", "svg"):
        fig.savefig(HERE / f"fig8_r6_r8_switch_cost.{ext}", dpi=200, bbox_inches="tight", facecolor=SURFACE)
    print("[fig8] written")


if __name__ == "__main__":
    main()
