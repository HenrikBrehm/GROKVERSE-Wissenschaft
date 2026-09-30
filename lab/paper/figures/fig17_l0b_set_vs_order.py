"""Figure 17 (draft; paper Section 6 and appendix J): L0b confirmation - set composition against a fixed data order in the
long-epoch regime (add 113, AdamW, batch 16, weight decay 0.1, 30 000 steps; 70 fresh seeds, frozen manifest bce36b1a).
(a) energy share on the stride-order frequencies O = {11, 12, 22, 23, 34, 45} per seed, i.i.d. vs stride order, for the random
split R and the engineered splits (F/G mean); chance 6/56. (b) paired order effects x_H1 (R) and x_H2 (F/G) with the registered
equivalence band +-0.02 for H2. (c) x_H3 = steering Delta_pow(stride) - Delta_pow(iid) with the non-inferiority margin -2.
(d) x_H4 = mean over F/G of log2 t_gen(stride) / t_gen(iid) (runs that never generalise censored at the budget).
Means and 95 % CIs are taken from the frozen analysis (lab/confirm/L0b_summary.json, bootstrap rng 21); verdicts are the
registered Holm-family verdicts. Written in session 65 (2026-10-01, ~00:55 Berlin) BEFORE any L0b result was looked at.
  python lab/paper/figures/fig17_l0b_set_vs_order.py            # real data -> fig17_l0b_set_vs_order.png/.svg
  python lab/paper/figures/fig17_l0b_set_vs_order.py --demo     # synthetic numbers, writes only to a temp dir (code check)
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
CHANCE_O = 6 / 56
DELTA, H3_MARGIN = 0.02, 2.0          # as registered in lab/tools/confirm_l0b.py
VERDICT_EN = {"bestätigt": "confirmed", "nicht bestätigt": "not confirmed"}


def style(a: plt.Axes) -> None:
    a.set_facecolor(SURFACE)
    a.grid(axis="y", color=GRID, linewidth=0.6)
    a.set_axisbelow(True)
    for side in ("top", "right"):
        a.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        a.spines[side].set_color(MUTED)
    a.tick_params(colors=MUTED, labelsize=7.5)


def demo_summary() -> dict:
    rng = np.random.default_rng(0)
    rows = []
    for s in range(70):
        o_r, o_fg = CHANCE_O + rng.normal(0, 0.01), 0.05 + rng.normal(0, 0.01)
        r = {"seed": 3730 + s, "technical": False, "o_R_iid16w": o_r, "o_R_stride16w": o_r + 0.03 + rng.normal(0, 0.02),
             "o_FG_iid16w": o_fg, "o_FG_stride16w": o_fg + rng.normal(0, 0.01)}
        r.update({"x_H1": r["o_R_stride16w"] - o_r, "x_H2": r["o_FG_stride16w"] - o_fg,
                  "x_H3": rng.normal(-0.3, 1.0), "x_H4": rng.normal(0.4, 0.5)})
        rows.append(r)
    hyp: dict = {"n": 70}
    for h in ("H1", "H2", "H3", "H4"):
        x = np.array([r[f"x_{h}"] for r in rows])
        m = rng.choice(x, (4000, len(x)), replace=True).mean(1)
        hyp[h] = {"mean": float(x.mean()), "ci95": [float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))],
                  "p_holm": 0.01, "verdict": "bestätigt"}
    return {"manifest_commit": "DEMO", "hypotheses": hyp, "rows": rows}


def strip(ax: plt.Axes, j: float, x: np.ndarray, h: dict | None, col: str, rng: np.random.Generator) -> None:
    ax.scatter(j + rng.uniform(-0.12, 0.12, len(x)), x, s=7, color=col, alpha=0.55, zorder=2, linewidths=0)
    if h and "ci95" in h:
        lo, hi = h["ci95"]
        ax.errorbar(j + 0.28, h["mean"], yerr=[[h["mean"] - lo], [hi - h["mean"]]], fmt="o", color=INK, markersize=4, capsize=3, zorder=3)


def label(h: dict | None, name: str) -> str:
    if not h or "verdict" not in h:
        return f"{name}: not evaluable"
    return f"{name}: {VERDICT_EN.get(h['verdict'], h['verdict'])} (Holm-p {h['p_holm']:.1g})"


def plot(summ: dict, out_dir: Path, tag: str = "") -> None:
    rows = [r for r in summ["rows"] if not r.get("technical")]
    hyp = summ["hypotheses"]
    rng = np.random.default_rng(11)   # jitter only
    fig, axs = plt.subplots(1, 4, figsize=(11.0, 3.6), gridspec_kw={"width_ratios": [2.2, 1.6, 1, 1]}, facecolor=SURFACE)
    for a in axs:
        style(a)
    ax, bx, cx, dx = axs
    cols = (("o_R_iid16w", C1), ("o_R_stride16w", C2), ("o_FG_iid16w", C1), ("o_FG_stride16w", C2))
    for r in rows:
        for k in (0, 2):
            ax.plot([k, k + 1], [r[cols[k][0]], r[cols[k + 1][0]]], color=GRID, linewidth=0.5, zorder=1)
    for j, (key, col) in enumerate(cols):
        v = np.array([r[key] for r in rows], float)
        ax.scatter(np.full(len(v), j) + rng.uniform(-0.05, 0.05, len(v)), v, s=7, color=col, alpha=0.7, zorder=2, linewidths=0)
    ax.axhline(CHANCE_O, color=MUTED, linewidth=0.8, linestyle=":")
    ax.set_xticks(range(4), ["R\ni.i.d.", "R\nstride", "F/G\ni.i.d.", "F/G\nstride"], fontsize=7.2, color=INK)
    ax.set_ylabel("energy share on order frequencies O", fontsize=8.5, color=INK)
    ax.set_title("(a) per seed, end of budget", fontsize=8, color=MUTED, loc="left")
    bx.axhspan(-DELTA, DELTA, color=GRID, alpha=0.5, zorder=0)
    for j, h in enumerate(("H1", "H2")):
        strip(bx, j, np.array([r[f"x_{h}"] for r in rows], float), hyp.get(h), C2, rng)
    bx.axhline(0, color=MUTED, linewidth=0.8)
    bx.set_xticks([0, 1], ["H1\nR", "H2\nF/G"], fontsize=7.2, color=INK)
    bx.set_ylabel("order effect on O share (stride - i.i.d.)", fontsize=8.5, color=INK)
    bx.set_title("(b) band = equivalence ±0.02", fontsize=8, color=MUTED, loc="left")
    strip(cx, 0, np.array([r["x_H3"] for r in rows], float), hyp.get("H3"), C1, rng)
    cx.axhline(0, color=MUTED, linewidth=0.8)
    cx.axhline(-H3_MARGIN, color=C2, linewidth=0.9, linestyle="--")
    cx.set_xticks([0], ["H3"], fontsize=7.2, color=INK)
    cx.set_ylabel(r"$\Delta_{pow}$(stride) $-$ $\Delta_{pow}$(i.i.d.)", fontsize=8.5, color=INK)
    cx.set_title("(c) margin −2", fontsize=8, color=MUTED, loc="left")
    strip(dx, 0, np.array([r["x_H4"] for r in rows], float), hyp.get("H4"), C1, rng)
    dx.axhline(0, color=MUTED, linewidth=0.8)
    dx.set_xticks([0], ["H4\nF/G"], fontsize=7.2, color=INK)
    dx.set_ylabel(r"log$_2$ t$_{gen}$(stride) / t$_{gen}$(i.i.d.)", fontsize=8.5, color=INK)
    dx.set_title("(d) delay", fontsize=8, color=MUTED, loc="left")
    n = hyp.get("n", len(rows))
    head = f"L0b, batch 16, {n} seeds (manifest {str(summ.get('manifest_commit', '?'))[:8]})"
    if hyp.get("verdict") == "nicht auswertbar":
        head += " - NOT EVALUABLE"
    lines = "   ".join(label(hyp.get(h), h) for h in ("H1", "H2", "H3", "H4"))
    fig.suptitle(f"{tag}{head}\n{lines}", fontsize=8, color=INK, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    for ext in ("png", "svg"):
        fig.savefig(out_dir / f"fig17_l0b_set_vs_order.{ext}", dpi=200, facecolor=SURFACE)
    plt.close(fig)


def main() -> None:
    if sys.argv[1:] == ["--demo"]:
        with tempfile.TemporaryDirectory() as tmp:
            plot(demo_summary(), Path(tmp), "DEMO (synthetic numbers) - ")
            print("[fig17] demo ok (nothing written to the repo)")
        return
    src = LAB / "confirm/L0b_summary.json"
    if not src.exists():
        raise SystemExit(f"[fig17] {src} missing: run confirm_l0b.py --analyze first")
    plot(json.loads(src.read_text(encoding="utf-8")), HERE)
    print("[fig17] written")


if __name__ == "__main__":
    main()
