"""Figure 15 (appendix candidate, N57/EXP-123): two stages before grokking in the Section 2 transformer. Per arm (random R,
count-matched control D_0, engineered E2_0; 20 R5 units each), held-out accuracy on pairs whose mirrored pair (b, a) was trained
(acc_swap, solid) and on the others (acc_other, dashed), against training step divided by the run's generalization step t_gen
(test >= 0.95); thin lines = units, thick = median over units on a common grid. Runs without t_gen are drawn up to their last step
over 8000 and left out of the median. Session 55. Pure file reading (swap_trace.py result.json), no training. Draw the EXP-123 data
only AFTER its frozen analysis (analyze.py) has been run and read.
  python lab/paper/figures/fig15_commutativity_stages.py                       # EXP-123 raw -> fig15_commutativity_stages.png/.svg
  python lab/paper/figures/fig15_commutativity_stages.py --raw DIR --out DIR   # e.g. the smoke run, code check
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
C1, C2, C3, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1f9e89", "#0b0b0b", "#52514e", "#d9d8d3"
ARMS = (("R", "random split R", C2), ("D_0", "count-matched control D", MUTED), ("E2_0", "engineered split E2", C1))
GRIDX = np.linspace(0, 1, 101)


def load(raw: Path, arm: str) -> list[dict]:
    out = []
    for f in sorted(raw.glob(f"u*_{arm}/result.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        out.append({"t": np.array(r["trace"]["step"], float), "swap": np.array(r["trace"]["swap"]),
                    "other": np.array(r["trace"]["other"]), "gen": r["generalization_step"]})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=str(LAB / "experiments/EXP-123-commutativity-stages/raw"))
    ap.add_argument("--out", default=str(HERE))
    a = ap.parse_args()
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4), sharey=True)
    for ax, (arm, label, col) in zip(axes, ARMS):
        runs = load(Path(a.raw), arm)
        med = {"swap": [], "other": []}
        for r in runs:
            x = r["t"] / (r["gen"] if r["gen"] else 8000.0)
            for key, ls in (("swap", "-"), ("other", "--")):
                ax.plot(x, r[key], ls, color=col, lw=0.5, alpha=0.35)
                if r["gen"]:
                    med[key].append(np.interp(GRIDX, x, r[key]))
        for key, ls, nm in (("swap", "-", "mirror trained"), ("other", "--", "no mirror trained")):
            if med[key]:
                ax.plot(GRIDX, np.median(med[key], axis=0), ls, color=INK, lw=2, label=f"median, {nm}")
        n_gen = sum(r["gen"] is not None for r in runs)
        ax.set_title(f"{label} ({n_gen}/{len(runs)} generalized)", fontsize=10, color=INK)
        ax.set_xlim(0, 1.05)
        ax.set_xlabel("training step / generalization step", fontsize=9, color=MUTED)
        ax.grid(color=GRID, lw=0.5)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].set_ylabel("held-out accuracy", fontsize=9, color=MUTED)
    leg = next((ax for ax in axes if ax.get_legend_handles_labels()[0]), None)   # first panel with median lines
    if leg is not None:
        leg.legend(fontsize=8, frameon=False, loc="upper left")
    fig.tight_layout()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(out / f"fig15_commutativity_stages.{ext}", dpi=160)
    print(f"written to {out}")


if __name__ == "__main__":
    main()
