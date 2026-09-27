"""EXP-084 post hoc (session 32, after the pre-registered reading): is the early W_E target share (step 250, a state of the network)
a better predictor of the generalization time than the split's M0 target share, over all 80 runs? Stated before computing:
|Spearman(we_share_250, b)| > |Spearman(m0_share, b)|; censored runs share the last rank (b = cap). Also the same within the
concentrated arms only (eps >= 2, all observed), where the question is whether W_E at 250 adds anything beyond the arm.
  python lab/experiments/EXP-084-dose-curve/posthoc_mediator_s32.py
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def avg_rank(v):
    v = np.asarray(v, float)
    r = np.empty(len(v))
    s = np.sort(v)
    for x in np.unique(v):
        r[v == x] = np.mean(np.flatnonzero(s == x))
    return r


def spear(x, y):
    return float(np.corrcoef(avg_rank(x), avg_rank(y))[0, 1])


def main() -> None:
    rows = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))["rows"]
    runs = [(a, r[a]) for r in rows for a in r if a != "unit"]
    b = [x["b"] for _, x in runs]
    out = {"all_80": {"rho_we250": spear([x["we_share_250"] for _, x in runs], b), "rho_m0": spear([x["m0_target_share"] for _, x in runs], b)}}
    conc = [(a, x) for a, x in runs if a in ("e2", "e4", "e8", "e16", "e32")]
    bc = [x["b"] for _, x in conc]
    out["eps_ge_2"] = {"n": len(conc), "rho_we250": spear([x["we_share_250"] for _, x in conc], bc),
                       "rho_m0": spear([x["m0_target_share"] for _, x in conc], bc)}
    e1 = [x for a, x in runs if a == "e1"]
    out["e1_we250_mean"] = float(np.mean([x["we_share_250"] for x in e1]))
    out["prediction_met"] = abs(out["all_80"]["rho_we250"]) > abs(out["all_80"]["rho_m0"])
    (HERE / "posthoc_mediator_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
