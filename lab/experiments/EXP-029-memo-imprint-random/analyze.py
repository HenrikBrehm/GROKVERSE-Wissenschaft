"""EXP-029 analysis (pre-registered in README.md): mask-spectrum imprint in W_E during memorisation, baselines 10-19."""
from __future__ import annotations

import json
import sys
from math import comb
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[0]
sys.path.insert(0, str(EXP / "EXP-015-mask-spectrum"))
from mask_spectrum import m0, mask_matrix  # noqa: E402


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    return float(np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0, 1])


def main() -> None:
    rows = []
    for s in range(10, 20):
        d = EXP / "EXP-003-early-prediction" / "raw_d" / f"EXP-001_baseline_t2000_m5_seed{s}_thr4"
        r = json.loads((d / "result.json").read_text())
        if r.get("status") != "completed":
            continue
        S, st = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy")
        tr = r["transitions"]["primary"]
        mem, gen = tr["memorization"]["first_crossing_step"], tr["generalization"]["first_crossing_step"]
        M = m0(mask_matrix(s))
        rho = np.array([spearman(x, M) for x in S])
        win = np.flatnonzero((st >= mem) & (st < gen))
        if len(win) < 3:
            rows.append({"seed": s, "valid": False}); continue
        half = win[: len(win) // 2], win[len(win) // 2:]
        top_m = set(int(k) for k in np.argsort(-M)[:5] + 1)
        ov = lambda i: len(set(int(k) for k in np.argsort(-S[i])[:5] + 1) & top_m)
        rows.append({"seed": s, "valid": True, "mem": mem, "gen": gen, "n_window": int(len(win)),
                     "rho_init": float(rho[0]), "rho_memo": float(rho[win].mean()), "rho_end": float(rho[-1]),
                     "rho_memo_h1": float(rho[half[0]].mean()), "rho_memo_h2": float(rho[half[1]].mean()),
                     "argmax_step": int(st[int(np.argmax(rho))]), "ov_m0top5_memo": float(np.mean([ov(i) for i in win])),
                     "ov_m0top5_end": ov(len(st) - 1)})
    v = [x for x in rows if x["valid"]]
    out = {"n_valid": len(v), "rows": rows}
    if len(v) < 8:
        out["verdict"] = "nicht auswertbar"
    else:
        a = sum(x["rho_memo"] > x["rho_init"] for x in v)
        b = sum(x["rho_memo"] > x["rho_end"] for x in v)
        n = len(v)
        need = 9 if n == 10 else n            # pre-registered: >= 9 of 10; with fewer valid seeds all must hold
        mm = float(np.mean([x["rho_memo"] for x in v]))
        pa, pb = a >= need and mm >= 0.30, b >= need
        sign_p = lambda k: sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n
        out.update(n_memo_gt_init=a, n_memo_gt_end=b, p_a=sign_p(a), p_b=sign_p(b), mean_rho_memo=mm,
                   mean_rho_init=float(np.mean([x["rho_init"] for x in v])),
                   mean_rho_end=float(np.mean([x["rho_end"] for x in v])),
                   P29a=pa, P29b=pb, verdict="bestätigt" if pa and pb else "teilweise" if pa or pb else "nicht bestätigt")
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
