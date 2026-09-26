"""EXP-045: does split steering (EXP-016) hold for the shared-embedding ReLU MLP (add mod 113)? UNTESTED (written out of window).

Per seed i (90-99): arms F and G (EXP-043 construction, add 113, eps 2), 10 000 steps each, GPU, --stop-after-gen large.
K = top-5 of W_E power (real DFT over Z_113, k = 1..56) from the W_E snapshot at step 10 000 (primary) and 2000 (secondary).
Delta_i and the one-sided sign-flip test as in EXP-016/043. Definition: README.md.
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
from grokverse.data import split_hash  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp043_analyze", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
_a43 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_a43)

SEEDS = range(90, 100)
PRIMARY, SECONDARY, ALPHA, MIN_VALID = 10_000, 2000, 0.05, 8


def K_at(d: Path, step: int) -> set[int] | None:
    steps = np.load(d / "we_snapshot_steps.npy").tolist()
    if step not in steps:
        return None
    W = np.load(d / "we_snapshots.npy")[steps.index(step)].astype(np.float64)
    if not np.isfinite(W).all():                        # s13: a diverged (NaN) run is invalid, not a silent K
        return None
    return _a43.top(_a43.group_power(W, "add", 113)[0])


def row(s: int) -> dict:
    r: dict = {"seed": s, "valid": False}
    T, K, K2, info = {}, {}, {}, {}
    for arm in "FG":
        stem = f"split_add113_seed{s}_eps2.0_{arm}"
        T[arm] = set(json.loads((HERE / f"splits/{stem}.json").read_text(encoding="utf-8"))["targets"])
        hits = sorted((HERE / "raw").glob(f"EXP-045_baseline_seed{s}_thr*_{stem}_mlp_*"))
        if len(hits) != 1 or not (hits[0] / "result.json").exists():   # Codex s12: died before first write -> invalid
            r["reason"] = f"arm {arm}: missing/ambiguous/no result.json"
            return r
        res = json.loads((hits[0] / "result.json").read_text(encoding="utf-8"))
        if (res["status"] != "completed" or res["steps_completed"] < PRIMARY or res["config"]["arch"] != "mlp"
                or res.get("device") != "cuda" or res["split_hash"] != split_hash(np.load(HERE / f"splits/{stem}.npy"))):
            r["reason"] = f"arm {arm}: status/steps/arch/device/hash"
            return r
        K[arm], K2[arm] = K_at(hits[0], PRIMARY), K_at(hits[0], SECONDARY)
        if K[arm] is None:
            r["reason"] = f"arm {arm}: no snapshot at {PRIMARY}"
            return r
        info[arm] = {"gen": res["events"].get("generalization_step"), "test_acc": res["final_acc"]["test"]}

    def delta(KK: dict) -> int:
        return len(KK["F"] & T["F"]) + len(KK["G"] & T["G"]) - len(KK["F"] & T["G"]) - len(KK["G"] & T["F"])
    r.update({"valid": True, "F": sorted(T["F"]), "G": sorted(T["G"]), "K_F": sorted(K["F"]), "K_G": sorted(K["G"]),
              "Delta": delta(K), "Delta_2000": delta(K2) if None not in K2.values() else None, "arms": info})
    return r


def main() -> None:
    rows = [row(s) for s in SEEDS]
    valid = [r for r in rows if r["valid"]]
    out: dict = {"rows": rows, "n_valid": len(valid)}
    if len(valid) < MIN_VALID:
        out["verdict"] = "nicht auswertbar"
    else:
        D = np.array([r["Delta"] for r in valid], dtype=float)
        pv = _a43.one_sided_p(D)
        d2 = [r["Delta_2000"] for r in valid if r["Delta_2000"] is not None]
        out.update({"Delta_mean": float(D.mean()), "p": pv, "n_positive": int((D > 0).sum()),
                    "Delta_2000_mean": float(np.mean(d2)) if d2 else None,
                    "verdict": "widerspricht" if D.mean() <= 0 else ("steuerbar" if pv < ALPHA
                                                                   else "richtungsgleich, nicht signifikant")})
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print({k: v for k, v in out.items() if k != "rows"})


if __name__ == "__main__":
    main()
