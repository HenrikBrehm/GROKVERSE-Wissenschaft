"""Post hoc (session 5, exploratory): predict harmonic-corrected K_h instead of W_E top-5 K with M0 / M0c.
K_h = top-5 of the final W_E spectrum after dropping frequencies that are fold(2k) of a stronger kept k (EXP-016 Nachtrag b).
H (before computing): rbar(M0c, K_h) < rbar(M0c, K). Seeds 0-9 (study final W_E spectra) and 10-17 (EXP-003d baselines)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import mask_spectrum as ms  # noqa: E402
from coherent_m0 import m0c  # noqa: E402

p12 = ms.p12
LAB = HERE.parents[2]
P, M = 113, 5


def fold(x: int) -> int:
    x %= P
    return min(x, P - x)


def k_and_kh(pw: np.ndarray) -> tuple[list[int], list[int]]:
    order = [int(j) + 1 for j in np.lexsort((np.arange(len(pw)), -pw))]
    kept: list[int] = []
    for k in order:
        if all(fold(2 * q) != k for q in kept):
            kept.append(k)
        if len(kept) == M:
            break
    return sorted(order[:M]), sorted(kept)


def final_power(s: int) -> np.ndarray | None:
    if s >= 10:
        d = Path(str(p12.BASE_D).format(s=s))
        return np.load(d / "spectra.npy")[-1]
    import torch
    sys.path.insert(0, str(LAB / "experiments/EXP-001-freq-ban"))
    import freq_ban as fb
    sd = torch.load(Path(str(p12.STORED).format(s=s)) / "model_final.pt", map_location="cpu")
    W = sd["W_E"].numpy().astype(np.float64)[:P]
    return fb.freq_power(W, fb.fourier_basis(P))


rows = []
for s in range(18):
    pw = final_power(s)
    K, Kh = k_and_kh(pw)
    Mk = ms.mask_matrix(s)
    a, c = ms.m0(Mk), m0c(Mk)
    rows.append({"seed": s, "K": K, "K_h": Kh, "changed": K != Kh,
                 "M0_K": p12.rbar(a, K), "M0_Kh": p12.rbar(a, Kh), "M0c_K": p12.rbar(c, K), "M0c_Kh": p12.rbar(c, Kh)})
out = {}
for grp, sel in (("seeds0_9", range(10)), ("seeds10_17", range(10, 18)), ("all", range(18))):
    R = [r for r in rows if r["seed"] in sel]
    d = np.array([r["M0c_K"] - r["M0c_Kh"] for r in R])
    out[grp] = {k: float(np.mean([r[k] for r in R])) for k in ("M0_K", "M0_Kh", "M0c_K", "M0c_Kh")}
    out[grp].update({"n_changed": sum(r["changed"] for r in R), "p_M0c_Kh_better": p12.sign_flip_p(d)})
for r in rows:
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
print(json.dumps(out, indent=1))
(HERE / "harmonic_corrected_k.json").write_text(json.dumps({"summary": out, "rows": rows}, indent=1), encoding="utf-8")
