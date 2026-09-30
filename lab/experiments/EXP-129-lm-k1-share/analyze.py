"""EXP-129 analysis (session 60, written before any run; readings in README "Vorab"). Primary: the EXP-116 rules
(EXP-105 analyze_pilot: Delta_pow on the 113 number-token rows at the last step; 'K2 haelt im LM' / 'nur Repraesentation' /
'bricht' / 'unklar'; precedence 'nicht gelernt (Budget)' if train-fact accuracy < 0.1 in >= 3 of 4 runs).
Secondary (clock: steps or repetitions?), per run with the EXP-116 run of the same model seed and split (K = 2) as partner:
a1 = held-out accuracy of the K = 1 run at 14 000; s = partner at the same STEP 14 000; e = partner at the same number of
EXPOSURES per fact (K = 2 shows twice as many facts per step: step 7 000). Each value is the mean of the three evaluations
ending there (13 500/13 750/14 000 resp. 6 500/6 750/7 000; review S60: single values are noisy). A run discriminates if |s - e| >= 0.2. Among
discriminating runs: 'Schritte' if |a1 - s| < |a1 - e| in >= 3 runs; 'Wiederholungen' if |a1 - e| < |a1 - s| in >= 3 runs;
otherwise (or fewer than 3 discriminating runs) 'unklar'. Evaluated only if the primary reading is not 'nicht gelernt (Budget)'
(then 'nicht auswertbar'): with a1 ~ 0 every run is trivially closer to e. Note: 'Wiederholungen' cannot separate
"repetitions per fact" from "half the arithmetic gradient per step" – operationally both are the same clock here. (A first draft used onset ratios; replaced before any run
because 'Wiederholungen' was unreachable within 14 000 steps.)
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-129-lm-k1-share/analyze.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-105-lm-ladder-stage2"))
import analyze_pilot as AP  # noqa: E402

SPL = "lab/experiments/EXP-102-lm-ladder-stage1/splits"
PAIRS = [f"3864:{SPL}/seed3804_F.npy,{SPL}/seed3804_G.npy", f"3865:{SPL}/seed3805_F.npy,{SPL}/seed3805_G.npy"]
STEPS = 14_000
WIN = lambda end: [end - 500, end - 250, end]                   # noqa: E731


def curves(root: Path) -> tuple[dict, dict, dict]:
    half, wraps, curve = {}, {}, {}
    for d in sorted(root.iterdir()):
        f = d / "result.json"
        if d.is_dir() and f.exists():
            res = json.loads(f.read_text(encoding="utf-8"))
            key = d.name.split("_steps")[0]                  # lm2_seed<model>_seed<split>_<F|G>
            half[key] = next((int(r[0]) for r in res["curve"] if r[2] >= 0.5), None)
            wraps[key] = res.get("text_wraps")
            curve[key] = {int(r[0]): float(r[2]) for r in res["curve"]}
    return half, wraps, curve


def clock(k1: dict, k2: dict) -> dict:
    rows, disc, v_s, v_e = {}, 0, 0, 0
    for key, c2 in k2.items():
        if key not in k1 or STEPS not in k1[key] or STEPS not in c2 or STEPS // 2 not in c2:
            rows[key] = None
            continue
        if any(x not in k1[key] for x in WIN(STEPS)) or any(x not in c2 for x in WIN(STEPS) + WIN(STEPS // 2)):
            rows[key] = None
            continue
        m = lambda c, end: sum(c[x] for x in WIN(end)) / 3            # noqa: E731
        a1, s, e = m(k1[key], STEPS), m(c2, STEPS), m(c2, STEPS // 2)
        d = abs(s - e) >= 0.2
        rows[key] = {"a1": a1, "same_step": s, "same_exposures": e, "discriminating": d}
        if d:
            disc += 1
            v_s += abs(a1 - s) < abs(a1 - e)
            v_e += abs(a1 - e) < abs(a1 - s)
    reading = ("unklar" if disc < 3 else "Schritte" if v_s >= 3 else "Wiederholungen" if v_e >= 3 else "unklar")
    return {"rows": rows, "n_discriminating": disc, "reading": reading}


def main() -> None:
    root = HERE / "raw_answer"
    argv, sys.argv = sys.argv, ["analyze_pilot.py", "--root", str(root), "--pairs", *PAIRS]
    try:
        AP.main()
    finally:
        sys.argv = argv
    out = json.loads((root / "pilot_summary.json").read_text(encoding="utf-8"))
    tr = [x for r in out["rows"] for x in r["train_acc"]]
    if sum(x < 0.1 for x in tr) >= len(tr) - 1:
        out["reading"] = "nicht gelernt (Budget)"
    k1, wraps, c1 = curves(root)
    k2, _, c2 = curves(LAB / "experiments/EXP-116-lm-low-share/raw_answer")
    out["first_step_heldout_ge_0.5"], out["exp116_first_step_heldout_ge_0.5"], out["text_wraps"] = k1, k2, wraps
    out["clock"] = clock(c1, c2) if out.get("reading") != "nicht gelernt (Budget)" else {"reading": "nicht auswertbar"}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
