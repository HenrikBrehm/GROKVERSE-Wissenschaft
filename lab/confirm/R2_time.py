"""R2 descriptive time addendum (session 32, fixed BEFORE any R2 run; outside the R2 family and its code hashes).
Question: does the switch cost of N43 (a switch inside the lock-in window delays grokking more than one after it) hold at other
hyperparameters? R2 has only switch arms (no destination-only runs), so contrasts between switch times, per seed the mean over both
directions of log2 b(@t1) - log2 b(@t2), b = min(first test >= 0.95, 4000) from step 0; exact one-sided sign test over non-tied seeds.
  T1 (wd 0.3)  @25 slower than @50            ('gestützt' if p < 0.05)
  T2 (lr 2e-3) @12 slower than @50            ('gestützt' if p < 0.05)
  T3 (lr 2e-3) @25 vs @50, descriptive only    (a clock in summed learning rate would put 25 steps at lr 2e-3 near the standard 50,
                                               i.e. ~0; a step clock would give > 0; not a clean clock test, lr stays doubled after the switch)
Arms are read from result.json fields (seed, switch_step, config.lr / config.weight_decay, split_file ending _A.npy / _B.npy).
Run only after `confirm_r2.py --analyze` reported a complete block.   python lab/confirm/R2_time.py
"""
import json
import math
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
CAP = 4000


def cell_of(cfg: dict) -> str | None:
    if abs(cfg.get("lr", 0) - 0.002) < 1e-12 and abs(cfg.get("weight_decay", 0) - 1.0) < 1e-12:
        return "lr2"
    if abs(cfg.get("weight_decay", 0) - 0.3) < 1e-12 and abs(cfg.get("lr", 0) - 0.001) < 1e-12:
        return "wd03"
    return None


def sign(d: np.ndarray) -> dict:
    nz = d[np.abs(d) > 1e-9]
    k, n = int((nz > 0).sum()), len(nz)
    p = sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0
    return {"mean": float(d.mean()), "pos": k, "nonzero": n, "p_one_sided": p}


def main() -> None:
    R: dict = {}
    for f in (LAB / "confirm/r2_raw").glob("*/result.json"):
        r = json.loads(f.read_text(encoding="utf-8"))
        c = cell_of(r["config"])
        if r.get("status") != "completed" or c is None or r.get("switch_step") is None:
            continue
        dirn = "AB" if str(r["split_file"]).endswith("_A.npy") else "BA"
        g = (r.get("events") or {}).get("generalization_step")
        R.setdefault((c, r["seed"]), {})[(dirn, r["switch_step"])] = math.log2(min(g, CAP) if g is not None else CAP)

    def contrast(cell: str, t1: int, t2: int) -> dict:
        d = [((v[("AB", t1)] - v[("AB", t2)]) + (v[("BA", t1)] - v[("BA", t2)])) / 2
             for (c, _), v in R.items() if c == cell and all(k in v for k in (("AB", t1), ("AB", t2), ("BA", t1), ("BA", t2)))]
        return {"n_seeds": len(d), **sign(np.array(d))} if d else {"n_seeds": 0}

    out = {"T1_wd03_25_vs_50": contrast("wd03", 25, 50), "T2_lr2_12_vs_50": contrast("lr2", 12, 50), "T3_lr2_25_vs_50": contrast("lr2", 25, 50)}
    for k in ("T1_wd03_25_vs_50", "T2_lr2_12_vs_50"):
        out[k]["reading"] = ("nicht auswertbar" if out[k]["n_seeds"] < 25 else ("gestützt" if out[k]["p_one_sided"] < 0.05 else "nicht gestützt"))
    (LAB / "confirm/R2_time.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
