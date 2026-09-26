"""EXP-044, descriptive (README Nachtrag session 14, written before any run; UNTESTED): continuous persistence pi per seed and t.

pi(t) = (L(t) - L(only G)) / (L(only F) - L(only G)), L = log[P(F targets) / P(G targets)] of the W_E power in the group basis at
the final step (EXP-043 group_power). Same run lookup and validity checks as analyze.py (shared loader). Compared with EXP-020
(add 113, ~73 % shared pairs): 0.41 / 0.74 / ~1.0 at t = 25 / 50 / 150. No verdict. Run under guarded_run.py (imports torch).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("exp044_analyze", HERE / "analyze.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)
REF_020 = {25: 0.41, 50: 0.74, 150: 1.0}


def final_power(task: str, p: int, s: int, kind: str) -> np.ndarray | None:
    st = HERE / f"splits/{task}{p}_seed{s}"
    switch = kind not in ("F", "G")
    budget = int(kind) + 2000 if switch else 2000
    L = A.load_run(A.find(task, p, s, kind),
                   A.Expect(seed=s, device=A.DEV, max_steps=budget, split_file=f"{st}_train_{'G' if kind == 'G' else 'F'}.npy",
                            test_file=f"{st}_test.npy", switch_file=f"{st}_train_G.npy" if switch else None,
                            config={"p": p, "task": task}, snapshots_at=(budget,)))
    return A.group_power(L.snapshot(budget), task, p)[0] if L.status == "ok" else None


def main() -> None:
    out: dict = {}
    for task, p in A.TASKS:
        rows = []
        for s in A.SEEDS:
            meta = json.loads((HERE / f"splits/{task}{p}_seed{s}.json").read_text(encoding="utf-8"))
            F, G = meta["targets"]["F"], meta["targets"]["G"]
            lr = lambda pw: float(np.log(pw[[k - 1 for k in F]].sum() / pw[[k - 1 for k in G]].sum()))   # noqa: E731
            pw = {k: final_power(task, p, s, k) for k in ("F", "G") + tuple(str(t) for t in A.SWITCH)}
            if any(v is None for v in pw.values()) or lr(pw["F"]) <= lr(pw["G"]):
                rows.append({"seed": s, "valid": False})
                continue
            lf, lg = lr(pw["F"]), lr(pw["G"])
            rows.append({"seed": s, "valid": True, "pi": {t: (lr(pw[str(t)]) - lg) / (lf - lg) for t in A.SWITCH}})
        v = [r for r in rows if r["valid"]]
        out[f"{task}{p}"] = {"rows": rows, "n_valid": len(v), "reference_EXP020": REF_020,
                             "pi_mean": {t: float(np.mean([r["pi"][t] for r in v])) for t in A.SWITCH} if v else None}
        print(task, p, out[f"{task}{p}"]["n_valid"], out[f"{task}{p}"]["pi_mean"], flush=True)
    (HERE / "pi_persistence.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
