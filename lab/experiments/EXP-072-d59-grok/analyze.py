"""EXP-072 (pilot): does D59 generalise within 20000 steps, and do the steered irreps stay dominant? Definition: README.md (fixed before any run).
Reads result.json / spectra.npy of the group_train runs only (no forward passes). Run under guarded_run.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
SPL = LAB / "confirm" / "splits"
SEEDS, STEPS, GEN_ACC = range(1000, 1005), 20000, 0.9


def own_in_top5(spec: np.ndarray, targets: list[int]) -> int:
    top = set((np.argsort(-spec, kind="stable")[:5] + 1).tolist())   # index k-1 -> irrep k
    return len(top & set(targets))


def row(s: int, arm: str) -> dict:
    stem = f"confirm_exp1_eps2.0_D59_seed{s}_{arm}"
    d = HERE / "raw" / f"EXP-046_seed{s}_{stem}_devcuda"
    if not (d / "result.json").exists():
        return {"seed": s, "arm": arm, "status": "fehlt"}
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    targets = json.loads((SPL / f"{stem}.json").read_text(encoding="utf-8"))["targets"]
    spec, steps = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()
    acc = np.array(res["dense"]["test_acc"])
    at = lambda st: own_in_top5(spec[steps.index(st)], targets) if st in steps else None   # noqa: E731
    first = next((int(res["dense"]["test_steps"][i]) for i in range(len(acc)) if acc[i] >= GEN_ACC), None)
    return {"seed": s, "arm": arm, "status": res["status"], "steps": res["steps_completed"], "gen_step": res.get("generalization_step"),
            "first_test_ge_0.9": first, "final_test": float(acc[-1]), "own_top5_2000": at(2000), "own_top5_final": at(steps[-1]),
            "model": (d / "model_final.pt").exists()}


def main() -> None:
    rows = [row(s, a) for s in SEEDS for a in "FG"]
    ok = [r for r in rows if r["status"] == "completed" and r["steps"] == STEPS]
    gen = [r for r in ok if r["final_test"] >= GEN_ACC]
    out = {"n_completed": len(ok), "n_generalised_final": len(gen),
           "first_ge_0.9_median": float(np.median([r["first_test_ge_0.9"] for r in ok if r["first_test_ge_0.9"]])) if ok else None,
           "first_ge_0.9_max": max((r["first_test_ge_0.9"] or 0) for r in ok) if ok else None,
           "own_top5_2000_mean": float(np.mean([r["own_top5_2000"] for r in ok])) if ok else None,
           "own_top5_final_mean": float(np.mean([r["own_top5_final"] for r in ok])) if ok else None,
           "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
