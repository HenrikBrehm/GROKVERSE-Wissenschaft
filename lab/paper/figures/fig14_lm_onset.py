"""Figure 14 (short paper Appendix K, candidate): in the small language model, steering of the number-token embedding appears
together with the fit to the training facts. Per F/G pair: (a) Delta_pow(t) on the 113 number-token rows; (b) training-fact
and held-out-fact accuracy (mean of F and G); dotted line = fit onset (first snapshot with training-fact accuracy >= 0.1
in both runs). Session 51. Pure file reading (runs via the EXP-105 pilot loader), no training.
Default: EXP-114 (K = 19, 1 seed, exploration). For LM1 or other blocks pass --root and --pairs (as analyze_pilot.py) and
--out; draw a confirmation block only AFTER its frozen analysis has been run and read.
  python lab/paper/figures/fig14_lm_onset.py            # EXP-114 -> fig14_lm_onset.png/.svg
  python lab/paper/figures/fig14_lm_onset.py --demo     # synthetic curves, writes only to a temp dir (code check)
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-105-lm-ladder-stage2"))
C1, C2, C3, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1f9e89", "#0b0b0b", "#52514e", "#d9d8d3"
SPL = "lab/experiments/EXP-102-lm-ladder-stage1/splits"
DEFAULT_ROOT = "lab/experiments/EXP-114-lm-dilution-pilot/raw_k19"
DEFAULT_PAIRS = [f"3862:{SPL}/seed3802_F.npy,{SPL}/seed3802_G.npy"]


def load_pairs(root: Path, pairs: list[str]) -> list[dict]:
    import analyze_pilot as AP
    out = []
    for spec in pairs:
        seed, files = spec.split(":")
        fF, fG = (LAB.parent / x for x in files.split(","))
        rF, rG = AP.load(root, int(seed), fF), AP.load(root, int(seed), fG)
        steps = [s for s in rF["steps"] if s in rG["P"]]
        dp = [AP.A.delta_pow(rF["P"][s], rG["P"][s], AP.targets(fF), AP.targets(fG)) for s in steps]
        cF = {int(r[0]): r for r in rF["res"]["curve"]}
        cG = {int(r[0]): r for r in rG["res"]["curve"]}
        tr = [(cF[s][1] + cG[s][1]) / 2 for s in steps]
        te = [(cF[s][2] + cG[s][2]) / 2 for s in steps]
        onset = next((s for s in steps if min(cF[s][1], cG[s][1]) >= 0.1), None)
        out.append({"seed": int(seed), "steps": steps, "dpow": dp, "train": tr, "test": te, "onset": onset})
    return out


def demo() -> list[dict]:
    steps = list(range(0, 4001, 250))
    s = np.array(steps, float)
    fit = 1 / (1 + np.exp(-(s - 1900) / 80))
    return [{"seed": 0, "steps": steps, "dpow": list(5.5 * fit + 0.01 * np.sin(s)), "train": list(fit),
             "test": list(0.98 * fit ** 2), "onset": 1750}]


def draw(rows: list[dict], title: str, out: Path) -> None:
    fig, ax = plt.subplots(1, 2, figsize=(9.0, 3.2), constrained_layout=True)
    for r in rows:
        ax[0].plot(r["steps"], r["dpow"], color=C1, lw=1.4, alpha=0.9 if len(rows) == 1 else 0.5)
        ax[1].plot(r["steps"], r["train"], color=C3, lw=1.4, alpha=0.9 if len(rows) == 1 else 0.5)
        ax[1].plot(r["steps"], r["test"], color=C2, lw=1.4, ls="--", alpha=0.9 if len(rows) == 1 else 0.5)
        if r["onset"] is not None:
            for a in ax:
                a.axvline(r["onset"], color=MUTED, lw=0.8, ls=":")
    ax[0].axhline(1, color=GRID, lw=1)
    ax[0].set(xlabel="step", ylabel="Δ_pow (number-token rows)", title="(a) steering")
    ax[1].set(xlabel="step", ylabel="fact accuracy (mean of F, G)", title="(b) fit", ylim=(-0.02, 1.02))
    ax[1].plot([], [], color=C3, label="training facts")
    ax[1].plot([], [], color=C2, ls="--", label="held-out facts")
    ax[1].plot([], [], color=MUTED, ls=":", label="fit onset (train ≥ 0.1 in F and G)")
    ax[1].legend(frameon=False, fontsize=8, loc="center left")
    for a in ax:
        a.spines[["top", "right"]].set_visible(False)
        a.tick_params(colors=INK)
    fig.suptitle(title, fontsize=10)
    fig.savefig(out.with_suffix(".png"), dpi=200)
    fig.savefig(out.with_suffix(".svg"))
    print("wrote", out.with_suffix(".png"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--pairs", nargs="+", default=DEFAULT_PAIRS)
    ap.add_argument("--out", default=str(HERE / "fig14_lm_onset"))
    ap.add_argument("--title", default="Small language model, K = 19 arithmetic sentences (EXP-114, 1 seed, exploration)")
    a = ap.parse_args()
    if a.demo:
        draw(demo(), "demo (synthetic)", Path(tempfile.mkdtemp()) / "fig14_demo")
        return
    draw(load_pairs(LAB.parent / a.root, a.pairs), a.title, Path(a.out))


if __name__ == "__main__":
    main()
