"""EXP-086, pre-run check (session 33, pure numpy on the stored split files, no training): does A2 push W_E along the SAME first-order
directions as A at the target frequencies F, or only at the same frequencies?

First-order picture (paper draft par. 5): at init the W_E gradient of token t collects, per output class c, the mask entry of the pair that
puts t in the operand slot; its frequency-k content is X[k, c] = sum_t exp(-2 pi i k t / P) M(t, c - t) (left slot, and the same for the
right slot). With near-orthogonal random unembedding rows the d-dim gradient direction at k is set by the vector X[k, :] over c, so the
alignment of two splits at k is  rho_k = |<X_A[k, :], X_B[k, :]>| / (|X_A[k, :]| |X_B[k, :]|)  (both slots concatenated; modulus =
best phase-shifted match, i.e. an upper bound on the alignment a common token shift could give). Mean over k in F.
Reference pairs: A vs A2 (question), A vs B (other targets, EXP-056 omega 0), R1 vs R2 (uniform), A vs R1 (baseline for chance).

  python lab/experiments/EXP-086-same-spectrum-switch/gradient_overlap_s33.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-053-p3-overlap-design"))
import overlap_split as ov  # noqa: E402

P, SEEDS = 113, range(400, 410)
S56 = LAB / "experiments/EXP-056-overlap-persistence/splits"


def coeffs(idx: np.ndarray) -> np.ndarray:
    """X[k, (slot, c)] for k = 0..P-1: DFT over the token in each operand slot, for every output class c = a + b mod P."""
    M = np.zeros((P, P))
    M[idx // P, idx % P] = 1.0
    t, c = np.arange(P)[:, None], np.arange(P)[None, :]
    left, right = M[t, (c - t) % P], M[(c - t) % P, t]          # left[t, c] = M(t, c - t): token t as first operand
    return np.concatenate([np.fft.fft(left, axis=0), np.fft.fft(right, axis=0)], axis=1)


def rho(Xa: np.ndarray, Xb: np.ndarray, ks: list[int], signed: bool = False) -> float:
    """signed=False: modulus (best common phase); signed=True: real part = cosine of the two gradient directions as they are
    (added after the first output, before any EXP-086 run: disjoint splits of one pool carry each other's negative image)."""
    f = (lambda z: z.real) if signed else abs    # noqa: E731
    r = [f(np.vdot(Xa[k], Xb[k])) / (np.linalg.norm(Xa[k]) * np.linalg.norm(Xb[k])) for k in ks]
    return float(np.mean(r))


def main() -> None:
    rows = []
    for s in SEEDS:
        F, G = ov.targets(s)
        A, B = np.load(S56 / f"seed{s}_w0_A.npy"), np.load(S56 / f"seed{s}_w0_B.npy")
        A2, R1, R2 = (np.load(HERE / "splits" / f"seed{s}_{a}.npy") for a in ("A2", "R1", "R2"))
        X = {n: coeffs(v) for n, v in (("A", A), ("B", B), ("A2", A2), ("R1", R1), ("R2", R2))}
        rows.append({"seed": s, "A_A2_F": rho(X["A"], X["A2"], F), "A_B_F": rho(X["A"], X["B"], F), "A_R1_F": rho(X["A"], X["R1"], F),
                     "R1_R2_F": rho(X["R1"], X["R2"], F), "A_A2_G": rho(X["A"], X["A2"], G),
                     **{f"{a}_{b}_F_signed": rho(X[a], X[b], F, True) for a, b in (("A", "A2"), ("A", "B"), ("A", "R1"), ("R1", "R2"))},
                     "share_F": {n: ov.share(v, F) for n, v in (("A", A), ("A2", A2), ("B", B), ("R1", R1))}})
    keys = ("A_A2_F", "A_B_F", "A_R1_F", "R1_R2_F", "A_A2_G", "A_A2_F_signed", "A_B_F_signed", "A_R1_F_signed", "R1_R2_F_signed")
    summ = {k: {"mean": float(np.mean([r[k] for r in rows])), "min": float(np.min([r[k] for r in rows])),
                "max": float(np.max([r[k] for r in rows]))} for k in keys}
    out = {"summary": summ, "rows": rows}
    (HERE / "gradient_overlap_s33.json").write_bytes(json.dumps(out, indent=1).encode())
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
