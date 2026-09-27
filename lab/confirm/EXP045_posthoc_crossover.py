"""EXP-045 post hoc, EXPLORATION (session 28). Hypothesis written before looking at the time course: in the shared-embedding MLP
the first-order theory (separate paths -> M0) holds only at the very start; once the network combines both operands the
coherent spectrum M0c takes over. Prediction: mean within-arm rho(M0, W_E target power) > rho(M0c, ...) at step 250 (the first
logged step after 0), and M0c > M0 from step 1000 on. Against it: M0c >= M0 already at 250. Data: spectra.npy of the 20 pilot
arms (seeds 90-99; add 113, where spectra.npy is the group basis). Also the transformer (P2d, add 113) for comparison."""
import json, sys
from pathlib import Path
import numpy as np
LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools")); sys.path.insert(0, str(LAB / "confirm"))
import confirm_splits as cs
from P1_posthoc_within import m0c_add
from rank_tools import spearman
E = next((LAB / "experiments").glob("EXP-045*"))
def series(runs):
    out = {}
    for d, idx, T in runs:
        sel = [k - 1 for k in T]; m0, mc = cs.m0(idx, "add", 113)[sel], m0c_add(idx, 113)[sel]
        sp, st = np.load(d / "spectra.npy"), list(np.load(d / "spectra_steps.npy"))
        for s in (0, 250, 500, 750, 1000, 1500, 2000, 4000, 10000):
            if s in st:
                out.setdefault(s, []).append((spearman(m0, sp[st.index(s)][sel]), spearman(mc, sp[st.index(s)][sel])))
    return {s: {"M0": round(float(np.mean([a for a, _ in v])), 3), "M0c": round(float(np.mean([b for _, b in v])), 3),
                "n_M0_gt_M0c": int(sum(a > b for a, b in v)), "n": len(v)} for s, v in out.items()}
mlp = []
for d in sorted((E / "raw").glob("*_mlp_devcuda")):
    stem = d.name.split("thr1_")[1].rsplit("_mlp_devcuda", 1)[0]
    mlp.append((d, np.load(E / f"splits/{stem}.npy"), json.loads((E / f"splits/{stem}.json").read_text())["targets"]))
tr = []
for d in sorted((LAB / "confirm/p2d_raw").glob("*_devcuda")):
    stem = d.name.split("thr1_")[1].rsplit("_devcuda", 1)[0]
    tr.append((d, np.load(LAB / f"confirm/p2d_splits/{stem}.npy"), json.loads((LAB / f"confirm/p2d_splits/{stem}.json").read_text())["targets"]))
out = {"mlp_EXP045": series(mlp), "transformer_P2d": series(tr)}
print(json.dumps(out, indent=0))
(LAB / "confirm/EXP045_posthoc_crossover.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
