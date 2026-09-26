"""Post hoc (session 15, exploratory, already analysed seeds 30-34): does the F head start grow or decay under G training?

pi(t, s) = (D_switch(s) - D_G(s)) / (D_F(s) - D_G(s)) with D = beta_F - beta_G (see posthoc_beta_persistence.py), evaluated at every
stored global step s of the switch run (spectra every 250 steps). D_F(s), D_G(s) come from the pure EXP-018 runs of the same seed at the
same global step. Pure numpy on stored spectra and split files; no training.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from posthoc_beta_persistence import SEEDS, TS, beta  # noqa: E402
from posthoc_beta_persistence import mask_power  # noqa: E402

RAW = HERE / "raw"


def spectra(run: Path) -> dict[int, np.ndarray]:
    st, pw = np.load(run / "spectra_steps.npy"), np.load(run / "spectra.npy")
    return {int(a): b for a, b in zip(st, pw)}


def main() -> None:
    out: dict = {}
    for s in SEEDS:
        m = {a: mask_power(np.load(HERE / f"splits/seed{s}_train_{a}.npy"), "add", 113) for a in "FG"}
        dd = lambda pw: beta(m["F"], pw) - beta(m["G"], pw)  # noqa: E731
        pure = {a: spectra(RAW / f"EXP-018_baseline_seed{s}_thr4_seed{s}_train_{a}") for a in "FG"}
        for t in TS:
            sw = spectra(RAW / f"EXP-020_baseline_seed{s}_thr4_seed{s}_train_F_to_seed{s}_train_G_at{t}")
            row = {}
            for g, pw in sorted(sw.items()):
                if g <= t or g not in pure["F"] or g not in pure["G"]:
                    continue
                dF, dG = dd(pure["F"][g]), dd(pure["G"][g])
                row[g] = {"pi": (dd(pw) - dG) / (dF - dG), "den": dF - dG}
            out.setdefault(str(t), {})[str(s)] = row
    (HERE / "posthoc_pi_trajectory.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for t in TS:
        steps = sorted({int(g) for r in out[str(t)].values() for g in r})
        line = []
        for g in steps:
            v = [out[str(t)][str(s)][g]["pi"] for s in SEEDS if g in out[str(t)][str(s)]]
            line.append(f"{g}:{np.mean(v):.2f}[{min(v):.2f},{max(v):.2f}]")
        print(f"t={t:>4} " + "  ".join(line))
    dens = [r[g]["den"] for t in out.values() for r in t.values() for g in r]
    print("denominator D_F - D_G: min", round(min(dens), 2), "median", round(float(np.median(dens)), 2))


if __name__ == "__main__":
    main()
