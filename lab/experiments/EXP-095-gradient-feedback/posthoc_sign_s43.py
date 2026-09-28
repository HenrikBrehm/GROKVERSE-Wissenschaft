"""EXP-095 post hoc (session 43, window closed, numpy on stored snapshots only, seen data, exploration): is the g24 arm
('initial gradient only') really 'first order', or is its low target selectivity an artefact of Adam turning a frozen
gradient into elementwise SIGN steps?

Background: with a frozen gradient g0, Adam's bias-corrected moments are exactly m = g0, v = g0^2, so every pre-switch
step is lr * sign(g0) per element (plus decoupled weight decay). Sign quantisation of a column that is a sum of a few
Fourier modes along the token axis spreads power into other frequencies (harmonics / intermodulation). If that explains
the excess non-target motion of g24 (post hoc a: R x1.48), then EXP-095's statement 'the first-order picture explains
only a small part' is confounded: g24 is first order under signSGD, not under gradient flow.

Quantities per seed and direction (A->B uses targets F of A, B->A uses G of B, averaged as in posthoc_components_s42):
  D   = W_E(24) - (1 - lr*wd)^24 * W_E(0)     (displacement with the weight-decay drift of W_E(0) removed)
  f(X)= T / (T + R), group power of X along the token axis (targets T, all other frequencies R)
  f_n = f(D_n24), f_g = f(D_g24), f_bin = f(sign(D_n24))   (binarised fresh-gradient displacement as surrogate)

Readings fixed HERE, BEFORE computing (session 43, 2026-09-28):
  P1 precondition 'sign steps': share q of |D_g24| entries within 10 % of lr * sum_j (1-lr*wd)^j (j < 24, = 0.02372)
     is >= 0.8 in the cell mean; also reported for n24 (descriptive). If P1 fails, the other readings are not interpreted.
  P2 gap share x = (mean f_n - mean f_bin) / (mean f_n - mean f_g), bootstrap CI over seeds (10 000, rng 43):
     'Binarisierung erklaert'  mean x in [0.6, 1.4] and CI lower bound > 0.3
     'teilweise'               CI lower bound > 0 and mean x < 0.6
     'nicht'                   CI includes 0 (or mean x < 0.2)
     otherwise 'unklar' (e.g. x > 1.4: binarisation overshoots).
  Descriptive only: f_n, f_g, f_bin cell means; power share of the pure third harmonics {3k mod p} of the targets in R
  for D_g24 vs D_n24 vs sign(D_n24) (full third-order products cover 21-48 of 51 non-targets, too many to test).
Expectation (stated before computing): 'teilweise' to 'erklaert'. Caveat: sign(D_n24) is not sign(g0); D_n24 already
contains Adam sign steps and 23 later fresh gradients, so it is only a smooth-direction surrogate.
Writes posthoc_sign_s43.json. Reads snapshots through the EXP-095 loader (same gates as analyze.py).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze as X  # noqa: E402  (EXP-095 loader)

LR, WD, T_SW, P = 1e-3, 1.0, 24, 113
DECAY = (1 - LR * WD) ** T_SW
UNIT = LR * sum((1 - LR * WD) ** j for j in range(T_SW))


def power(W: np.ndarray) -> np.ndarray:
    return X.E.A._a43.group_power(W, "add", P)[0]


def f_share(W: np.ndarray, F: list[int]) -> float:
    pw = power(W)
    return float(pw[[k - 1 for k in F]].sum() / pw.sum())


def h3_share(W: np.ndarray, F: list[int]) -> float:
    pw = power(W)
    h3 = {min(3 * k % P, P - 3 * k % P) for k in F} - set(F) - {0}
    rest = pw.sum() - pw[[k - 1 for k in F]].sum()
    return float(pw[[k - 1 for k in sorted(h3)]].sum() / rest)


def boot_x(fn: np.ndarray, fb: np.ndarray, fg: np.ndarray, rng: np.random.Generator) -> list[float]:
    idx = rng.integers(0, len(fn), size=(10_000, len(fn)))
    num, den = fn[idx].mean(1) - fb[idx].mean(1), fn[idx].mean(1) - fg[idx].mean(1)
    x = num / den
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def disp(res) -> np.ndarray:
    _, W_t, W_0 = res
    return W_t.astype(np.float64) - DECAY * W_0.astype(np.float64)


def main() -> None:
    rows = []
    for s in X.D.SEEDS:
        meta = json.loads((X.E.SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        tg = {"AB": meta["targets"]["A"], "BA": meta["targets"]["B"]}
        acc = {k: [] for k in ("q_g", "q_n", "f_n", "f_g", "f_bin", "h3_n", "h3_g", "h3_bin")}
        for kind in ("AB", "BA"):
            n, g = X.load(s, kind, "n24"), X.load(s, kind, "g24")
            if isinstance(n, str) or isinstance(g, str):
                raise SystemExit(f"seed {s} {kind}: {n if isinstance(n, str) else g}")
            Dn, Dg, F = disp(n), disp(g), tg[kind]
            Db = UNIT * np.sign(Dn)
            acc["q_g"].append(float(np.mean(np.abs(np.abs(Dg) - UNIT) <= 0.1 * UNIT)))
            acc["q_n"].append(float(np.mean(np.abs(np.abs(Dn) - UNIT) <= 0.1 * UNIT)))
            for key, W in (("n", Dn), ("g", Dg), ("bin", Db)):
                acc[f"f_{key}"].append(f_share(W, F))
                acc[f"h3_{key}"].append(h3_share(W, F))
        rows.append({"seed": s, **{k: float(np.mean(v)) for k, v in acc.items()}})
    col = lambda k: np.array([r[k] for r in rows])   # noqa: E731
    fn, fg, fb = col("f_n"), col("f_g"), col("f_bin")
    x = float((fn.mean() - fb.mean()) / (fn.mean() - fg.mean()))
    ci = boot_x(fn, fb, fg, np.random.default_rng(43))
    q_g = float(col("q_g").mean())
    if q_g < 0.8:
        reading = "nicht interpretierbar (P1 verfehlt)"
    elif 0.6 <= x <= 1.4 and ci[0] > 0.3:
        reading = "Binarisierung erklaert"
    elif ci[0] <= 0 or x < 0.2:
        reading = "nicht"
    elif x < 0.6:
        reading = "teilweise"
    else:
        reading = "unklar"
    out = {"n": len(rows), "unit": UNIT, "P1_q_g24": q_g, "q_n24": float(col("q_n").mean()),
           "f_n24": float(fn.mean()), "f_g24": float(fg.mean()), "f_bin_n24": float(fb.mean()),
           "gap_share_x": x, "x_ci95": ci, "reading": reading,
           "h3_share_of_R": {k: float(col(f"h3_{k}").mean()) for k in ("n", "g", "bin")},
           "per_seed": rows}
    (HERE / "posthoc_sign_s43.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "per_seed"}, indent=1))


if __name__ == "__main__":
    main()
