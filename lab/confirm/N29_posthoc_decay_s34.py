"""Session 34, post hoc on the frozen N29 runs (seeds 2250-2269, add 113, one-layer transformer): does the persistence of the
first split's frequencies decay with longer training after the switch, or does it stay? (paper section 6 lists this as untested;
Janati et al. 2026 report post-grokking loss of generalization for add 113.)

Fixed BEFORE reading any trajectory (only the final-step values of N29 were read before, for K4c):
- Measure per seed and switch time t in {25, 50}: D(tau) = (L_AB(tau) - L_BA(tau)) / 2, L = log(P(A targets) / P(B targets)) of the
  stored W_E power (spectra.npy, additive DFT, k = 1..56), tau = steps after the switch (0, 250, ..., 4000).
  D > 0: the first split's targets dominate (persistence); D < 0: the second split's targets dominate.
- H_decay: at t = 50, D(+4000) < D(+2000) in >= 2/3 of the valid seeds AND median D(+4000)/D(+2000) < 0.8.
- H_hold: median ratio in [0.8, 1.25] (or growth > 1.25 = "strengthens"); any other pattern = unclear.
- t = 25 is reported descriptively (the sign is expected negative, so a ratio is read as |D| of the new targets).
Decision rule: H_decay -> K4 in the paper gets a time qualifier ("persists for at least 2000 steps, then decays");
H_hold -> section 6 names this as a post hoc observation up to 4000 steps (N29 seeds, already used for K4c, not a confirmation).
Only loading, no training. Run: python lab/confirm/N29_posthoc_decay_s34.py
"""
import json
from pathlib import Path

import numpy as np

RAW, SPL = Path("lab/confirm/n29_raw"), Path("lab/confirm/n29_splits")
OUT = Path("lab/confirm/N29_posthoc_decay_s34.json")


def run(s: int, first: str, second: str, t: int) -> Path:
    return RAW / f"EXP-020_baseline_seed{s}_thr1_n29_seed{s}_w0_{first}_to_n29_seed{s}_w0_{second}_at{t}_devcuda"


def L_traj(d: Path, F: list[int], G: list[int], t: int) -> dict[int, float]:
    S, steps = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy")
    return {int(st) - t: float(np.log(S[i, [k - 1 for k in F]].sum() / S[i, [k - 1 for k in G]].sum()))
            for i, st in enumerate(steps) if st >= t}


def main() -> None:
    summ = json.loads(Path("lab/confirm/N29_summary.json").read_text(encoding="utf-8"))
    seeds = [r["seed"] for r in summ["rows"] if not r.get("technical")]
    out = {"seeds": seeds, "per_seed": {}, "t": {}}
    for t in (25, 50):
        Ds = []
        for s in seeds:
            tg = json.loads((SPL / f"n29_seed{s}_w0.json").read_text(encoding="utf-8"))["targets"]
            ab, ba = L_traj(run(s, "A", "B", t), tg["A"], tg["B"], t), L_traj(run(s, "B", "A", t), tg["A"], tg["B"], t)
            D = {tau: (ab[tau] - ba[tau]) / 2 for tau in sorted(ab) if tau in ba}
            out["per_seed"][f"{s}@{t}"] = D
            Ds.append(D)
        taus = sorted(set.intersection(*[set(D) for D in Ds]))
        M = np.array([[D[tau] for tau in taus] for D in Ds])
        d2, d4 = M[:, taus.index(2000)], M[:, taus.index(4000)]
        ratio = d4 / d2
        rng = np.random.default_rng(34)
        boot = [np.mean((d4 - d2)[rng.integers(0, len(d2), len(d2))]) for _ in range(10000)]
        out["t"][t] = {"taus": taus, "mean_D": M.mean(0).tolist(), "sd_D": M.std(0, ddof=1).tolist(),
                       "median_ratio_4000_2000": float(np.median(ratio)),
                       "n_decrease_abs": int(np.sum(np.abs(d4) < np.abs(d2))), "n": len(d2),
                       "mean_change_4000_minus_2000": float(np.mean(d4 - d2)),
                       "ci95_change": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
                       "n_sign_kept_4000": int(np.sum(np.sign(d4) == np.sign(M[:, taus.index(250)])))}
        r = out["t"][t]
        print(f"t={t}: n={r['n']}  mean D at tau " + ", ".join(f"{tau}:{m:+.2f}" for tau, m in zip(taus, r["mean_D"]) if tau % 500 == 0 or tau == 250))
        print(f"   median D4000/D2000 {r['median_ratio_4000_2000']:.3f}; |D| smaller at 4000 in {r['n_decrease_abs']}/{r['n']}; "
              f"mean change {r['mean_change_4000_minus_2000']:+.3f} CI {r['ci95_change'][0]:+.3f}..{r['ci95_change'][1]:+.3f}; sign as at +250 kept {r['n_sign_kept_4000']}/{r['n']}")
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
