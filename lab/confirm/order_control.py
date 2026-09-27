"""Session 28, EXPLORATION: baseline for the C2 order measure. For every switch run, the same Spearman(power at t, power at
t + budget) over 5 frequencies drawn at random from those that are neither old nor new targets (200 draws per run, mean),
next to the old-target value. Data: N29 (t = 25/50, budget 4000) and EXP-059/058 (t = 10..50, budget 2000, normal arms)."""
import json, sys
from pathlib import Path
import numpy as np
LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "confirm")); sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
from analyze import group_power
from rank_tools import spearman
rng = np.random.default_rng(7)

def one(d: Path, t: int, bud: int, T_old, T_new):
    ws, W = list(np.load(d / "we_snapshot_steps.npy")), np.load(d / "we_snapshots.npy").astype(np.float64)
    a, b = (group_power(W[ws.index(k)], "add", 113)[0] for k in (t, t + bud))
    o = [k - 1 for k in T_old]
    rest = np.array([k - 1 for k in range(1, 57) if k not in T_old and k not in T_new])
    ctrl = np.mean([spearman(a[s], b[s]) for s in (rng.choice(rest, 5, replace=False) for _ in range(200))])
    return spearman(a[o], b[o]), ctrl

out = {}
for t in (25, 50):
    r = []
    for d in sorted((LAB / "confirm/n29_raw").glob(f"*_at{t}_devcuda")):
        s = int(d.name.split("_seed")[1].split("_")[0]); f, g = ("A", "B") if f"w0_A_to_n29_seed{s}_w0_B" in d.name else ("B", "A")
        T = json.loads((LAB / f"confirm/n29_splits/n29_seed{s}_w0.json").read_text())["targets"]
        r.append(one(d, t, 4000, T[f], T[g]))
    r = np.array(r); out[f"N29@{t}"] = {"n": len(r), "old": round(r[:, 0].mean(), 3), "control": round(r[:, 1].mean(), 3)}
E59, E58, E56 = (next((LAB / "experiments").glob(f"EXP-0{n}*")) for n in (59, 58, 56))
for raw in (E59 / "raw", E58 / "raw"):
    for d in sorted(raw.glob("EXP-020_*_devcuda")):
        tail = d.name.rsplit("_devcuda", 1)[0].split("_at")[1]
        if not tail.isdigit():
            continue
        t = int(tail); s = int(d.name.split("_seed")[1].split("_")[0])
        f, g = ("A", "B") if f"w0_A_to_seed{s}_w0_B" in d.name else ("B", "A")
        T = json.loads((E56 / f"splits/seed{s}_w0.json").read_text())["targets"]
        out.setdefault(f"E59@{t}", []).append(one(d, t, 2000, T[f], T[g]))
for k in [k for k in out if k.startswith("E59")]:
    r = np.array(out[k]); out[k] = {"n": len(r), "old": round(r[:, 0].mean(), 3), "control": round(r[:, 1].mean(), 3)}
print(json.dumps(dict(sorted(out.items(), key=lambda x: (x[0][:3], int(x[0].split('@')[1])))), indent=0))
(LAB / "confirm/order_control.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
