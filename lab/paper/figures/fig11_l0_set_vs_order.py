"""Figure 11 (draft, short paper Section 6): L0 set composition vs data order under minibatch (pilot EXP-100; later the L0
confirmation). Left: Delta_pow at the end of the budget per seed and arm (full batch 2000 / 30 000 steps, i.i.d. minibatch 256 / 64,
SGD with momentum, stride order), mean with 95 % bootstrap CI. Right: share of the embedding energy on the stride-order
frequencies O = {11, 12, 22, 23, 34, 45}, i.i.d. vs stride, for the engineered splits (F/G mean) and the random split R; chance 6/56.
Reads lab/experiments/EXP-100-set-vs-order/summary.json (analyze.py output). Drawn from the pilot data (session 46/47); the
bootstrap CIs are the figure's own (rng 11) and can differ slightly from the text's.
  python lab/paper/figures/fig11_l0_set_vs_order.py            # real data -> fig11_l0_set_vs_order.png/.svg
  python lab/paper/figures/fig11_l0_set_vs_order.py --demo     # synthetic numbers, writes only to a temp dir (code check)
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
LAB = HERE.parents[1]
C1, C2, INK, MUTED, SURFACE, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#fcfcfb", "#d9d8d3"
ARMS = (("fb", "full batch\n2000"), ("fb30k", "full batch\n30 000"), ("iid256", "minibatch\n256"), ("iid64", "minibatch\n64"),
        ("sgdm256", "SGD+mom.\n256"), ("stride256", "stride order\n256"))
CHANCE_O = 6 / 56
EN = {"Menge steuert unter Minibatch": "yes (pilot, 8 seeds)",   # s47: English title from the pre-fixed German readings
      "Konflikt nicht pruefbar (Reihenfolge wirkt nicht)": "not testable (order has no effect)"}


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


def demo_rows() -> list[dict]:
    rng = np.random.default_rng(0)
    rows = []
    for s in range(8):
        r = {"seed": s, "valid": True}
        for arm, _ in ARMS:
            r[f"dpow_end_{arm}"] = 6 + rng.normal(0, 1)
            r[f"o_{arm}"] = CHANCE_O + rng.normal(0, 0.01)
        r["R_o_iid256"], r["R_o_stride256"] = CHANCE_O + rng.normal(0, 0.01), CHANCE_O + 0.05 + rng.normal(0, 0.01)
        rows.append(r)
    return rows


def plot(rows: list[dict], out_dir: Path, reading: str = "") -> None:
    ok = [r for r in rows if r.get("valid")]
    rng = np.random.default_rng(11)
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(8.8, 3.8), gridspec_kw={"width_ratios": [3, 1.4]}, facecolor=SURFACE)
    style(ax)
    style(bx)
    for j, (arm, _) in enumerate(ARMS):
        v = np.array([r[f"dpow_end_{arm}"] for r in ok if f"dpow_end_{arm}" in r], float)
        if not len(v):
            ax.text(j, 0.5, "not\nevaluable", ha="center", va="bottom", fontsize=7, color=MUTED)   # s47: SGD arm dropped (calibration)
            continue
        col = MUTED if arm.startswith("fb") else (C2 if arm == "stride256" else C1)
        ax.scatter(j + rng.uniform(-0.08, 0.08, len(v)), v, s=9, color=col, alpha=0.7, zorder=2)
        lo, hi = boot_ci(v, rng)
        ax.errorbar(j + 0.2, v.mean(), yerr=[[v.mean() - lo], [hi - v.mean()]], fmt="o", color=INK, markersize=4, capsize=3, zorder=3)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.set_xticks(range(len(ARMS)), [lab for _, lab in ARMS], fontsize=7.2, color=INK)
    ax.set_ylabel(r"steering $\Delta_{pow}$ (end of budget)", fontsize=8.5, color=INK)
    if reading:
        ax.set_title(reading, fontsize=8, color=MUTED, loc="left")
    pairs = (("F/G", [r.get("o_iid256") for r in ok], [r.get("o_stride256") for r in ok]),
             ("R", [r.get("R_o_iid256") for r in ok], [r.get("R_o_stride256") for r in ok]))
    for k, (lab, a, b) in enumerate(pairs):
        a2 = [x for x, y in zip(a, b) if x is not None and y is not None]
        b2 = [y for x, y in zip(a, b) if x is not None and y is not None]
        for x, y in zip(a2, b2):
            bx.plot([2 * k, 2 * k + 1], [x, y], color=GRID, linewidth=0.7)
        bx.scatter([2 * k] * len(a2), a2, s=9, color=C1)
        bx.scatter([2 * k + 1] * len(b2), b2, s=9, color=C2)
    bx.axhline(CHANCE_O, color=MUTED, linewidth=0.8, linestyle=":")
    bx.set_xticks([0, 1, 2, 3], ["F/G\ni.i.d.", "F/G\nstride", "R\ni.i.d.", "R\nstride"], fontsize=7.2, color=INK)
    bx.set_ylabel("energy share on order frequencies O", fontsize=8.5, color=INK)
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(out_dir / f"fig11_l0_set_vs_order.{ext}", dpi=200, facecolor=SURFACE)


def main() -> None:
    if sys.argv[1:] == ["--demo"]:
        with tempfile.TemporaryDirectory() as tmp:
            plot(demo_rows(), Path(tmp), "DEMO (synthetic numbers)")
            print("[fig11] demo ok (nothing written to the repo)")
        return
    summ = json.loads((LAB / "experiments/EXP-100-set-vs-order/summary.json").read_text(encoding="utf-8"))
    p = summ["primary"]
    plot(summ["rows"], HERE, f"set steers under minibatch: {EN.get(p.get('K2_MB'), p.get('K2_MB'))}; "
                             f"conflict test: {EN.get(p.get('Konflikt'), p.get('Konflikt'))}")
    print("[fig11] written")


if __name__ == "__main__":
    main()
