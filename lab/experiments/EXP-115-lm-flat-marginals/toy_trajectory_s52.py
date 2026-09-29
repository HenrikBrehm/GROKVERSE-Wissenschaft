"""Session 52, post hoc exploration: Delta_pow trajectory in the toy model (EXP-104 runs, flat splits) every 250 steps.
Reading fixed before computing (JOURNAL S52 cycle 1): per seed/m over common steps of both arms, "decline" if Delta_pow at the
last common step < 0.8 * max and the max lies >= 500 steps before the end; else "rises/plateau". Descriptive, 2 seeds.
"""
import json, sys
from pathlib import Path
import numpy as np
LAB = Path(__file__).resolve().parents[2]
E = LAB / "experiments" / "EXP-104-flat-marginal-splits"
sys.path.insert(0, str(E))
from analyze import delta_pow  # noqa: E402
out = []
for seed in (3850, 3851):
    for m in (0, 10, 500):
        sp, st, T, gen = {}, {}, {}, {}
        for arm in ("F", "G"):
            d = E / "raw" / f"EXP-018_baseline_seed{seed}_thr1_s{seed}_{arm}_m{m}_tf0.3009_devcuda"
            sp[arm] = np.load(d / "spectra.npy"); st[arm] = np.load(d / "spectra_steps.npy")
            T[arm] = json.loads((E / "splits" / f"s{seed}_{arm}_m{m}.json").read_text())["targets"]
            gen[arm] = (json.loads((d / "result.json").read_text()).get("events") or {}).get("generalization_step")
        common = sorted(set(st["F"].tolist()) & set(st["G"].tolist()))
        tr = []
        for s in common:
            iF = int(np.where(st["F"] == s)[0][0]); iG = int(np.where(st["G"] == s)[0][0])
            tr.append((s, delta_pow(sp["F"][iF], sp["G"][iG], T["F"], T["G"])))
        steps = [s for s, _ in tr]; vals = [v for _, v in tr]
        k = int(np.argmax(vals)); last = vals[-1]
        reading = "decline" if (last < 0.8 * vals[k] and steps[-1] - steps[k] >= 500) else "rises/plateau"
        row = {"seed": seed, "m": m, "gen": gen, "peak_step": steps[k], "peak": round(vals[k], 2), "last_step": steps[-1],
               "last": round(last, 2), "reading": reading, "trace": {s: round(v, 2) for s, v in tr if s % 500 == 0}}
        out.append(row); print(json.dumps(row))
(Path(__file__).with_suffix(".json")).write_text(json.dumps(out, indent=1), encoding="utf-8")
