"""R5 post hoc (session 55, reading fixed in JOURNAL S55 cycle 7 before computing): does the largest single-frequency power of the
split's M0 mask spectrum (mask_power, EXP-015) predict the R5 generalization time within an arm, in particular within the random
arm R? Spearman rho(max power, log2 b) per arm, censored times (8000) tied; one-sided permutation p (rho < 0). Reads R5_summary.json
and the split files only.
  python lab/confirm/R5_posthoc_maskpeak_s55.py
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lab/experiments/EXP-102-lm-ladder-stage1"))
sys.path.insert(0, str(ROOT / "lab/confirm"))
from flat_marginal_split_s45 import mask_power  # noqa: E402
from R5_posthoc_share_speed_s38 import spearman  # noqa: E402

ARMS = ("E8_0", "E2_0", "E2_1", "E1_0", "R", "D_0", "D_1")
N_PERM = 20000


def main() -> None:
    rows = json.loads((ROOT / "lab/confirm/R5_summary.json").read_text(encoding="utf-8"))["rows"]
    rng = np.random.default_rng(55)
    out, pool_x, pool_y = {}, [], []
    for arm in ARMS:
        x, y = [], []
        for r in rows:
            if r["technical"]:
                continue
            idx = np.load(ROOT / f"lab/confirm/r5_splits/r5_u{r['unit']}_{arm}.npy").astype(np.int64)
            x.append(float(mask_power(idx, "add", 113).max()))
            y.append(float(np.log2(r["times"][arm][0])))
        rho = spearman(x, y)
        perm = [spearman(x, rng.permutation(y)) for _ in range(N_PERM)]
        p = (1 + sum(v <= rho for v in perm)) / (N_PERM + 1)
        out[arm] = {"n": len(x), "rho": rho, "p_one_sided_less": p, "max_power_median": float(np.median(x)),
                    "max_power_range": [float(min(x)), float(max(x))], "n_censored": int(sum(v >= np.log2(8000) for v in y))}
        pool_x += x; pool_y += y
        print(arm, json.dumps(out[arm]), flush=True)
    out["pooled"] = {"n": len(pool_x), "rho": spearman(pool_x, pool_y)}
    rho_r, p_r = out["R"]["rho"], out["R"]["p_one_sided_less"]
    out["reading_R"] = ("Spitze sagt Tempo auch im Zufallsarm" if rho_r <= -0.4 and p_r < 0.05
                        else "nicht im Zufallsarm" if abs(rho_r) < 0.2 else "schwach")
    print("pooled", out["pooled"], "reading R:", out["reading_R"])
    Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
