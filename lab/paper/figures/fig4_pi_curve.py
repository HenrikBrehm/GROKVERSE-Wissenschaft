"""Figure 4 (draft): persistence index pi of the first split's frequency choice after a switch to a pair-disjoint split at step t
(2000 further steps), add mod 113. Pilot curve: EXP-059 normal arm, 10 KNOWN seeds (mean +- SD per t; exploration). Confirmed points:
N28 (manifest fa154bd, 30 FRESH seeds): normal switch at t = 25 and t = 50 (seed means, 95 % bootstrap CI over seeds computed here from the
frozen per-seed values). pi is an affinely normalised log-energy index (0 = pure second-split endpoint, 1 = pure first-split endpoint),
not a probability. Confirmed points are drawn 1.2 steps to the right of t only for visibility. Output: fig4_pi_curve.png/.svg.
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
PILOT, CONF, INK, MUTED, SURFACE, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#fcfcfb", "#d9d8d3"   # palette slots 1, 2


def boot_ci(v: np.ndarray, rng: np.random.Generator, n: int = 10000) -> tuple[float, float]:
    m = rng.choice(v, (n, len(v)), replace=True).mean(1)
    return float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))


def main() -> None:
    s59 = json.loads(Path(glob.glob(str(LAB / "experiments/EXP-059-*/summary.json"))[0]).read_text(encoding="utf-8"))
    ts = sorted(int(t) for t in s59["pi_normal_mean"])
    mean = np.array([s59["pi_normal_mean"][str(t)] for t in ts])
    sd = np.array([s59["pi_normal_sd"][str(t)] for t in ts])
    s28 = json.loads((LAB / "confirm/N28_summary.json").read_text(encoding="utf-8"))
    ok = [r for r in s28["rows"] if r.get("valid")]
    rng = np.random.default_rng(4)
    conf = {}
    for t, key in ((25, "normal25"), (50, "normal50")):
        v = np.array([r["pi"][key] for r in ok], dtype=float)
        conf[t] = (float(v.mean()), boot_ci(v, rng), len(v))
    assert abs(conf[25][0] - s28["pi_mean"]["normal25"]) < 1e-9 and abs(conf[50][0] - s28["pi_mean"]["normal50"]) < 1e-9
    fig, ax = plt.subplots(figsize=(5.2, 3.4), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.fill_between(ts, mean - sd, mean + sd, color=PILOT, alpha=0.15, linewidth=0)
    ax.plot(ts, mean, "-o", color=PILOT, linewidth=2, markersize=5, label="pilot EXP-059 (10 known seeds, mean ± SD)")
    for i, t in enumerate((25, 50)):
        m, (lo, hi), n = conf[t]
        ax.errorbar([t + 1.2], [m], yerr=[[m - lo], [hi - m]], fmt="s", color=CONF, markersize=6, capsize=0, linewidth=2,
                    label=f"confirmed N28 ({n} fresh seeds, 95 % CI)" if i == 0 else None)
    ax.axhline(0, color=MUTED, linewidth=0.8)
    ax.axhline(1, color=MUTED, linewidth=0.8, linestyle=":")
    ax.set_xlabel("steps on the first split before the switch (t)", fontsize=8.5, color=INK)
    ax.set_ylabel("persistence index π", fontsize=8.5, color=INK)
    ax.set_title("The early choice becomes persistent within ≈ 50 steps (add mod 113)", fontsize=9, color=INK, loc="left")
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=7.5)
    ax.legend(fontsize=7, frameon=False, loc="upper left")
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(HERE / f"fig4_pi_curve.{ext}", dpi=200, facecolor=SURFACE)
    print("[fig4] written", {t: (round(c[0], 3), tuple(round(x, 3) for x in c[1]), c[2]) for t, c in conf.items()}, flush=True)


if __name__ == "__main__":
    main()
