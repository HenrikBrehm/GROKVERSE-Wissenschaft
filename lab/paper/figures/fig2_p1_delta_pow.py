"""Figure 2 (draft): K2 held-out replication P1 - Delta_pow per task with 95 % bootstrap CI, from the frozen summary
lab/confirm/P1_summary.json (manifest 733e829). No numbers are typed by hand. Output: fig2_p1_delta_pow.png/.svg next to this script.
Dashed line: the registered minimum effect (Delta_pow = 1).
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
SERIES, INK, MUTED, SURFACE = "#2a78d6", "#0b0b0b", "#52514e", "#fcfcfb"   # dataviz reference palette (slot 1, text, surface)
LABELS = {"add113": "add mod 113", "mul113": "mul mod 113", "add97": "add mod 97", "D59": "D$_{59}$"}
MIN_EFFECT = 1.0


def main() -> None:
    s = json.loads((LAB / "confirm" / "P1_summary.json").read_text(encoding="utf-8"))
    tasks = [t for t in LABELS if t in s["tasks"]]
    means = [s["tasks"][t]["mean"] for t in tasks]
    ci = [s["tasks"][t]["ci95"] for t in tasks]
    fig, ax = plt.subplots(figsize=(4.8, 3.0), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    y = list(range(len(tasks)))[::-1]
    ax.hlines(y, [c[0] for c in ci], [c[1] for c in ci], color=SERIES, linewidth=2)
    ax.plot(means, y, "o", color=SERIES, markersize=8, markeredgewidth=0, zorder=3)
    for yi, m, t in zip(y, means, tasks):
        ax.annotate(f"{m:.2f}  ({s['tasks'][t]['n_positive']}/{s['tasks'][t]['n_valid']} > 0)", (m, yi), xytext=(0, 9),
                    textcoords="offset points", ha="center", fontsize=8, color=MUTED)
    ax.axvline(MIN_EFFECT, color=MUTED, linestyle="--", linewidth=1)
    ax.text(MIN_EFFECT + 0.1, len(tasks) - 0.45, "registered\nminimum effect", fontsize=7, color=MUTED, va="top")
    ax.set_yticks(y, [LABELS[t] for t in tasks], color=INK)
    ax.set_xlim(0, max(c[1] for c in ci) * 1.12)
    ax.set_ylim(-0.6, len(tasks) - 0.3)
    ax.set_xlabel("$\\Delta_{pow}$: target vs. comparison W$_E$ energy (step 2000)", color=INK, fontsize=9)
    ax.set_title("P1: held-out replication, 50 fresh seeds per task", color=INK, fontsize=9, loc="left")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(HERE / f"fig2_p1_delta_pow.{ext}", dpi=200, facecolor=SURFACE)
    print("[fig2] written", flush=True)


if __name__ == "__main__":
    main()
