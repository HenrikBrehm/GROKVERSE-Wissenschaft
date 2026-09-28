"""EXP-102, prediction before any run (session 44; numpy on the split files only): does the train-set conditional p(b | a)
carry power at the split's target frequencies (over the token a)? If yes, the "all positions" loss rewards target-frequency
features of a directly (the reason for the allnb control).

Measure per split: Q[a, b] = count(a, b) / count(a) (empirical p(b | a)), centred per row (minus 1/p... i.e. minus the row
mean); power over a: P(k) = sum_b |FFT_a(Qc)[k, b]|^2 + |FFT_a(Qc)[p-k, b]|^2, k = 1..56; share at T_F, at T_G.
Also the same for the marginal count(a) (the part of the signal that is only "how often a occurs"), and, descriptively,
in (a, c = a + b) coordinates: Qac[a, c] = Q[a, c - a] (the split weights are cos(2 pi k a / p + phi_k(c)), so the target
structure is exact at fixed c and scrambled at fixed b). With an untied output layer the b-prediction gradient on the
embedding of a follows Q[a, b] at fixed b, so the primary measure is the fixed-b one; this was noticed before computing.
Reading fixed here: "p(b|a) carries the targets" if, averaged over seeds 3800-3809, share_T_F(F) - share_T_F(R) >= 0.05
(chance for 5 of 56 frequencies is 0.089); report both arms and the marginal. Descriptive, not a test of EXP-102.

  python lab/experiments/EXP-102-lm-ladder-stage1/pba_spectrum_s44.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P = 113
SEEDS = range(3800, 3810)


def over_a(X: np.ndarray) -> np.ndarray:
    F = np.abs(np.fft.fft(X, axis=0)) ** 2
    pw = F.sum(axis=1) if X.ndim == 2 else F
    K = (P - 1) // 2
    return pw[1:K + 1] + pw[P - K:][::-1]


def share(pw: np.ndarray, S) -> float:
    return float(pw[[k - 1 for k in S]].sum() / pw.sum())


def main() -> None:
    rows = []
    for s in SEEDS:
        T = json.loads((HERE / "splits" / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        for arm in ("F", "G", "R"):
            idx = np.load(HERE / "splits" / f"seed{s}_{arm}.npy")
            C = np.zeros((P, P))
            C[idx // P, idx % P] = 1.0
            ca = C.sum(1)
            Q = C / ca[:, None]
            Qc = Q - Q.mean(1, keepdims=True)
            pq, pm = over_a(Qc), over_a(ca - ca.mean())
            a_ = np.arange(P)
            Qac = Qc[a_[:, None], (a_[None, :] - a_[:, None]) % P]           # Qac[a, c] = Qc[a, c - a]
            pac = over_a(Qac)
            rows.append({"seed": s, "arm": arm, "Q_TF": share(pq, T["F"]), "Q_TG": share(pq, T["G"]),
                         "marg_TF": share(pm, T["F"]), "marg_TG": share(pm, T["G"]),
                         "Qac_TF": share(pac, T["F"]), "Qac_TG": share(pac, T["G"])})
    summ = {}
    for arm in ("F", "G", "R"):
        r = [x for x in rows if x["arm"] == arm]
        summ[arm] = {k: float(np.mean([x[k] for x in r])) for k in ("Q_TF", "Q_TG", "marg_TF", "marg_TG", "Qac_TF", "Qac_TG")}
    diff = summ["F"]["Q_TF"] - summ["R"]["Q_TF"]
    out = {"rows": rows, "summary": summ, "Q_TF_F_minus_R": diff,
           "reading": "p(b|a) carries the targets" if diff >= 0.05 else "p(b|a) does not carry the targets (first look)"}
    (HERE / "pba_spectrum_s44.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
