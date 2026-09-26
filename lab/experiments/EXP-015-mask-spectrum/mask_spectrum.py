"""EXP-015: does the train-split mask alone predict the final frequency set?

M0(k) = sum_c |sum_t N_left(t,c) w^{-kt}|^2 + |sum_t N_right(t,c) w^{-kt}|^2,  w = exp(2 pi i / p),
N_left(t,c) = 1 if (t, c-t) is a training pair, N_right(t,c) = 1 if (c-t, t) is.
k and p-k are combined (k = 1..56). Definition: README.md. Run through guarded_run.py.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB.parent / "training"))
sys.path.insert(0, str(LAB / "experiments/EXP-012-init-gradient"))

import predict as p12  # noqa: E402
from grokverse.config import get_config  # noqa: E402
from grokverse.data import make_dataset  # noqa: E402


def mask_matrix(seed: int) -> np.ndarray:
    cfg = get_config("arch25k", seed=seed)
    data = make_dataset(cfg)
    p = cfg.p
    M = np.zeros((p, p))
    x = data["train_x"].numpy()
    M[x[:, 0], x[:, 1]] = 1.0            # M[a, b] = 1 if (a, b) is a training pair
    return M


def m0(M: np.ndarray) -> np.ndarray:
    p = M.shape[0]
    t = np.arange(p)
    c = np.arange(p)
    other = (c[None, :] - t[:, None]) % p                  # [t, c] -> c - t
    n_left = M[t[:, None], other]                          # (t, c-t) in train
    n_right = M[other, t[:, None]]                         # (c-t, t) in train
    power = (np.abs(np.fft.fft(n_left, axis=0)) ** 2 + np.abs(np.fft.fft(n_right, axis=0)) ** 2).sum(axis=1)
    K = (p - 1) // 2
    return power[1:K + 1] + power[p - K:][::-1]            # combine k and p-k


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", type=int, choices=(1, 2), required=True)
    a = ap.parse_args()
    k009 = {}
    for r in json.loads(p12.EXP009.read_text(encoding="utf-8"))["runs"]:
        if r["run"].startswith("txf_add_p113_wd1.0_frac0.3_seed"):
            k009[int(r["run"].split("seed")[1].split("_")[0])] = r["k_final"]
    rows = []
    for s in (range(0, 10) if a.phase == 1 else range(10, 20)):
        if a.phase == 1:
            K = k009[s]
        else:
            d = Path(str(p12.BASE_D).format(s=s))
            if not (d / "result.json").exists():
                rows.append({"seed": s, "valid": False, "reason": "baseline missing"})
                continue
            res = json.loads((d / "result.json").read_text(encoding="utf-8"))
            if res["status"] != "completed":
                rows.append({"seed": s, "valid": False, "reason": res["status"]})
                continue
            K = res["final_top_m_freqs"]
        pw = m0(mask_matrix(s))
        top = sorted((np.argsort(-pw, kind="stable")[:5] + 1).tolist())
        row = {"seed": s, "valid": True, "K": K, "M0_top5": top, "ov": len(set(top) & set(K)),
               "rbar_M0": p12.rbar(pw, K)}
        if a.phase == 2:                 # Nachtrag a/b: secondaries E0, G0, log E0 + log M0
            pr = p12.init_predictors(s)[0]
            row["rbar_logprod"] = p12.rbar(np.log(pr["E0"]) + np.log(pw), K)
            row["rbar_E0"], row["rbar_G0"] = p12.rbar(pr["E0"], K), p12.rbar(pr["G0"], K)
        rows.append(row)
    valid = [r for r in rows if r["valid"]]
    out: dict = {"phase": a.phase, "rows": rows, "n_valid": len(valid)}
    if len(valid) >= p12.MIN_VALID:
        rb = float(np.mean([r["rbar_M0"] for r in valid]))
        p = p12.mc_null_p(rb, len(valid))
        out.update({"rbar_M0": rb, "p_vs_null": p, "ov_mean": float(np.mean([r["ov"] for r in valid]))})
        if a.phase == 2:
            # Nachtrag b (Codex review): co-primary matched vs foreign masks, permutation over mask assignment
            vs = [r["seed"] for r in valid]
            masks = {m: m0(mask_matrix(m)) for m in vs}
            R = np.array([[p12.rbar(masks[m], r["K"]) for m in vs] for r in valid])
            rng = np.random.default_rng(0)
            null = np.array([R[np.arange(len(vs)), rng.permutation(len(vs))].mean() for _ in range(20000)])
            p_perm = float((np.sum(null <= np.trace(R) / len(vs) - 1e-12) + 1) / (len(null) + 1))
            out["foreign_mask"] = {"rbar_foreign_mean": float((R.sum() - np.trace(R)) / (len(vs) * (len(vs) - 1))),
                                   "p_perm": p_perm}
            out["verdict"] = "bestätigt" if p < p12.ALPHA and p_perm < p12.ALPHA else "nicht bestätigt"
            for name in ("E0", "G0"):
                d = np.array([r[f"rbar_{name}"] - r["rbar_M0"] for r in valid])
                out[f"secondary_vs_{name}"] = {"rbar": float(np.mean([r[f"rbar_{name}"] for r in valid])),
                                               "p_M0_better": p12.sign_flip_p(d)}
            diff = np.array([r["rbar_M0"] - r["rbar_logprod"] for r in valid])
            out["secondary_logprod"] = {"rbar": float(np.mean([r["rbar_logprod"] for r in valid])),
                                        "p_better_than_M0": p12.sign_flip_p(diff)}
    else:
        out["verdict"] = "nicht auswertbar"
    (HERE / f"summary_phase{a.phase}.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})


if __name__ == "__main__":
    main()
