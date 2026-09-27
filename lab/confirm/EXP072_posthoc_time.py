"""EXP-072 post hoc, EXPLORATION (session 28): does the fine order of the five target irreps (N39) persist after D59 groks?
Pilot seeds 1000-1004 (the P1 D59 splits, already seen), 20 000 steps. Mean within-arm Spearman(M0 of the split = D59 mask
spectrum confirm_splits.m0, irrep power of W_E) at several steps; first step with test acc >= 0.9 from result.json events."""
import json, sys
from pathlib import Path
import numpy as np
LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools")); sys.path.insert(0, str(LAB / "confirm"))
import confirm_splits as cs
from rank_tools import spearman
E = next((LAB / "experiments").glob("EXP-072*"))
rows, gens = {}, []
for d in sorted((E / "raw").glob("*_devcuda")):
    stem = d.name.split("_", 2)[2].rsplit("_devcuda", 1)[0]
    T = json.loads((LAB / "confirm/splits" / f"{stem}.json").read_text(encoding="utf-8"))["targets"]; sel = [k - 1 for k in T]
    m = cs.m0(np.load(LAB / "confirm/splits" / f"{stem}.npy"), "D", 59)[sel]
    sp, st = np.load(d / "spectra.npy"), list(np.load(d / "spectra_steps.npy"))
    gens.append((json.loads((d / "result.json").read_text(encoding="utf-8")).get("events") or {}))
    for s in (0, 250, 1000, 2000, 4000, 6000, 10000, 15000, 20000):
        if s in st:
            rows.setdefault(s, []).append(spearman(m, sp[st.index(s)][sel]))
out = {"arms": len(gens), "events_example": gens[0], "mean_rho_M0": {s: round(float(np.mean(v)), 3) for s, v in rows.items()},
       "n_pos": {s: int((np.array(v) > 0).sum()) for s, v in rows.items()}}
print(json.dumps(out, indent=1))
(LAB / "confirm/EXP072_posthoc_time.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
