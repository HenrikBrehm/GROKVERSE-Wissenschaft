"""Post hoc (session 41, exploration): premise check for the 'older gradients are less selective' reading.
Pure R9 runs (snapshots 0, 50, 250, 2000): share f of the group power of the W_E increment on the run's own five targets,
for 0->50, 50->250, 250->2000; plus the cumulative 0->50 and 0->250. Chance share: 5/56 = 0.089."""
import importlib.util, json
from pathlib import Path
import numpy as np
LAB = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("a43", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
a43 = importlib.util.module_from_spec(spec); spec.loader.exec_module(a43)
RAW, SPL = LAB / "confirm/r9_raw", LAB / "confirm/r9_splits"
def f(D, T):
    pw = a43.group_power(D, "add", 113)[0]; return pw[[k - 1 for k in T]].sum() / pw.sum()
rows = []
for s in range(3300, 3336):
    m = json.loads((SPL / f"r9_seed{s}_w0.json").read_text(encoding="utf-8"))
    for arm in "AB":
        d = RAW / f"EXP-018_baseline_seed{s}_thr1_r9_seed{s}_w0_{arm}_devcuda"
        st = np.load(d / "we_snapshot_steps.npy").tolist(); W = dict(zip(st, np.load(d / "we_snapshots.npy")))
        T = m["targets"][arm]
        rows.append({"seed": s, "arm": arm, "f_0_50": f(W[50] - W[0], T), "f_50_250": f(W[250] - W[50], T),
                     "f_250_2000": f(W[2000] - W[250], T), "N_0_50": float(np.linalg.norm((W[50] - W[0])[:113])),
                     "N_50_250": float(np.linalg.norm((W[250] - W[50])[:113]))})
col = lambda k: np.array([r[k] for r in rows])
out = {k: float(col(k).mean()) for k in rows[0] if k not in ("seed", "arm")}
d = col("f_50_250") - col("f_0_50")
out["f_50_250_minus_f_0_50_pos"] = int((d > 0).sum()); out["n_runs"] = len(rows)
(LAB / "confirm/R9_increment_selectivity_s41.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
