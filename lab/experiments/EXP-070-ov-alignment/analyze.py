"""EXP-070 (exploration): OV alignment of the attention with the targets of split A at t = 0, 10, 25, 50, 100 (pure A runs).
Definition: README.md (fixed before any run). Run under guarded_run.py.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB.parent / "training"))
_spec = importlib.util.spec_from_file_location("exp061", LAB / "experiments/EXP-061-grad-alignment/analyze.py")
G61 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G61)
SPL = LAB / "experiments/EXP-056-overlap-persistence/splits"
SEEDS, TS, P = range(400, 410), (10, 25, 50, 100), 113


def init_model(s: int):
    import torch
    from grokverse.config import get_config
    from grokverse.models import build_model
    from grokverse.seed import set_seed
    torch.set_num_threads(1)
    set_seed(s)
    return build_model(get_config("arch25k", seed=s, steps=10, threads=1))


def trained_model(s: int, t: int):
    import torch
    d = next((HERE / "raw" / f"t{t}").glob(f"EXP-018_baseline_seed{s}_thr1_seed{s}_w0_A_devcuda"))
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    assert res["status"] == "completed" and res["steps_completed"] == t, d
    m = init_model(s)
    m.load_state_dict(torch.load(d / "model_final.pt", map_location="cpu"))
    snap0 = np.load(d / "we_snapshots.npy")[list(np.load(d / "we_snapshot_steps.npy")).index(0)]
    return m, snap0


def measures(m, A: list[int], B: list[int]) -> dict:
    X = m.W_E.detach().numpy().astype(np.float64)[:P]
    WV, WO = m.W_V.detach().numpy().astype(np.float64), m.W_O.detach().numpy().astype(np.float64)
    OV = [WV[h] @ WO[h] for h in range(WV.shape[0])]
    def gain(S):
        PS = G61.project(X, S)
        return sum(float(((PS @ o) ** 2).sum()) for o in OV) / float((PS ** 2).sum())
    eA, eB = (float((G61.project(X, S) ** 2).sum()) for S in (A, B))
    return {"L": float(np.log(gain(A) / gain(B))), "E": float(np.log(eA / eB))}


def main() -> None:
    rows = []
    for s in SEEDS:
        meta = json.loads((SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        A, B = meta["targets"]["A"], meta["targets"]["B"]
        m0 = init_model(s)
        r = {"seed": s, "0": measures(m0, A, B)}
        for t in TS:
            m, snap0 = trained_model(s, t)
            assert np.allclose(snap0[:P], m0.W_E.detach().numpy()[:P], atol=1e-6), f"init mismatch seed {s}"   # rebuilt init == trainer init
            r[str(t)] = measures(m, A, B)
        rows.append(r)
    keys = ["0"] + [str(t) for t in TS]
    med = {k: {q: float(np.median([r[k][q] for r in rows])) for q in ("L", "E")} for k in keys}
    steps = {"L_10_25": float(np.median([r["25"]["L"] - r["10"]["L"] for r in rows])),
             "L_25_50": float(np.median([r["50"]["L"] - r["25"]["L"] for r in rows])),
             "E_10_25": float(np.median([r["25"]["E"] - r["10"]["E"] for r in rows])),
             "E_25_50": float(np.median([r["50"]["E"] - r["25"]["E"] for r in rows])),
             "n_L_rise_25_50_gt_10_25": int(sum((r["50"]["L"] - r["25"]["L"]) > (r["25"]["L"] - r["10"]["L"]) for r in rows))}
    out = {"median": med, "increments": steps, "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
