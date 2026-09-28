"""Post hoc (session 41, exploration): selectivity and size of the W_E displacement at the switch in the stored R9 runs.
f = share of the group power of W_E(t) - W_E(0) on the first split's targets (mean over A->B and B->A); N = ||W_E(t) - W_E(0)||
over the p number rows. Direct file reads of the bound R9 run directories (no loader gates; descriptive only)."""
import importlib.util, json, sys
from pathlib import Path
import numpy as np
LAB = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("a43", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
a43 = importlib.util.module_from_spec(spec); spec.loader.exec_module(a43)
RAW, SPL = LAB / "confirm/r9_raw", LAB / "confirm/r9_splits"
CELLS = {"n25": "at25", "n30": "at30", "l100": "at100_lrs0.25", "l100b": "at100_lrs0.25_psb0.975_0.995", "c2": "at15_lrs2", "c2b": "at15_lrs2_psb0.8_0.96"}
def one(s, first, second, tag, targets):
    d = RAW / f"EXP-020_baseline_seed{s}_thr1_r9_seed{s}_w0_{first}_to_r9_seed{s}_w0_{second}_{tag}_devcuda"
    st = np.load(d / "we_snapshot_steps.npy").tolist(); W = np.load(d / "we_snapshots.npy")
    D = W[1] - W[0]; assert st[0] == 0
    pw = a43.group_power(D, "add", 113)[0]
    return pw[[k - 1 for k in targets]].sum() / pw.sum(), np.linalg.norm(D[:113])
rows = []
for s in range(3300, 3336):
    m = json.loads((SPL / f"r9_seed{s}_w0.json").read_text(encoding="utf-8"))
    F, G = m["targets"]["A"], m["targets"]["B"]
    r = {"seed": s}
    for c, tag in CELLS.items():
        (fa, na), (fb, nb) = one(s, "A", "B", tag, F), one(s, "B", "A", tag, G)
        r[f"f_{c}"], r[f"N_{c}"] = (fa + fb) / 2, (na + nb) / 2
    rows.append(r)
col = lambda k: np.array([r[k] for r in rows])
def ci(x, seed=41):
    rng = np.random.default_rng(seed); m = x[rng.integers(0, len(x), (10000, len(x)))].mean(1)
    return [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)]
out = {"means": {c: {"f": float(col(f"f_{c}").mean()), "N": float(col(f"N_{c}").mean())} for c in CELLS}}
for a, b in (("l100", "l100b"), ("c2b", "c2"), ("n30", "n25"), ("l100", "n25"), ("l100b", "n25")):
    lf, lN = np.log(col(f"f_{a}") / col(f"f_{b}")), np.log(col(f"N_{a}") / col(f"N_{b}"))
    out[f"{a}_vs_{b}"] = {"logf": float(lf.mean()), "logf_ci": ci(lf), "logf_pos": int((lf > 0).sum()),
                         "logN": float(lN.mean()), "logN_ci": ci(lN), "logN_pos": int((lN > 0).sum())}
(LAB / "confirm/R9_displacement_s41.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
