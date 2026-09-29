"""EXP-102 equivalence check (session 47, written before the equivalence runs): does lm_ladder.py in rung r0 ("all off")
reproduce freq_ban.py on the same split (seeds 3800-3802, split F, 2000 steps, GPU, raw_equiv)?
Criterion (fixed before the runs): 'gleichwertig' if in all 3 seeds the relative Frobenius difference of W_E[:113] at step 2000
is <= 1e-3, OR the top-5 group-power frequencies are identical and |log(P_F/P_G)| differs by <= 0.2; otherwise 'abweichend'
(then the ladder pilot does not start; blocker in the README). Also reported: max relative difference at steps 50/250/1000.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-102-lm-ladder-stage1/equiv_compare.py
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
_spec = importlib.util.spec_from_file_location("exp043_analyze", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
_a43 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_a43)
RAW = HERE / "raw_equiv"


def snaps(d: Path) -> dict[int, np.ndarray]:
    W, S = np.load(d / "we_snapshots.npy"), np.load(d / "we_snapshot_steps.npy")
    return {int(s): w[:113].astype(np.float64) for s, w in zip(S, W)}


def main() -> None:
    rows, ok_all = [], True
    for s in (3800, 3801, 3802):
        T = json.loads((HERE / f"splits/seed{s}.json").read_text(encoding="utf-8"))["targets"]
        fb = [d for d in RAW.glob(f"EXP-016_baseline_seed{s}_thr1_seed{s}_F*") if d.is_dir()]
        ld = [d for d in RAW.glob(f"lad_seed{s}_seed{s}_F_op0_fs0_tie0_lossanswer_B0_steps2000_*") if d.is_dir()]
        assert len(fb) == 1 and len(ld) == 1, (s, fb, ld)
        for d in fb + ld:
            assert json.loads((d / "result.json").read_text(encoding="utf-8"))["status"] == "completed", d
        A, B = snaps(fb[0]), snaps(ld[0])
        rel = {t: float(np.linalg.norm(A[t] - B[t]) / np.linalg.norm(A[t])) for t in (50, 250, 1000, 2000) if t in A and t in B}
        pa, pb = (_a43.group_power(x[2000], "add", 113)[0] for x in (A, B))
        top = lambda pw: sorted(int(k) + 1 for k in np.argsort(pw)[-5:])   # noqa: E731
        lr = lambda pw: float(np.log(pw[[k - 1 for k in T["F"]]].sum() / pw[[k - 1 for k in T["G"]]].sum()))   # noqa: E731
        ok = rel.get(2000, 1.0) <= 1e-3 or (top(pa) == top(pb) and abs(lr(pa) - lr(pb)) <= 0.2)
        ok_all &= ok
        rows.append({"seed": s, "rel_diff": rel, "top5_freq_ban": top(pa), "top5_ladder": top(pb), "logratio_freq_ban": lr(pa),
                     "logratio_ladder": lr(pb), "ok": bool(ok)})
    out = {"reading": "gleichwertig" if ok_all else "abweichend", "rows": rows}
    (HERE / "equiv_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
