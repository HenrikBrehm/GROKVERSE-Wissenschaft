"""EXP-063 (pilot): does resetting the rest of the network (or W_E) at the switch t = 50 lift the exclusion of new frequencies?
Definition: README.md (registered before any EXP-063 run). Run under guarded_run.py. a, b as EXP-062 (final spectra vs pure runs of EXP-056).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
_spec = importlib.util.spec_from_file_location("exp062", LAB / "experiments/EXP-062-rate-race/analyze.py")
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)
A, B = R.A, R.B
T = 50
ARMS = {"normal": (B.root_for(T), ""), "rsrest": (HERE / "raw", "_rsrest"), "rswe": (HERE / "raw", "_rswe")}


def run(s: int, first: str, second: str, arm: str) -> dict[int, np.ndarray] | str:
    root, suf = ARMS[arm]
    d = A.find_run(root, f"EXP-0*_baseline_seed{s}_thr*_{A.stem(s, B.OM, first)}_to_{A.stem(s, B.OM, second)}_at{T}{suf}{A.SUF}")
    if d is None:
        return f"{arm} {first}{second}: fehlt"
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    if res.get("status") != "completed" or res.get("steps_completed") != T + 2000:
        return f"{arm} {first}{second}: not completed"
    if arm != "normal" and res.get("events", {}).get("reset_at_switch", {}).get("which") != arm[2:]:
        return f"{arm} {first}{second}: reset not recorded"
    return R.spectra(d)


def classify(db: np.ndarray) -> str:
    if len(db) < 8:
        return "nicht auswertbar"
    if (db > 1).sum() >= 8:
        return "Ausschluss sitzt (auch) im Rest des Netzes"
    if (db < 0.5).sum() >= 8:
        return "Rest-Reset hebt den Ausschluss nicht auf"
    return "unklar"


def main() -> None:
    rows = []
    for s in B.SEEDS:
        meta = json.loads((A.SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        pure = {x: R.spectra(R.run_dir(s, x, None, None)) for x in "AB"}
        r, bad = {"seed": s}, []
        for arm in ARMS:
            aa, bb = [], []
            for first, second, own, new in (("A", "B", F, G), ("B", "A", G, F)):
                sw = run(s, first, second, arm)
                if isinstance(sw, str):
                    bad.append(sw)
                    continue
                a, b = R.split(sw, pure[second], own, new, T + 2000, 2000)
                aa.append(a)
                bb.append(b)
            if len(aa) == 2:
                r[f"a_{arm}"], r[f"b_{arm}"] = float(np.mean(aa)), float(np.mean(bb))
        r["valid"] = not bad
        if bad:
            r["reason"] = "; ".join(bad[:3])
        rows.append(r)
    ok = [r for r in rows if r["valid"]]
    db = np.array([r["b_normal"] - r["b_rsrest"] for r in ok])
    out = {"n_valid": len(ok), "verdict": classify(db), "db_rest": db.tolist(),
           "mean": {k: float(np.mean([r[k] for r in ok])) for k in ("a_normal", "b_normal", "a_rsrest", "b_rsrest", "a_rswe", "b_rswe")} if ok else {},
           "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    assert classify(np.ones(7) * 3) == "nicht auswertbar"
    assert classify(np.r_[np.ones(8) * 2, 0, 0]) == "Ausschluss sitzt (auch) im Rest des Netzes"
    assert classify(np.r_[np.zeros(8), 3, 3]) == "Rest-Reset hebt den Ausschluss nicht auf"
    assert classify(np.r_[np.ones(5) * 2, np.zeros(5)]) == "unklar"
    print("[exp063] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
