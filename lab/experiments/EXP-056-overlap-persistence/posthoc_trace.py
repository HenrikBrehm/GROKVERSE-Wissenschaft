"""EXP-056 post hoc (session 21, written AFTER seeing the EXP-056 result; descriptive only, no verdict): how much persistence pi would a
PASSIVE trace of the first 25 steps give?

pi is measured on W_E alone and all runs of a seed share one init, so the passive-trace prediction can be computed from saved snapshots:
  W_trace = W_E(pure second split, end) + c * (W_E(switch run, step 25) - W_E(step 0)),
c = (1 - lr * wd)^2000 = 0.999^2000 = 0.135 (AdamW decoupled decay alone) and c = 1 (upper bound: no decay at all).
pi_trace is computed like pi (EXP-056 analyze.logratio / pi_of) with L(A->B) replaced by L(W_trace). Run under guarded_run.py.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("exp056", HERE / "analyze.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)
C_DECAY = 0.999 ** 2000


def snap(d: Path, step: int) -> np.ndarray:
    steps = np.load(d / "we_snapshot_steps.npy").tolist()
    return np.load(d / "we_snapshots.npy")[steps.index(step)].astype(np.float64)


def run_dir(s: int, om: float, kind: str) -> Path:
    first, second = kind[0], kind[1:] or None
    pat = f"EXP-0*_baseline_seed{s}_thr*_{A.stem(s, om, first)}" + (f"_to_{A.stem(s, om, second)}_at{A.T_SWITCH}" if second else "") + A.SUF
    d = A.find_run(HERE / "raw", pat)
    if d is None:
        raise SystemExit(f"missing run {pat}")
    return d


def main() -> None:
    summ = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))
    out = []
    for r in summ["rows"]:
        if not r["valid"]:
            continue
        s = r["seed"]
        for om in A.OMEGAS:
            lv = r["levels"][str(om)]
            meta = json.loads((A.SPL / f"seed{s}_w{A.lvl(om)}.json").read_text(encoding="utf-8"))
            F, G = meta["targets"]["A"], meta["targets"]["B"]
            L = lv["L"]
            row = {"seed": s, "omega": om, "pi": lv["pi"]}
            for c_name, c in (("decay", C_DECAY), ("no_decay", 1.0)):
                pis = []
                for sw, pure, other in (("AB", "B", "A"), ("BA", "A", "B")):
                    dsw, dpure = run_dir(s, om, sw), run_dir(s, om, pure)
                    trace = snap(dsw, A.T_SWITCH) - snap(dsw, 0)
                    W = snap(dpure, A.BUDGET) + c * trace
                    pw = A._a43.group_power(W, "add", 113)[0]
                    Lt = A.logratio(pw, F, G)
                    pis.append((Lt - L[pure]) / (L[other] - L[pure]))
                row[f"pi_trace_{c_name}"] = float(np.mean(pis))
            out.append(row)
    res = {"C_DECAY": C_DECAY, "rows": out}
    for k in ("pi", "pi_trace_decay", "pi_trace_no_decay"):
        v = np.array([x[k] for x in out])
        res[f"{k}_mean"], res[f"{k}_max"] = float(v.mean()), float(v.max())
    (HERE / "posthoc_trace.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
