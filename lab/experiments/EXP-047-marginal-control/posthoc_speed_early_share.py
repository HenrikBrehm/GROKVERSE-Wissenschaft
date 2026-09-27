"""Session 31 (2026-09-27), POST HOC exploration on stored runs (no training).

Question: within ONE concentration level (EXP-047 engineered arms, eps 2, GPU, 10 seeds x F/G), does the early W_E power share on the
arm's own 5 targets (step 250: after memorisation, before any generalisation) predict how early the run generalises (trainer event,
first test >= 0.95)? Stated before looking: Spearman(share_250, gen) < 0 over the 20 runs; also paired within seed (F and G share the
init): does the arm with the higher share_250 generalise earlier? For comparison the same with the mask share (M0 target share).
Motivation: across eps 1/2/8 both are ordered alike (EXP-042/posthoc_speed_amplitude.py); within eps 2 the MASK share did not predict
paired (lab/confirm/speed_posthoc_share_within.py).
  python lab/experiments/EXP-047-marginal-control/posthoc_speed_early_share.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
import confirm_splits as cs  # noqa: E402

SEEDS = range(150, 160)


def spear(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def main() -> None:
    rows = []
    for sd in SEEDS:
        for arm in "FG":
            T = {arm: json.loads((HERE / "splits" / f"split_add113_seed{sd}_eng_{arm}.json").read_text(encoding="utf-8"))["targets"]}
            d = HERE / "raw" / f"EXP-016_baseline_seed{sd}_thr1_split_add113_seed{sd}_eng_{arm}_devcuda"
            r = json.loads((d / "result.json").read_text(encoding="utf-8"))
            st = [int(x) for x in np.load(d / "spectra_steps.npy")]
            pw = np.load(d / "spectra.npy")[st.index(250)]
            m0 = cs.m0(np.load(HERE / "splits" / f"split_add113_seed{sd}_eng_{arm}.npy"), "add", 113)
            g = (r.get("events") or {}).get("generalization_step")
            rows.append({"seed": sd, "arm": arm, "gen": g, "we_share_250": float(pw[[k - 1 for k in T[arm]]].sum() / pw.sum()),
                         "m0_share": float(m0[[k - 1 for k in T[arm]]].sum() / m0.sum())})
    gen = np.array([np.inf if r["gen"] is None else r["gen"] for r in rows])
    out = {"note": "post hoc exploration, seen seeds 150-159", "rows": rows, "n": len(rows), "n_censored": int(np.isinf(gen).sum())}
    rng = np.random.default_rng(0)
    for key in ("we_share_250", "m0_share"):
        x = np.array([r[key] for r in rows])
        rho = spear(x, gen)
        null = np.array([spear(x, rng.permutation(gen)) for _ in range(20000)])
        w = l = 0
        for sd in SEEDS:
            f, g_ = [r for r in rows if r["seed"] == sd]
            hi, lo = (f, g_) if f[key] > g_[key] else (g_, f)
            gh, gl = (np.inf if q["gen"] is None else q["gen"] for q in (hi, lo))
            w, l = w + (gh < gl), l + (gh > gl)
        n = w + l
        out[key] = {"spearman": rho, "p_one_sided_perm": float((null <= rho).mean()),
                    "paired_higher_earlier": int(w), "paired_later": int(l),
                    "p_sign_one_sided": sum(math.comb(n, k) for k in range(w, n + 1)) / 2 ** n if n else 1.0}
    (HERE / "posthoc_speed_early_share.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
