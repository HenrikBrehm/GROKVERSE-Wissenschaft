"""Main-text Figure 1 of the short paper (session 45): the two-part figure announced in draft_short ("Abbildungen"):
(a) mask spectrum M0 vs learned W_E power for one engineered split (EXP-016 seed 10, pilot data; same data and code path as
fig1_mask_vs_learned.py), (b) the pre-registered P1 replication (Delta_pow per task, 95 % CI, from P1_summary.json; as
fig2_p1_delta_pow.py). No numbers are typed by hand; both source figures stay as they are.
  python lab/paper/figures/fig_main1_steering.py
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
sys.path.insert(0, str(HERE))
from fig1_mask_vs_learned import E16, INK, MUTED, OTHER, P, SEED, SERIES, SURFACE, mask_power  # noqa: E402
from fig2_p1_delta_pow import LABELS, LAB, MIN_EFFECT  # noqa: E402


def style(ax: plt.Axes) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=7.5)


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
    s = json.loads((LAB / "confirm" / "P1_summary.json").read_text(encoding="utf-8"))
    tasks = [t for t in LABELS if t in s["tasks"]]

    fig = plt.figure(figsize=(9.6, 3.8), facecolor=SURFACE)
    gs = fig.add_gridspec(2, 2, width_ratios=[3, 2], wspace=0.28, hspace=0.45)
    a1, a2, b = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[:, 1])
    for ax, vals, title in ((a1, m0 / m0.sum(), "(a) mask spectrum M0 of the training pairs (share)"),
                            (a2, learned / learned.sum(), "learned W$_E$ power at step 2000 (share)")):
        style(ax)
        ax.bar(k, vals, width=0.7, color=colors, linewidth=0)
        ax.set_title(title, fontsize=8.5, color=INK, loc="left")
    a2.set_xlabel("frequency k (blue: the five prescribed targets; one pilot split)", fontsize=8, color=INK)

    style(b)
    y = list(range(len(tasks)))[::-1]
    means = [s["tasks"][t]["mean"] for t in tasks]
    ci = [s["tasks"][t]["ci95"] for t in tasks]
    b.hlines(y, [c[0] for c in ci], [c[1] for c in ci], color=SERIES, linewidth=2)
    b.plot(means, y, "o", color=SERIES, markersize=7, markeredgewidth=0, zorder=3)
    for yi, m, t in zip(y, means, tasks):
        b.annotate(f"{m:.2f}  ({s['tasks'][t]['n_positive']}/{s['tasks'][t]['n_valid']} > 0)", (m, yi), xytext=(0, 8),
                   textcoords="offset points", ha="center", fontsize=7.5, color=MUTED)
    b.axvline(MIN_EFFECT, color=MUTED, linestyle="--", linewidth=1)
    b.text(MIN_EFFECT + 0.1, len(tasks) - 0.45, "registered\nminimum effect", fontsize=7, color=MUTED, va="top")
    b.set_yticks(y, [LABELS[t] for t in tasks], color=INK)
    b.set_xlim(0, max(c[1] for c in ci) * 1.15)
    b.set_ylim(-0.6, len(tasks) - 0.3)
    b.set_xlabel("$\\Delta_{pow}$ at step 2000 (natural log)", color=INK, fontsize=8.5)
    b.set_title("(b) pre-registered replication, 50 fresh seeds per task", color=INK, fontsize=8.5, loc="left")
    for ext in ("png", "svg"):
        fig.savefig(HERE / f"fig_main1_steering.{ext}", dpi=200, facecolor=SURFACE, bbox_inches="tight")
    print("[fig_main1] written", flush=True)


if __name__ == "__main__":
    main()
