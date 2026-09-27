"""Figure 7 (draft, EXPLORATION with a prediction fixed before the runs, section 4): EXP-084 dose curve.
x: realised M0 power share of the split on its 5 targets; y: time to the trainer's generalization event (test >= 0.95), log scale,
censored at 4000 (drawn as open markers at the cap). One point per run (10 fresh units x 8 arms). Lines: the two models whose
predictions were committed before any run (prediction_s32.json, commit 6d0231f): M_share b = T_inf + A/(s - s0) and M_eps
(log b linear in log eps, drawn at each arm's median share). Output: fig7_dose_curve.png/.svg.
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
OBS, SHARE, EPS, INK, MUTED, SURFACE, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#fcfcfb", "#d9d8d3"
ARMS = ("R", "e0.5", "e1", "e2", "e4", "e8", "e16", "e32")
CAP = 4000


def main() -> None:
    summ = json.loads((LAB / "experiments/EXP-084-dose-curve/summary.json").read_text(encoding="utf-8"))
    pred = json.loads((LAB / "experiments/EXP-084-dose-curve/prediction_s32.json").read_text(encoding="utf-8"))
    p = pred["m_share_params"]
    xs, ys, obs = [], [], []
    for r in summ["rows"]:
        for a in ARMS:
            xs.append(r[a]["m0_target_share"]); ys.append(r[a]["b"]); obs.append(r[a]["observed"])
    xs, ys, obs = np.array(xs), np.array(ys, float), np.array(obs)
    fig, ax = plt.subplots(figsize=(5.2, 3.6), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.scatter(xs[obs], ys[obs], s=22, color=OBS, zorder=3, label="runs (10 fresh units × 8 arms)")
    ax.scatter(xs[~obs], ys[~obs], s=22, facecolors="none", edgecolors=OBS, zorder=3, label=f"no event by {CAP} (censored)")
    s = np.linspace(p["s0"] + 0.012, 0.45, 300)
    ax.plot(s, np.minimum(p["T_inf"] + p["A"] / (s - p["s0"]), CAP), color=SHARE, linewidth=2, label="M_share, fixed before the runs")
    em = [(pred["per_arm"][a]["share_median"], pred["per_arm"][a]["M_eps_b"]) for a in ARMS if a != "R"]
    ax.plot([e[0] for e in em], [e[1] for e in em], "--", color=EPS, linewidth=2, marker="D", markersize=5, label="M_eps, fixed before the runs")
    ax.set_yscale("log")
    ax.set_xlabel("realised mask power share on the 5 targets (M0)", fontsize=8.5, color=INK)
    ax.set_ylabel("steps to generalization (log)", fontsize=8.5, color=INK)
    ax.set_title("Speed-up saturates with the pair spectrum (EXP-084, pilot)", fontsize=9, color=INK, loc="left")
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=7.5)
    ax.legend(fontsize=6.8, frameon=False, loc="upper right")
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(HERE / f"fig7_dose_curve.{ext}", dpi=200, facecolor=SURFACE)
    print("[fig7] written", int(obs.sum()), "observed of", len(obs), flush=True)


if __name__ == "__main__":
    main()
