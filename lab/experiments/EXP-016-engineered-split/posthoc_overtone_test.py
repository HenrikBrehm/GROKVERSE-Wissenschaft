"""Post hoc (session 5, after Codex review): is the 2k mode in W_E an overtone of k or an independently used frequency?
Study models (seeds 0-9, 25k, model_final.pt), pairs (k, h = fold(2k)) both in the W_E top-5.
(1) Phase locking across embedding dimensions j: an overtone of a per-dimension waveform f_j(A_j cos(theta - phi_j)) has
    psi_j = 2 phi_j or 2 phi_j + pi (sign of the quadratic term), so the AXIAL resultant R2 = |mean_j exp(2i(psi_j - 2phi_j))|
    is large. Independent mode: R2 ~ 1/sqrt(n). Control: same statistic for (k, q) with q another top-5 member, not fold(2k).
    Only dims where both amplitudes exceed their median are used.
(2) Ablation: remove frequency h (resp. k, resp. a random non-top-5 frequency) from W_E[:p]; test loss/acc on the
    study test split. Inference only; run through guarded_run.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(ROOT / "training"))
sys.path.insert(0, str(LAB / "experiments/EXP-001-freq-ban"))
import freq_ban as fb  # noqa: E402
from grokverse.config import get_config  # noqa: E402
from grokverse.data import make_dataset  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.train import evaluate  # noqa: E402

P, M = 113, 5
B = fb.fourier_basis(P)


def fold(x: int) -> int:
    x %= P
    return min(x, P - x)


def phase_amp(W: np.ndarray, k: int, as_multiple: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Per-dimension phase and amplitude of frequency k. If as_multiple = m (k = fold(m)), express the phase for m
    (a folded frequency p - m flips the sine)."""
    c = B[:, 2 * k - 1] @ W
    s = B[:, 2 * k] @ W
    if as_multiple is not None and as_multiple % P > P // 2:
        s = -s
    return np.arctan2(s, c), np.hypot(c, s)


def axial_R(W: np.ndarray, k: int, q: int, mult: int) -> tuple[float, int]:
    phi, a = phase_amp(W, k)
    psi, b = phase_amp(W, q, as_multiple=mult * k)
    sel = (a > np.median(a)) & (b > np.median(b))
    d = psi[sel] - mult * phi[sel]
    return float(np.abs(np.mean(np.exp(2j * d)))), int(sel.sum())


def main() -> None:
    rng = np.random.default_rng(0)
    rows = []
    for s in range(10):
        cfg = get_config("arch25k", seed=s)
        model = build_model(cfg)
        sd = torch.load(ROOT / f"training/runs/txf_add_p113_wd1.0_frac0.3_seed{s}_arch25k/model_final.pt",
                        map_location="cpu")
        model.load_state_dict(sd)
        data = make_dataset(cfg)
        W = model.W_E.detach().numpy().astype(np.float64)[:P]
        pw = fb.freq_power(W, B)
        K = [int(j) + 1 for j in np.argsort(-pw, kind="stable")[:M]]
        base = evaluate(model, data["test_x"], data["test_y"], P)

        def ablate(freq: int) -> tuple[float, float]:
            proj = torch.tensor(fb.ban_projector(B, [freq]), dtype=model.W_E.dtype)
            W0 = model.W_E.detach().clone()
            with torch.no_grad():
                model.W_E[:P] = proj @ model.W_E[:P]
            out = evaluate(model, data["test_x"], data["test_y"], P)
            with torch.no_grad():
                model.W_E.copy_(W0)
            return out

        for k in K:
            h = fold(2 * k)
            if h not in K:
                continue
            others = [q for q in K if q not in (k, h)]
            ctrl_R = [axial_R(W, k, q, 2)[0] for q in others]
            nonK = [j for j in range(1, 57) if j not in K]
            rnd = int(rng.choice(nonK))
            R2, n = axial_R(W, k, h, 2)
            rows.append({"seed": s, "k": k, "h": h, "power_ratio_h_over_k": float(pw[h - 1] / pw[k - 1]),
                         "R2_phase_lock": R2, "n_dims": n, "R2_control_mean": float(np.mean(ctrl_R)),
                         "loss_base": base[0], "acc_base": base[1],
                         "ablate_h": ablate(h), "ablate_k": ablate(k), "ablate_random_nonK": (rnd, *ablate(rnd)),
                         "ablate_other_K": [(q, *ablate(q)) for q in others]})
    for r in rows:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
    summ = {"n_pairs": len(rows), "R2_mean": float(np.mean([r["R2_phase_lock"] for r in rows])),
            "R2_control_mean": float(np.mean([r["R2_control_mean"] for r in rows])),
            "dloss_h_mean": float(np.mean([r["ablate_h"][0] - r["loss_base"] for r in rows])),
            "dloss_k_mean": float(np.mean([r["ablate_k"][0] - r["loss_base"] for r in rows])),
            "dloss_otherK_mean": float(np.mean([np.mean([o[1] for o in r["ablate_other_K"]]) - r["loss_base"]
                                                for r in rows])),
            "dloss_random_mean": float(np.mean([r["ablate_random_nonK"][1] - r["loss_base"] for r in rows]))}
    print(json.dumps(summ, indent=1))
    (HERE / "posthoc_overtone_test.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1))


if __name__ == "__main__":
    main()
