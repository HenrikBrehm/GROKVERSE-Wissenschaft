"""EXP-123 post hoc (session 55, reading fixed in JOURNAL S55 cycle 15 before computing): Spearman rho between the R5 W_E target
share at step 250 (R5_summary.json we_share_250) and log t_swap (EXP-123 summary.json) per arm and pooled over R, D_0, E2_0;
also rho with log t_gen for comparison. Reuses spearman() from lab/confirm/R5_posthoc_share_speed_s38.py.
  python lab/experiments/EXP-123-commutativity-stages/posthoc_share_tswap_s55.py
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "lab/confirm"))
from R5_posthoc_share_speed_s38 import spearman  # noqa: E402


def perm_p(x, y, rng, n=20000):
    rho = spearman(x, y)
    return rho, (1 + sum(spearman(x, rng.permutation(y)) <= rho for _ in range(n))) / (n + 1)


def main() -> None:
    r5 = {r["unit"]: r for r in json.loads((ROOT / "lab/confirm/R5_summary.json").read_text(encoding="utf-8"))["rows"]}
    e = {(r["unit"], r["arm"]): r for r in json.loads((HERE / "summary.json").read_text(encoding="utf-8"))["rows"]}
    rng = np.random.default_rng(1555)
    out, px, py = {}, [], []
    for arm in ("R", "D_0", "E2_0"):
        us = [u for u in range(20) if e[(u, arm)]["t_swap"]]
        x = [r5[u]["we_share_250"][arm] for u in us]
        y = [float(np.log2(e[(u, arm)]["t_swap"])) for u in us]
        rho, p = perm_p(x, y, rng)
        g = [u for u in us if e[(u, arm)]["t_gen"]]
        rho_gen = spearman([r5[u]["we_share_250"][arm] for u in g], [float(np.log2(e[(u, arm)]["t_gen"])) for u in g])
        out[arm] = {"n": len(us), "rho_tswap": rho, "p": p, "rho_tgen_generalized": rho_gen}
        px += x; py += y
        print(arm, out[arm], flush=True)
    out["pooled"] = {"n": len(px), "rho_tswap": spearman(px, py)}
    e2 = out["E2_0"]
    out["reading"] = ("Stufe 1 folgt der fruehen Zielenergie" if e2["rho_tswap"] <= -0.4 and e2["p"] < 0.05 and out["pooled"]["rho_tswap"] <= -0.6
                      else "nicht" if abs(e2["rho_tswap"]) < 0.2 else "schwach")
    print(out["pooled"], out["reading"])
    (HERE / "posthoc_share_tswap_s55.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
