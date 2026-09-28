"""EXP-100 / L0, first-order prediction BEFORE the pilot (session 44; numpy on split files only, no training, no outcomes).

Idea: the choice of frequencies is made within the first ~25-50 steps (K4, K5). At first order, what W_E has been pushed
towards by then is the SUM of the per-step first-order mask terms of the batches seen so far (momentum only delays it).
Under a fixed stride order (sorted by (a mod 10, a), LeDoux 2026) the early batches cover only a few residue classes of a,
so the cumulative push over the first L steps carries power at the order frequencies O = {11, 12, 22, 23, 34, 45}, but
only while L is short compared with an epoch (n / B steps: 15 at B = 256, 60 at B = 64). Over whole epochs the stride
push equals the set's push. Hypothesis H-window: the order can only compete with the set when an epoch is longer than
the lock-in window.

Computation per seed (EXP-100 splits 3700-3707, arms F and R) and regime (B = 256, 64; order stride / iid (mean over 20
random permutations) / full batch): cumulative push C_L = sum_{s<=L} (1/|B_s|) mask(B_s) for L = 25, 50; its M0 spectrum
(make_split.mask_power of EXP-043, i.e. left+right label-coded masks, FFT over the token axis, k = 1..56, with pair
multiplicity); shares of the power at O and at the split's own targets T_F.
Prediction rule (fixed here, before computing): the order "can act" in a regime if, averaged over seeds on the random
split R, the O-share excess of stride over iid at L = 50 is at least half of the target-share excess of the engineered
split F over chance (mean share_T(F, full batch) - 5/56). Otherwise "order washed out at first order". This yields a
prediction for the feasibility step and the conflict arm; it is not a test (first order, no Adam normalization).

  python lab/experiments/EXP-100-set-vs-order/firstorder_window_s44.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
P = 113
O = (11, 12, 22, 23, 34, 45)
SEEDS = range(3700, 3708)
LS = (25, 50)
BS = (256, 64)
N_IID = 20


def spectrum(counts: np.ndarray) -> np.ndarray:
    """M0 power (k = 1..56) of a pair-count matrix counts[a, b] (multiplicity allowed), same algebra as mask_power."""
    t = np.arange(P)
    other = (t[None, :] - t[:, None]) % P                 # other[t, c] = c - t
    left, right = counts[t[:, None], other], counts[other, t[:, None]]
    pw = (np.abs(np.fft.fft(left, axis=0)) ** 2 + np.abs(np.fft.fft(right, axis=0)) ** 2).sum(axis=1)
    K = (P - 1) // 2
    return pw[1:K + 1] + pw[P - K:][::-1]


def share(pw: np.ndarray, S) -> float:
    return float(pw[[k - 1 for k in S]].sum() / pw.sum())


def cumulative(idx_order: np.ndarray, B: int, L: int) -> np.ndarray:
    """Sum over the first L batches of (1/|batch|) * pair counts; epochs repeat the given order (stride) ."""
    C = np.zeros((P, P))
    n, pos = len(idx_order), 0
    for _ in range(L):
        if pos >= n:
            pos = 0
        bi = idx_order[pos:pos + B]
        pos += B
        np.add.at(C, (bi // P, bi % P), 1.0 / len(bi))
    return C


def cumulative_iid(idx: np.ndarray, B: int, L: int, rng: np.random.Generator) -> np.ndarray:
    C = np.zeros((P, P))
    n, pos, perm = len(idx), len(idx), None
    for _ in range(L):
        if pos >= n:
            perm, pos = idx[rng.permutation(n)], 0
        bi = perm[pos:pos + B]
        pos += B
        np.add.at(C, (bi // P, bi % P), 1.0 / len(bi))
    return C


def main() -> None:
    sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
    from make_split import mask_power                      # cross-check of spectrum() on 0/1 masks
    rng = np.random.default_rng(44)
    rows = []
    for s in SEEDS:
        meta = json.loads((HERE / "splits" / f"seed{s}.json").read_text(encoding="utf-8"))
        TF = meta["targets"]["F"]
        for arm in ("F", "R"):
            idx = np.load(HERE / "splits" / f"seed{s}_{arm}.npy")
            M = np.zeros((P, P))
            M[idx // P, idx % P] = 1.0
            full = spectrum(M)
            assert np.allclose(full, mask_power(idx, "add", P)), "spectrum() differs from mask_power on a 0/1 mask"
            a = idx // P
            stride = idx[np.lexsort((np.arange(len(idx)), a, a % 10))]      # as trainer_l0.patch (ties: file order)
            for B in BS:
                for L in LS:
                    st = spectrum(cumulative(stride, B, L))
                    ii = np.mean([spectrum(cumulative_iid(idx, B, L, rng)) for _ in range(N_IID)], axis=0)
                    rows.append({"seed": s, "arm": arm, "B": B, "L": L, "epochs": L * B / len(idx),
                                 "O_stride": share(st, O), "O_iid": share(ii, O), "O_full": share(full, O),
                                 "T_stride": share(st, TF), "T_iid": share(ii, TF), "T_full": share(full, TF)})
    out = {"rows": rows, "summary": {}}
    tF = np.mean([r["T_full"] for r in rows if r["arm"] == "F" and r["B"] == 256 and r["L"] == 25])
    set_excess = tF - 5 / 56
    for B in BS:
        for L in LS:
            sel = [r for r in rows if r["arm"] == "R" and r["B"] == B and r["L"] == L]
            selF = [r for r in rows if r["arm"] == "F" and r["B"] == B and r["L"] == L]
            ex = float(np.mean([r["O_stride"] - r["O_iid"] for r in sel]))
            out["summary"][f"B{B}_L{L}"] = {
                "epochs_in_window": L * B / 3831, "O_excess_stride_vs_iid_R": ex,
                "O_share_iid_R": float(np.mean([r["O_iid"] for r in sel])),
                "T_share_F_stride": float(np.mean([r["T_stride"] for r in selF])),
                "T_share_F_iid": float(np.mean([r["T_iid"] for r in selF])),
                "prediction": ("order can act" if ex >= 0.5 * set_excess else "order washed out at first order") if L == 50 else None}
    out["set_target_excess_F"] = float(set_excess)
    (HERE / "firstorder_window_s44.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out["summary"], indent=1), "\nset target excess (F, full batch):", round(set_excess, 4))


if __name__ == "__main__":
    main()
