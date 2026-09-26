"""Post hoc (session 5, exploratory): coherent mask spectrum M0c vs M0.

W_E is shared by both input positions, so the first-gradient contributions of token t from the left pair (t, c-t)
and the right pair (c-t, t) should add coherently:  M0c(k) = sum_c |N_left^(k, c) + N_right^(k, c)|^2,
whereas M0 (EXP-015) adds their powers. H (stated before computing): rbar(M0c) < rbar(M0) on exploration seeds 0-9.
Seeds 10-17 are reported only as a labelled replication (they were already used to confirm M0).
Also: G0 (actual first gradient, EXP-012) vs both, where available. No training; reuses split reconstruction.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXP015 = HERE.parent
sys.path.insert(0, str(EXP015))
import mask_spectrum as ms  # noqa: E402
p12 = ms.p12


def m0c(M: np.ndarray) -> np.ndarray:
    p = M.shape[0]
    t = np.arange(p)
    other = (np.arange(p)[None, :] - t[:, None]) % p
    n = M[t[:, None], other] + M[other, t[:, None]]
    power = (np.abs(np.fft.fft(n, axis=0)) ** 2).sum(axis=1)
    K = (p - 1) // 2
    return power[1:K + 1] + power[p - K:][::-1]


def k_of(seed: int, k009: dict) -> list[int] | None:
    if seed < 10:
        return k009.get(seed)
    d = Path(str(p12.BASE_D).format(s=seed))
    if not (d / "result.json").exists():
        return None
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    return res["final_top_m_freqs"] if res["status"] == "completed" else None


def main() -> None:
    k009 = {}
    for r in json.loads(p12.EXP009.read_text(encoding="utf-8"))["runs"]:
        if r["run"].startswith("txf_add_p113_wd1.0_frac0.3_seed"):
            k009[int(r["run"].split("seed")[1].split("_")[0])] = r["k_final"]
    out = {}
    for name, seeds in (("exploration_0_9", range(0, 10)), ("replication_10_17", range(10, 18))):
        rows = []
        for s in seeds:
            K = k_of(s, k009)
            if K is None:
                continue
            M = ms.mask_matrix(s)
            a, c = ms.m0(M), m0c(M)
            rows.append({"seed": s, "rbar_M0": p12.rbar(a, K), "rbar_M0c": p12.rbar(c, K),
                         "spearman_M0_M0c": float(np.corrcoef(np.argsort(np.argsort(a)),
                                                              np.argsort(np.argsort(c)))[0, 1])})
        d = np.array([r["rbar_M0"] - r["rbar_M0c"] for r in rows])
        out[name] = {"n": len(rows), "rbar_M0": float(np.mean([r["rbar_M0"] for r in rows])),
                     "rbar_M0c": float(np.mean([r["rbar_M0c"] for r in rows])),
                     "p_M0c_better_signflip": p12.sign_flip_p(d),
                     "p_M0c_vs_null": p12.mc_null_p(float(np.mean([r["rbar_M0c"] for r in rows])), len(rows)),
                     "mean_spearman_M0_M0c": float(np.mean([r["spearman_M0_M0c"] for r in rows])), "rows": rows}
    (HERE / "coherent_m0.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    main()
