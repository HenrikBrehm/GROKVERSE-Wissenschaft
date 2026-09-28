"""EXP-095 post hoc c (session 43, numpy on stored snapshots, seen data, exploration): does the arcsine law (Van Vleck) predict
how much target share an elementwise sign() removes from a W_E displacement?

For a zero-mean Gaussian process x along the token axis with circular autocorrelation rho(tau), sign(x) has autocorrelation
(2/pi) * arcsin(rho(tau)). So the spectrum of sign(D) can be PREDICTED from the spectrum of D alone, per column: target share
f_pred = sum of predicted power at the five targets / all non-constant frequencies. Applied to the n24 displacement D_n24 (the
surrogate of posthoc_sign_s43.py), compared with the measured f(sign(D_n24)) = f_bin. Columns are mean-centred along the
token axis before computing rho (the DC is excluded from f anyway). Also reported: the leading-term approximation
f_lin = (2/pi) f_n + (1 - 2/pi) * 5/56 (uniform spreading of the non-linear remainder), stated before computing as a rule of thumb.

Reading fixed HERE, BEFORE computing (session 43): cell mean |f_pred - f_bin| <= 0.01 -> 'Arkussinus erklaert';
<= 0.02 -> 'grob'; else 'nicht'. Same numbers for g24's own displacement are not meaningful (it is already sign).
Caveat: D columns are not Gaussian processes (few dominant cosines, 54 % of entries already full sign steps).
Writes posthoc_arcsine_s43.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import posthoc_sign_s43 as S  # noqa: E402  (loader, disp(), f_share(), power())

P = 113


def arcsine_power(D: np.ndarray) -> np.ndarray:
    """Predicted group power per frequency 1..(p-1)/2 of sign(D), each column scaled to unit variance."""
    X = D - D.mean(axis=0, keepdims=True)
    F = np.fft.fft(X, axis=0)
    ac = np.fft.ifft(np.abs(F) ** 2, axis=0).real          # circular autocovariance per column
    rho = np.clip(ac / ac[0:1], -1.0, 1.0)
    ac_out = (2 / np.pi) * np.arcsin(rho)                   # sign() autocorrelation (unit variance)
    S_out = np.fft.fft(ac_out, axis=0).real                 # predicted power spectrum per column (length p)
    k = np.arange(1, (P - 1) // 2 + 1)
    return (S_out[k] + S_out[P - k]).sum(axis=1)


def f_of(pw: np.ndarray, F: list[int]) -> float:
    return float(pw[[k - 1 for k in F]].sum() / pw.sum())


def main() -> None:
    rows = []
    for s in S.X.D.SEEDS:
        meta = json.loads((S.X.E.SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        tg = {"AB": meta["targets"]["A"], "BA": meta["targets"]["B"]}
        acc = {"f_n": [], "f_bin": [], "f_pred": [], "f_lin": []}
        for kind in ("AB", "BA"):
            n = S.X.load(s, kind, "n24")
            if isinstance(n, str):
                raise SystemExit(n)
            Dn, F = S.disp(n), tg[kind]
            fn = S.f_share(Dn, F)
            acc["f_n"].append(fn)
            acc["f_bin"].append(S.f_share(np.sign(Dn), F))
            acc["f_pred"].append(f_of(arcsine_power(Dn), F))
            acc["f_lin"].append((2 / np.pi) * fn + (1 - 2 / np.pi) * 5 / 56)
        rows.append({"seed": s, **{k: float(np.mean(v)) for k, v in acc.items()}})
    col = lambda k: np.array([r[k] for r in rows])   # noqa: E731
    m = {k: float(col(k).mean()) for k in ("f_n", "f_bin", "f_pred", "f_lin")}
    err = abs(m["f_pred"] - m["f_bin"])
    reading = "Arkussinus erklaert" if err <= 0.01 else "grob" if err <= 0.02 else "nicht"
    out = {"n": len(rows), "means": m, "abs_err_pred": err, "abs_err_lin": abs(m["f_lin"] - m["f_bin"]),
           "per_seed_abs_err_pred_mean": float(np.mean(np.abs(col("f_pred") - col("f_bin")))), "reading": reading, "per_seed": rows}
    (HERE / "posthoc_arcsine_s43.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "per_seed"}, indent=1))


if __name__ == "__main__":
    main()
