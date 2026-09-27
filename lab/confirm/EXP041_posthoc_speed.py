"""Post hoc (session 30), EXPLORATION: grokking speed of the pure E (engineered) and R (uniform random) arms that EXP-041 ran on the
EXP-018 splits (seeds 20-29, common held-out test set T*, CPU, 2150 steps). Checks split/test hashes against the EXP-018 files,
reports the trainer's generalization event (test >= 0.95), final test accuracy and the exact one-sided paired sign test over the seeds
whose order is determined (E crossed, R censored or later). Not pre-registered for this question; EXP-018 (arm D) decides the open part.

  python lab/confirm/EXP041_posthoc_speed.py
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "training"))
from grokverse.data import split_hash  # noqa: E402

RAW = ROOT / "lab/experiments/EXP-041-imprint/raw/EXP-018_baseline_seed{s}_thr4_seed{s}_train_{a}"
SPL = ROOT / "lab/experiments/EXP-018-split-speed/splits"


def main() -> None:
    rows, signs = [], []
    for s in range(20, 30):
        r = {}
        for a in "ER":
            res = json.loads((Path(str(RAW).format(s=s, a=a)) / "result.json").read_text(encoding="utf-8"))
            assert res["status"] == "completed" and res["seed"] == s
            assert res["split_hash"] == split_hash(np.load(SPL / f"seed{s}_train_{a}.npy"))
            assert res["test_hash"] == split_hash(np.load(SPL / f"seed{s}_test.npy"))
            r[a] = ((res.get("events") or {}).get("generalization_step"), res["steps_completed"], res["final_acc"]["test"])
        (ge, _, _), (gr, nr, _) = r["E"], r["R"]
        sign = (1 if ge is not None and (gr is None or ge < gr) else
                -1 if gr is not None and (ge is None or gr < ge) else None)
        signs.append(sign)
        rows.append({"seed": s, "E": r["E"], "R": r["R"], "order": sign})
        print(s, "E", r["E"], "R", r["R"], "order", sign)
    det = [x for x in signs if x is not None]
    k = sum(1 for x in det if x > 0)
    p = sum(__import__("math").comb(len(det), i) for i in range(k, len(det) + 1)) / 2 ** len(det)
    print(f"determined {len(det)}, E first {k}, exact one-sided sign test p = {p:.4f}")
    (ROOT / "lab/confirm/EXP041_posthoc_speed.json").write_text(json.dumps({"rows": rows, "determined": len(det), "E_first": k,
                                                                             "p_sign_one_sided": p}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
