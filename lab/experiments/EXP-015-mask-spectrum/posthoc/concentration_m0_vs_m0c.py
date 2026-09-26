"""Post hoc (session 5). H (before computing): the coherent mask spectrum M0c (transformer statistic) is more
concentrated than M0 (MLP statistic) on the same random splits: higher top-5 share and lower participation ratio.
Motivation: the study (RESULTS.md 16.4/16.5) finds ~4-5 key frequencies in the transformer vs ~11 in the MLP and leaves
open why. Pure computation on the split masks of seeds 0-17 (make_dataset, run through guarded_run.py)."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import mask_spectrum as ms  # noqa: E402
from coherent_m0 import m0c  # noqa: E402


def stats(pw: np.ndarray) -> dict:
    q = pw / pw.sum()
    return {"top5_share": float(np.sort(q)[-5:].sum()), "n_eff": float(1 / (q ** 2).sum()),
            "cv": float(pw.std() / pw.mean())}


rows = []
for s in range(18):
    M = ms.mask_matrix(s)
    rows.append({"seed": s, "M0": stats(ms.m0(M)), "M0c": stats(m0c(M))})
summ = {k: {"M0": float(np.mean([r["M0"][k] for r in rows])), "M0c": float(np.mean([r["M0c"][k] for r in rows])),
            "n_M0c_more_concentrated": int(sum((r["M0c"][k] < r["M0"][k]) if k == "n_eff" else (r["M0c"][k] > r["M0"][k])
                                               for r in rows))} for k in ("top5_share", "n_eff", "cv")}
print(json.dumps(summ, indent=1))
(HERE / "concentration_m0_vs_m0c.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1))
