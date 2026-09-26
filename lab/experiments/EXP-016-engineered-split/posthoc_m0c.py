"""Post hoc (session 5, exploratory, idea formed after seeing EXP-016 data): do the EXP-016 'misses' (learned
frequencies outside the target set) come from the coherent mask spectrum M0c of the engineered split?
Compares |K ∩ top5(M0)| (= targets) with |K ∩ top5(M0c)| and the M0c rank of the missed frequencies.
K = top-5 of W_E at step 2000. Reads finished runs only; no training."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "EXP-015-mask-spectrum"))
sys.path.insert(0, str(HERE.parent / "EXP-015-mask-spectrum/posthoc"))
import mask_spectrum as ms  # noqa: E402
from coherent_m0 import m0c  # noqa: E402
from make_split import mask_from_idx  # noqa: E402
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("a16", HERE / "analyze.py")   # avoid other EXP analyze.py on sys.path
a16 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a16)
RUN, top_at = a16.RUN, a16.top_at


def top(pw: np.ndarray, m: int = 5) -> set[int]:
    return {int(k) + 1 for k in np.argsort(-pw, kind="stable")[:m]}


rows = []
for s in range(10, 20):
    for arm, suf in (("F", ""), ("G", "_G")):
        d = Path(str(RUN).format(s=s, suffix=suf))
        if not (d / "result.json").exists():
            continue
        if json.loads((d / "result.json").read_text(encoding="utf-8"))["status"] != "completed":
            continue
        idx = np.load(HERE / f"splits/split_seed{s}_eps2.0{suf}.npy")
        M = mask_from_idx(idx)
        a, c = ms.m0(M), m0c(M)
        K = top_at(d, 2000)
        rank_c = np.argsort(np.argsort(-c, kind="stable"))
        tgt = set(json.loads((HERE / f"splits/split_seed{s}_eps2.0{suf}.json").read_text(encoding="utf-8"))["targets"])
        miss = sorted(K - tgt)
        rows.append({"seed": s, "arm": arm, "K": sorted(K), "targets": sorted(tgt), "top5_M0c": sorted(top(c)),
                     "ov_M0": len(K & top(a)), "ov_M0c": len(K & top(c)),
                     "missed": miss, "M0c_rank_of_missed": [int(rank_c[k - 1]) + 1 for k in miss],
                     "M0c_top10_hits_missed": sum(int(rank_c[k - 1]) < 10 for k in miss)})
for r in rows:
    print(r)
n_miss = sum(len(r["missed"]) for r in rows)
print(json.dumps({"runs": len(rows), "ov_M0_mean": float(np.mean([r["ov_M0"] for r in rows])),
                  "ov_M0c_mean": float(np.mean([r["ov_M0c"] for r in rows])), "n_missed": n_miss,
                  "missed_in_M0c_top10": sum(r["M0c_top10_hits_missed"] for r in rows),
                  "chance_top10_of_remaining": "10/51 per missed freq if uniform over non-target ranks"}))
(HERE / "posthoc_m0c.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
