"""Figure 9 (draft, CONFIRMED block, section 3.15): lock-in ticks in summed learning rate Lambda once Adam's moment windows are
also measured in Lambda. add mod 113, GPU. R9 (manifest 8b22879a, 36 seeds 3300-3335): persistence pi of the first choice after a
switch, per seed (thin lines join the cells of one seed), cell mean with 95 % bootstrap CI over seeds.
Left, Lambda = 25: 25 default steps (n25), 100 steps at lr x 0.25 with default betas (l100) and with windows matched in Lambda,
beta' = 1 - c (1 - beta) = 0.975 / 0.995 (l100b). Right, Lambda = 30: 30 default steps (n30), 15 steps at lr x 2 with default betas
(c2) and with beta' = 0.8 / 0.96 (c2b). Registered contrasts: H1 = l100 - l100b, H2 = l100b vs n25 (equivalence +-0.1),
H3 = c2b - c2. Reads only the frozen summary R9_summary.json. Output: fig9_r9_window_clock.png/.svg.
  python lab/paper/figures/fig9_r9_window_clock.py
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
PANELS = ((r"$\Lambda$ = 25", ("n25", "l100", "l100b"), ("25 steps\ndefault", "100 steps, lr/4\ndefault $\\beta$",
                                                         "100 steps, lr/4\n$\\beta'$ in $\\Lambda$")),
          (r"$\Lambda$ = 30", ("n30", "c2", "c2b"), ("30 steps\ndefault", "15 steps, 2 lr\ndefault $\\beta$",
                                                     "15 steps, 2 lr\n$\\beta'$ in $\\Lambda$")))


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
    r9 = json.loads((LAB / "confirm/R9_summary.json").read_text(encoding="utf-8"))
    rows = [r for r in r9["rows"] if r.get("valid")]
    assert r9["hypotheses"]["n"] == len(rows) == r9["n_planned"] == 36
    pi = {c: np.array([r[f"pi_{c}"] for r in rows]) for c in ("n25", "n30", "l100", "l100b", "c2", "c2b")}
    h = r9["hypotheses"]
    assert np.isclose((pi["l100"] - pi["l100b"]).mean(), h["H1"]["mean"]) and np.isclose((pi["c2b"] - pi["c2"]).mean(), h["H3"]["mean"])
    assert np.isclose((pi["l100b"] - pi["n25"]).mean(), h["H2"]["mean"])
    rng = np.random.default_rng(39)
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8), sharey=True, facecolor=SURFACE)
    for a, (title, cells, labels) in zip(axes, PANELS):
        style(a)
        x = np.arange(3)
        for i in range(len(rows)):
            a.plot(x, [pi[c][i] for c in cells], color=GRID, linewidth=0.7, zorder=1)
        for j, c in enumerate(cells):
            col = MUTED if j == 0 else (C2 if j == 1 else C1)
            a.scatter(np.full(len(rows), j) + rng.uniform(-0.06, 0.06, len(rows)), pi[c], s=7, color=col, alpha=0.55, zorder=2)
            lo, hi = boot_ci(pi[c], rng)
            a.errorbar(j + 0.18, pi[c].mean(), yerr=[[pi[c].mean() - lo], [hi - pi[c].mean()]], fmt="o", color=INK,
                       markersize=4, capsize=3, linewidth=1.1, zorder=3)
        a.set_xticks(x, labels, fontsize=7.5, color=INK)
        a.set_xlim(-0.4, 2.5)
        a.set_title(title, fontsize=9, color=INK, loc="left")
    axes[0].set_ylabel(r"persistence $\pi$ of the first choice", fontsize=8.5, color=INK)
    axes[0].text(2.45, 1.07, f"H1: +{h['H1']['mean']:.3f}, {h['H1']['n_positive']}/36\nH2: {h['H2']['mean']:+.3f} (equiv. $\\pm$0.1)",
                 transform=axes[0].get_xaxis_transform(), ha="right", va="top", fontsize=7, color=MUTED)
    axes[1].text(2.45, 1.07, f"H3: +{h['H3']['mean']:.3f}, {h['H3']['n_positive']}/36",
                 transform=axes[1].get_xaxis_transform(), ha="right", va="top", fontsize=7, color=MUTED)
    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(HERE / f"fig9_r9_window_clock.{ext}", dpi=200, facecolor=SURFACE)
    print("[fig9] written", {c: round(float(v.mean()), 3) for c, v in pi.items()})


if __name__ == "__main__":
    main()
