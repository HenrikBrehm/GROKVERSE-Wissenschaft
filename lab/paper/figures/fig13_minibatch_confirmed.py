"""Figure 13 (short paper Section 6, proposed main-text Figure 4): the two confirmed minibatch blocks, drawn only from the frozen
summaries (no pilot data). (a) L0: Delta_pow per fresh seed at the end of the budget under i.i.d. minibatches of 256 and 64
(10 seeds), mean with the frozen 95 % CI. (b) N54b: mean persistence pi(t) after a switch at step t, per batch size, lr 1e-3
(solid) and 2e-3 (dashed); 0.5 marks the half-point. (c) N54b: half-point t_1/2 per seed against steps per epoch N/B (log-log),
with the frozen mean slopes alpha. Session 50. Pure file reading, no training.

Reads lab/confirm/L0_summary.json and lab/confirm/N54B_summary.json.
  python lab/paper/figures/fig13_minibatch_confirmed.py          # real data -> fig13_minibatch_confirmed.png/.svg
  python lab/paper/figures/fig13_minibatch_confirmed.py --demo   # synthetic numbers, writes only to a temp dir (code check)
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
CONF = HERE.parents[1] / "confirm"
C1, C2, C3, INK, MUTED, SURFACE, GRID = "#2a78d6", "#eb6834", "#1f9e89", "#0b0b0b", "#52514e", "#fcfcfb", "#d9d8d3"
BATCH_COL = {"1024": C1, "256": C3, "64": C2}
LRS = (("0.001", "lr 1e-3", "-", "o"), ("0.002", "lr 2e-3", "--", "^"))


def style(a: plt.Axes) -> None:
    a.set_facecolor(SURFACE)
    a.grid(color=GRID, linewidth=0.6)
    a.set_axisbelow(True)
    for side in ("top", "right"):
        a.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        a.spines[side].set_color(MUTED)
    a.tick_params(colors=MUTED, labelsize=7.5)


def ticks(a: plt.Axes, axis: str, vals: list) -> None:
    """Plain tick labels on a log axis (no minor scientific-notation labels)."""
    from matplotlib.ticker import FixedLocator, NullLocator, ScalarFormatter
    ax_ = a.xaxis if axis == "x" else a.yaxis
    ax_.set_major_locator(FixedLocator(vals))
    ax_.set_major_formatter(ScalarFormatter())
    ax_.set_minor_locator(NullLocator())


def plot(l0: dict, nb: dict, out_dir: Path, note: str = "") -> None:
    rng = np.random.default_rng(13)
    fig, (ax, bx, cx) = plt.subplots(1, 3, figsize=(10.2, 3.5), gridspec_kw={"width_ratios": [1, 1.6, 1.6]}, facecolor=SURFACE)
    for a in (ax, bx, cx):
        style(a)
    # (a) L0 confirmation
    rows = [r for r in l0["rows"] if not r.get("technical")]
    for j, (hk, arm, lab) in enumerate((("H1", "iid256", "batch 256"), ("H2", "iid64", "batch 64"))):
        v = np.array([r[f"dpow_{arm}"] for r in rows], float)
        h = l0["hypotheses"][hk]
        ax.scatter(j + rng.uniform(-0.08, 0.08, len(v)), v, s=9, color=C1, alpha=0.7, zorder=2)
        lo, hi = h["ci95"]
        ax.errorbar(j + 0.22, h["mean"], yerr=[[h["mean"] - lo], [hi - h["mean"]]], fmt="o", color=INK, markersize=4, capsize=3, zorder=3)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.set_xlim(-0.5, 1.6)
    ax.set_xticks([0, 1], ["batch 256", "batch 64"], fontsize=7.5, color=INK)
    ax.set_ylabel(r"steering $\Delta_{pow}$ (end of budget)", fontsize=8.5, color=INK)
    ax.set_title(f"(a) L0, {len(rows)} fresh seeds", fontsize=8.5, color=INK, loc="left")
    # (b) mean pi(t) per batch and lr
    for lr, lrlab, ls, _ in LRS:
        pm = nb["secondary"][f"lr{lr}"]["pi_mean"]
        for b, col in BATCH_COL.items():
            ts = sorted(pm[b], key=float)
            bx.plot([float(t) for t in ts], [pm[b][t] for t in ts], ls, color=col, marker="o", markersize=2.5, linewidth=1.2)
    bx.axhline(0.5, color=MUTED, linewidth=0.8, linestyle=":")
    bx.set_xscale("log")
    ticks(bx, "x", [20, 50, 100, 200, 450])
    bx.set_xlabel("switch step t", fontsize=8.5, color=INK)
    bx.set_ylabel(r"persistence $\pi(t)$ (mean over seeds)", fontsize=8.5, color=INK)
    bx.set_title("(b) N54b: switch after t steps", fontsize=8.5, color=INK, loc="left")
    from matplotlib.lines import Line2D
    keys = [Line2D([], [], color=c, linewidth=1.5, label=f"batch {b}") for b, c in BATCH_COL.items()]
    keys += [Line2D([], [], color=INK, linestyle=ls, linewidth=1.0, label=lab) for _, lab, ls, _ in LRS]
    bx.legend(handles=keys, fontsize=6.3, frameon=False, loc="upper left")
    # (c) t_half per seed against N/B
    for lr, lrlab, ls, mk in LRS:
        rs = nb["rows"][lr]
        n_train = rs[0]["n_train"]
        for b, col in BATCH_COL.items():
            x = n_train / int(b)
            th = [r["th"][b] for r in rs if not r["cens"][b]]
            cx.scatter(x * np.exp(rng.uniform(-0.04, 0.04, len(th))), th, s=9, color=col, marker=mk, alpha=0.6, zorder=2)
        xs = np.array([n_train / int(b) for b in BATCH_COL])
        tm = [nb["secondary"][f"lr{lr}"]["t_half_mean"][b] for b in BATCH_COL]
        al = nb["secondary"][f"lr{lr}"]["alpha"]
        cx.plot(xs, tm, ls, color=INK, linewidth=1.0,
                label=rf"{lrlab}: $\alpha$ = {al['mean']:.2f} [{al['ci95'][0]:.2f}, {al['ci95'][1]:.2f}]")
    cx.set_xscale("log")
    cx.set_yscale("log")
    ticks(cx, "x", [round(3831 / b, 2) for b in (1024, 256, 64)])
    ticks(cx, "y", [30, 60, 100, 200, 300])
    cx.set_xlabel("steps per epoch N/B", fontsize=8.5, color=INK)
    cx.set_ylabel(r"half-point $t_{1/2}$ (steps)", fontsize=8.5, color=INK)
    cx.set_title("(c) N54b: lock-in half-point, 10 fresh seeds", fontsize=8.5, color=INK, loc="left")
    cx.legend(fontsize=6.5, frameon=False, loc="upper left")
    if note:
        fig.suptitle(note, fontsize=8, color=MUTED)
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(out_dir / f"fig13_minibatch_confirmed.{ext}", dpi=200, facecolor=SURFACE)


def demo() -> tuple[dict, dict]:
    rng = np.random.default_rng(0)
    l0 = {"rows": [{"seed": s, "dpow_iid256": 9 + rng.normal(), "dpow_iid64": 9 + rng.normal()} for s in range(10)],
          "hypotheses": {"H1": {"mean": 9.0, "ci95": [8.5, 9.5]}, "H2": {"mean": 9.0, "ci95": [8.5, 9.5]}}}
    grid = {"1024": [20, 40, 60, 120], "256": [40, 80, 150, 250], "64": [100, 200, 300, 450]}
    nb = {"rows": {}, "secondary": {}}
    for lr in ("0.001", "0.002"):
        nb["rows"][lr] = [{"n_train": 3831, "th": {b: 30.0 * (3831 / int(b)) ** 0.55 * rng.uniform(0.8, 1.2) for b in grid},
                           "cens": {b: False for b in grid}} for _ in range(10)]
        nb["secondary"][f"lr{lr}"] = {"pi_mean": {b: {str(t): min(1.0, t / grid[b][-1]) for t in ts} for b, ts in grid.items()},
                                      "t_half_mean": {b: 30.0 * (3831 / int(b)) ** 0.55 for b in grid},
                                      "alpha": {"mean": 0.55, "ci95": [0.5, 0.6]}}
    return l0, nb


def main() -> None:
    if sys.argv[1:] == ["--demo"]:
        with tempfile.TemporaryDirectory() as tmp:
            plot(*demo(), Path(tmp), "DEMO (synthetic numbers)")
            print("[fig13] demo ok (nothing written to the repo)")
        return
    l0 = json.loads((CONF / "L0_summary.json").read_text(encoding="utf-8"))
    nb = json.loads((CONF / "N54B_summary.json").read_text(encoding="utf-8"))
    plot(l0, nb, HERE)
    print("[fig13] written")


if __name__ == "__main__":
    main()
