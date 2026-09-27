"""Figure 6 (draft, EXPLORATION, section 4): the delay of generalization caused by a data switch at step t, next to the persistence of
the first split's frequency choice. add mod 113, pair-disjoint split pairs (omega = 0), GPU.
Top: switch cost C(t) = per-seed mean over both directions of log2 b(switch at t) - log2 b(destination split only), b = first test
accuracy >= 0.95 bounded at 2000 steps from step 0 (R6 definition). Pilot seeds 400-409 (EXP-059 + EXP-056, same splits/init; mean with
95 % bootstrap CI over seeds); N28 seeds 2200-2229 at t = 25 and 50 (same definition). All post hoc on seeds whose frequencies were seen;
the confirmation R6 is drafted, not run. Bottom: persistence index pi of the same pilot seeds (EXP-059 summary, mean +- SD), as in fig. 4.
Two panels instead of two y-axes. Output: fig6_switch_cost.png/.svg.
"""
from __future__ import annotations

import glob
import json
import math
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
PILOT, N28C, INK, MUTED, SURFACE, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#fcfcfb", "#d9d8d3"   # palette slots 1, 2
CAP = 2000


def boot_ci(v: np.ndarray, rng: np.random.Generator, n: int = 10000) -> tuple[float, float]:
    m = rng.choice(v, (n, len(v)), replace=True).mean(1)
    return float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))


def log_b(d: Path) -> float:
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    assert r["status"] == "completed", d.name
    g = (r.get("events") or {}).get("generalization_step")
    return math.log2(min(g, CAP) if g is not None else CAP)


def costs(dirs: list[Path], pat: re.Pattern, ts: list[int]) -> dict[int, np.ndarray]:
    lb: dict = {}
    for root in dirs:
        for d in root.iterdir():
            m = pat.search(d.name)
            if not m or m.group(5):                         # skip optimizer-reset variants
                continue
            s, a, b, t = int(m.group(1)), m.group(2), m.group(3), m.group(4)
            if b is not None and int(t) not in ts:
                continue
            lb.setdefault(s, {})[a if b is None else (a + b, int(t))] = log_b(d)
    return {t: np.array([((v[("AB", t)] - v["B"]) + (v[("BA", t)] - v["A"])) / 2 for v in lb.values()]) for t in ts}


def main() -> None:
    ts = [10, 15, 20, 25, 30, 35, 50]
    pil = costs([LAB / "experiments/EXP-059-momentum-exposure/raw", LAB / "experiments/EXP-056-overlap-persistence/raw"],
                re.compile(r"seed(\d+)_thr1_seed\d+_w0_(A|B)(?:_to_seed\d+_w0_(A|B)_at(\d+)(_rom)?)?_devcuda$"), ts)
    n28 = costs([LAB / "confirm/n28_raw"], re.compile(r"seed(\d+)_thr1_n28_seed\d+_w0_(A|B)(?:_to_n28_seed\d+_w0_(A|B)_at(\d+)(_rom)?)?_devcuda$"),
                [25, 50])
    ref = json.loads((LAB / "confirm/speed_switch_curve_s32.json").read_text(encoding="utf-8"))["C"]
    assert all(abs(pil[t].mean() - ref[str(t)]["mean"]) < 1e-9 for t in ts), "pilot values differ from speed_switch_curve_s32.json"
    rng = np.random.default_rng(6)
    pm = np.array([pil[t].mean() for t in ts])
    pci = np.array([boot_ci(pil[t], rng) for t in ts])
    s59 = json.loads(Path(glob.glob(str(LAB / "experiments/EXP-059-*/summary.json"))[0]).read_text(encoding="utf-8"))
    tp = sorted(int(t) for t in s59["pi_normal_mean"])
    pim = np.array([s59["pi_normal_mean"][str(t)] for t in tp])
    pisd = np.array([s59["pi_normal_sd"][str(t)] for t in tp])

    fig, (ax, bx) = plt.subplots(2, 1, figsize=(5.2, 5.0), sharex=True, facecolor=SURFACE, gridspec_kw={"height_ratios": [3, 2]})
    for a in (ax, bx):
        a.set_facecolor(SURFACE)
        a.grid(axis="y", color=GRID, linewidth=0.6)
        a.set_axisbelow(True)
        for side in ("top", "right"):
            a.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            a.spines[side].set_color(MUTED)
        a.tick_params(colors=MUTED, labelsize=7.5)
        a.axhline(0, color=MUTED, linewidth=0.8)
    ax.fill_between(ts, pci[:, 0], pci[:, 1], color=PILOT, alpha=0.15, linewidth=0)
    ax.plot(ts, pm, "-o", color=PILOT, linewidth=2, markersize=5, label="pilot seeds 400–409 (mean, 95 % CI)")
    for i, t in enumerate((25, 50)):
        m, (lo, hi) = float(n28[t].mean()), boot_ci(n28[t], rng)
        ax.errorbar([t + 1.2], [m], yerr=[[m - lo], [hi - m]], fmt="s", color=N28C, markersize=6, capsize=0, linewidth=2,
                    label=f"N28 ({len(n28[t])} seeds, 95 % CI)" if i == 0 else None)
    ax.set_ylabel("delay of generalization\nlog2 (switch / destination only)", fontsize=8.5, color=INK)
    ax.set_title("Switching data during the lock-in delays grokking (post hoc)", fontsize=9, color=INK, loc="left")
    ax.legend(fontsize=7, frameon=False, loc="lower left")
    bx.fill_between(tp, pim - pisd, pim + pisd, color=PILOT, alpha=0.15, linewidth=0)
    bx.plot(tp, pim, "-o", color=PILOT, linewidth=2, markersize=5)
    bx.axhline(1, color=MUTED, linewidth=0.8, linestyle=":")
    bx.set_ylabel("persistence π\n(pilot, mean ± SD)", fontsize=8.5, color=INK)
    bx.set_xlabel("steps on the first split before the switch (t)", fontsize=8.5, color=INK)
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(HERE / f"fig6_switch_cost.{ext}", dpi=200, facecolor=SURFACE)
    print("[fig6] pilot C", dict(zip(ts, pm.round(3))), "N28", {t: round(float(n28[t].mean()), 3) for t in (25, 50)}, flush=True)


if __name__ == "__main__":
    main()
