"""EXP-030 analysis (pre-registered in README.md): does M0 predict final K beyond the step-250 W_E imprint?"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[0]
sys.path.insert(0, str(EXP / "EXP-015-mask-spectrum"))
from mask_spectrum import m0, mask_matrix  # noqa: E402

SEEDS = range(10, 20)


def rank(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x, kind="stable")
    r = np.empty(len(x))
    r[order] = np.arange(len(x), dtype=float)
    for v in np.unique(x):                       # average ties (k is binary)
        m = x == v
        r[m] = r[m].mean()
    return r


def corr(x: np.ndarray, y: np.ndarray) -> float:
    return float(np.corrcoef(x, y)[0, 1])


def partial(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float:
    rx, ry, rz = rank(x), rank(y), rank(z)
    Z = np.column_stack([np.ones_like(rz), rz])
    res = lambda v: v - Z @ np.linalg.lstsq(Z, v, rcond=None)[0]
    return corr(res(rx), res(ry))


def sign_flip_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def main() -> None:
    rows = []
    Ms = {s: m0(mask_matrix(s)) for s in SEEDS}
    for s in SEEDS:
        d = EXP / "EXP-003-early-prediction" / "raw_d" / f"EXP-001_baseline_t2000_m5_seed{s}_thr4"
        r = json.loads((d / "result.json").read_text())
        S, st = np.load(d / "spectra.npy"), list(np.load(d / "spectra_steps.npy"))
        K = r["final_top_m_freqs"]
        k = np.zeros(56); k[[f - 1 for f in K]] = 1.0
        M = Ms[s]
        row = {"seed": s, "K": K}
        for step in (250, 500, 1000):
            if step not in st:
                continue
            A = S[st.index(step)]
            row[f"rho_A{step}"] = corr(rank(A), rank(k))
            row[f"rho_M_given_A{step}"] = partial(M, k, A)
            row[f"rho_A{step}_given_M"] = partial(A, k, M)
        row["rho_M"] = corr(rank(M), rank(k))
        row["rho_M_foreign"] = float(np.mean([corr(rank(Ms[t]), rank(k)) for t in SEEDS if t != s]))
        rows.append(row)
    mean = lambda key: float(np.mean([x[key] for x in rows]))
    out = {"n": len(rows), "rows": rows, **{f"mean_{k}": mean(k) for k in rows[0] if k.startswith("rho")}}
    if out["mean_rho_M"] <= 0 or out["mean_rho_A250"] <= 0:
        out["verdict"] = "nicht auswertbar"
    else:
        dlt = np.array([x["rho_M"] - x["rho_M_given_A250"] for x in rows])
        p = sign_flip_p(dlt)
        half = out["mean_rho_M_given_A250"] <= 0.5 * out["mean_rho_M"]
        out.update(delta_mean=float(dlt.mean()), p_delta=p,
                   verdict="Rest gestützt" if p < 0.05 and half else "M0 wirkt auch direkt" if not half else "unklar")
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
