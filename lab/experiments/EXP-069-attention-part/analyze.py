"""EXP-069 (pilot): pattern (W_Q, W_K) or value path (W_V, W_O)? Definition: README.md (registered before any run).
Reuses the EXP-067 analysis with other parts; normal (EXP-059) and rsattn (EXP-067) as comparison arms. Run under guarded_run.py.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
_spec = importlib.util.spec_from_file_location("exp067", LAB / "experiments/EXP-067-exclusion-part/analyze.py")
X = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(X)

PARTS = ("qk", "vo")
X.PARTS = PARTS + ("attn",)                            # function (EXP-064 style) also for the rsattn comparison arm
X.ARMS = {"normal": X.ARMS["normal"], "rsattn": X.ARMS["rsattn"]} | {f"rs{p}": (HERE / "raw", f"_rs{p}") for p in PARTS}
X.ARMS["rsattn"] = (LAB / "experiments/EXP-067-exclusion-part/raw", "_rsattn")


def main() -> None:
    rows = [X.seed_row(s) for s in X.B.SEEDS]
    ok = [r for r in rows if r["valid"]]
    out = {"n_valid": len(ok), "verdict": {}, "db": {}}
    for p in PARTS:
        db = np.array([r["b_normal"] - r[f"b_rs{p}"] for r in ok])
        out["verdict"][p] = X.classify(db)
        out["db"][p] = db.tolist()
    keys = [k for k in (ok[0] if ok else {}) if k.startswith(("a_", "b_", "accold_", "accnew_"))]
    out["mean"] = {k: float(np.mean([r[k] for r in ok if k in r])) for k in keys}
    out["rows"] = rows
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    assert set(X.ARMS) == {"normal", "rsattn", "rsqk", "rsvo"}
    assert X.ARMS["rsqk"][1] == "_rsqk" and X.ARMS["rsattn"][0].name == "raw"
    assert X.classify(np.r_[np.ones(8) * 2, 0, 0]) == "trägt den Ausschluss mit"
    print("[exp069] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
