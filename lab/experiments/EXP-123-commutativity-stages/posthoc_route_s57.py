"""EXP-123 post hoc (session 57, reading fixed in JOURNAL S57 cycle 6 before computing): W_E top-5 concentration C (energy share of
the 5 strongest frequencies of the additive DFT of W_E, add 113) at the last R5 spectrum snapshot <= t_swap, per arm (R, D_0, E2_0),
units with observed t_swap. Reading: 'gleicher Weg' if median C(R) >= 0.8 median C(E2_0), 'anderer Weg' if <= 0.5x, else 'unklar'.
Descriptive: C at step 0, C(R) at the last snapshot <= t_gen. Reads R5 raw spectra (lab/confirm/r5_raw) and EXP-123 summary.json.
  python lab/experiments/EXP-123-commutativity-stages/posthoc_route_s57.py
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = ROOT / "lab/confirm/r5_raw"


def conc(pw: np.ndarray) -> float:
    return float(np.sort(pw)[-5:].sum() / pw.sum())


def spectra(seed: int, u: int, arm: str) -> tuple[np.ndarray, np.ndarray]:
    ds = list(RAW.glob(f"EXP-018_baseline_seed{seed}_thr1_r5_u{u}_{arm}_devcuda"))
    assert len(ds) == 1, (seed, u, arm, ds)
    S, st = np.load(ds[0] / "spectra.npy"), np.load(ds[0] / "spectra_steps.npy")
    assert S.shape == (len(st), 56) and np.isfinite(S).all()
    return S, st


def at(S: np.ndarray, st: np.ndarray, t: int) -> float:
    i = int(np.searchsorted(st, t, side="right") - 1)
    return conc(S[i])


def main() -> None:
    rows = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))["rows"]
    out: dict = {}
    for arm in ("R", "D_0", "E2_0"):
        rs = [r for r in rows if r["arm"] == arm and r["status"] == "ok" and r["t_swap"]]
        c_sw, c0, c_gen = [], [], []
        for r in rs:
            S, st = spectra(r["seed"], r["unit"], arm)
            c_sw.append(at(S, st, r["t_swap"]))
            c0.append(conc(S[0]))
            if r["t_gen"]:
                c_gen.append(at(S, st, r["t_gen"]))
        out[arm] = {"n": len(rs), "C_tswap_median": float(np.median(c_sw)), "C_tswap_range": [min(c_sw), max(c_sw)],
                    "C_step0_median": float(np.median(c0)), "C_tgen_median": float(np.median(c_gen)) if c_gen else None,
                    "n_tgen": len(c_gen), "t_swap_median": float(np.median([r["t_swap"] for r in rs]))}
    ratio = out["R"]["C_tswap_median"] / out["E2_0"]["C_tswap_median"]
    out["ratio_R_over_E"] = ratio
    out["reading"] = "gleicher Weg" if ratio >= 0.8 else ("anderer Weg" if ratio <= 0.5 else "unklar")
    (HERE / "posthoc_route_s57.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
