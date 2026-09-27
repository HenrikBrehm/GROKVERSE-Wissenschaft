"""N29 post hoc, EXPLORATION (session 28; N29 seeds already seen, no confirmation). Programme B, persistence.

Question: after a data switch A -> B, which of the five OLD targets (T_A) keep the most W_E power at the end (t + 4000)?
Three predictors, fixed before looking at any ranking:
  switch : the target's W_E power at the switch step t (history: what the target acquired before the switch),
  M0c_A  : its power in the centred coherent mask spectrum of the FIRST split (A; in B->A runs: B) (the early gradient that built it),
  M0c_B  : its power in the mask spectrum of split B (residual support by the NEW data).
Reading: if 'switch' (or M0c_A) orders the old targets and M0c_B does not, persistence of a target follows its pre-switch
history; if M0c_B orders them, it follows the new data's residual support. Same analysis for the NEW targets T_B at the end
(C1 analogue within switch runs: M0c_B vs power at the switch). Mean within-run Spearman over the 20 seeds per switch step,
within-run permutation null (20 000), two-sided. Reads the stored W_E snapshots directly (not through the frozen N29 loader).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "confirm"))
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
from analyze import group_power  # noqa: E402
from P1_posthoc_within import m0c_add, mean_rho  # noqa: E402

P, N_PERM = 113, 20_000
RAW, SPL = LAB / "confirm/n29_raw", LAB / "confirm/n29_splits"


def main() -> None:
    rng = np.random.default_rng(2026_09_28_3)
    out = {"note": "post hoc exploration on seen N29 seeds", "t": {}}
    for t in (25, 50):
        rows = {"old": {"y": [], "switch": [], "M0c_A": [], "M0c_B": []}, "new": {"y": [], "switch": [], "M0c_A": [], "M0c_B": []}}
        for d in sorted(RAW.glob(f"*_at{t}_devcuda")):
            s = int(d.name.split("_seed")[1].split("_")[0])
            meta = json.loads((SPL / f"n29_seed{s}_w0.json").read_text(encoding="utf-8"))
            steps = list(np.load(d / "we_snapshot_steps.npy"))
            W = np.load(d / "we_snapshots.npy").astype(np.float64)
            pw_t, pw_end = (group_power(W[steps.index(k)], "add", P)[0] for k in (t, t + 4000))
            first, second = ("A", "B") if f"w0_A_to_n29_seed{s}_w0_B" in d.name else ("B", "A")   # both directions ran
            mA, mB = (m0c_add(np.load(SPL / f"n29_seed{s}_w0_{a}.npy"), P) for a in (first, second))  # A/B = first/second split
            for key, T in (("old", meta["targets"][first]), ("new", meta["targets"][second])):
                sel = [k - 1 for k in T]
                for name, v in (("y", pw_end), ("switch", pw_t), ("M0c_A", mA), ("M0c_B", mB)):
                    rows[key][name].append(v[sel])
        res = {}
        for key, r in rows.items():
            Y = np.array(r["y"])
            res[key] = {"n": len(Y)}
            for name in ("switch", "M0c_A", "M0c_B"):
                X = np.array(r[name])
                obs = mean_rho(X, Y)
                null = np.array([mean_rho(rng.permuted(X, axis=1), Y) for _ in range(N_PERM)])
                res[key][name] = {"mean_rho": round(obs, 3), "p_two": float((np.abs(null) >= abs(obs)).mean())}
        out["t"][str(t)] = res
        print(t, json.dumps(res), flush=True)
    (LAB / "confirm/N29_posthoc_within.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
