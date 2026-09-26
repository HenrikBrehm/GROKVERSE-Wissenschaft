"""EXP-023 (design after Nachtrag a): with a position-specific value matrix, does M0c lose its advantage over M0?
(UNTESTED on real runs.) Fresh seeds 50-59; arms base / rand / copy; all runs exactly STEPS = 3000 steps (intention to
treat, no early stop); K = W_E top-5 at step 3000. Primary: Delta_d = [rbar_rand(M0c) - rbar_rand(M0)] -
[rbar_base(M0c) - rbar_base(M0)] > 0, one-sided sign-flip over seeds. Secondary: the same for 'copy' (expected ~ 0) and a
manipulation check (first-gradient cross-term vs mask cross-term for base and rand at init). Definition: README.md.
Uses make_dataset and one backward pass per seed: run through guarded_run.py."""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-015-mask-spectrum"))
sys.path.insert(0, str(LAB / "experiments/EXP-015-mask-spectrum/posthoc"))
sys.path.insert(0, str(HERE))
import mask_spectrum as ms  # noqa: E402
import positional_gradient as pg  # noqa: E402
import split_value as sv  # noqa: E402
from coherent_m0 import m0c  # noqa: E402
from value_path_intervention import forward_split_value  # noqa: E402

p12 = ms.p12
SEEDS, STEPS, MIN_VALID, ALPHA, P = range(50, 60), 3000, 8, 0.05, 113
RUN = {"base": HERE / "raw/EXP-001_baseline_t2000_m5_seed{s}_thr4",
       "rand": HERE / "raw/EXP-023_baseline_t2000_m5_seed{s}_thr4_svrand",
       "copy": HERE / "raw/EXP-023_baseline_t2000_m5_seed{s}_thr4_svcopy"}
WANT_SV = {"base": None, "rand": "rand", "copy": "copy"}


def load(s: int, arm: str) -> tuple[tuple | None, str | None]:
    d = Path(str(RUN[arm]).format(s=s))
    if not (d / "result.json").exists():
        return None, "missing"
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    want = {"status": "completed", "seed": s, "condition": "baseline", "max_steps": STEPS, "steps_completed": STEPS,
            "stop_after_generalization": 100000, "split_value": WANT_SV[arm], "split_file": None, "split_seed": None}
    for k, v in want.items():
        if res.get(k) != v:
            return None, f"{k}={res.get(k)!r}, expected {v!r}"
    spec, steps = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()
    if STEPS not in steps:
        return None, "no spectrum at 3000"
    pw = spec[steps.index(STEPS)]
    return (res, sorted(int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:5])), None


def cross_rho(s: int, variant: str | None) -> float:
    """First-gradient positional cross-term vs mask cross-term for the exact converted model at init."""
    cfg = pg.get_config("arch25k", seed=s, threads=4)
    torch.set_num_threads(4)
    pg.set_seed(cfg.seed)
    data = pg.make_dataset(cfg)
    model = pg.build_model(cfg)
    if variant is not None:
        model = sv.convert(model, s, variant)
    x, y = data["train_x"], data["train_y"]
    e = model.W_E[x].detach().requires_grad_(True)
    out = forward_split_value(model, e, model.W_V1 if variant else None, None)
    F.cross_entropy(out[:, -1, :P], y).backward()
    d = model.W_E.shape[1]
    GL = torch.zeros(P, d).index_add_(0, x[:, 0], e.grad[:, 0])
    GR = torch.zeros(P, d).index_add_(0, x[:, 1], e.grad[:, 1])
    B = pg.fb.fourier_basis(P)
    PL, PR, PS = (pg.fb.freq_power(G.detach().numpy().astype(np.float64), B) for G in (GL, GR, GL + GR))
    M = ms.mask_matrix(s)
    return pg.rho(PS - PL - PR, m0c(M) - ms.m0(M))


def row(s: int) -> dict:
    r: dict = {"seed": s, "valid": False}
    got = {}
    for arm in RUN:
        x, err = load(s, arm)
        if err:
            r["reason"] = f"{arm}: {err}"
            return r
        got[arm] = x
    sums = {got[a][0]["init_checksum_shared"] for a in RUN}
    hashes = {got[a][0]["split_hash"] for a in RUN}
    if len(sums) != 1 or len(hashes) != 1:
        r["reason"] = "init checksum or split differs between arms"
        return r
    M = ms.mask_matrix(s)
    a, c = ms.m0(M), m0c(M)
    for arm in RUN:
        K = got[arm][1]
        r[f"K_{arm}"] = K
        r[f"d_{arm}"] = p12.rbar(c, K) - p12.rbar(a, K)
        r[f"rbar_{arm}_M0"], r[f"rbar_{arm}_M0c"] = p12.rbar(a, K), p12.rbar(c, K)
    r.update({"valid": True, "Delta_rand": r["d_rand"] - r["d_base"], "Delta_copy": r["d_copy"] - r["d_base"],
              "cross_rho_base": cross_rho(s, None), "cross_rho_rand": cross_rho(s, "rand")})
    return r


def one_sided_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def main() -> None:
    rows = [row(s) for s in SEEDS]
    valid = [r for r in rows if r["valid"]]
    out: dict = {"rows": rows, "n_valid": len(valid)}
    if len(valid) < MIN_VALID:
        out["verdict"] = "nicht auswertbar"
    else:
        D = np.array([r["Delta_rand"] for r in valid])
        p = one_sided_p(D)
        Dc = np.array([r["Delta_copy"] for r in valid])
        out.update({"Delta_rand_mean": float(D.mean()), "p_one_sided": p,
                    "Delta_copy_mean": float(Dc.mean()), "p_copy_one_sided": one_sided_p(Dc),
                    "manipulation_cross_rho": {"base": float(np.mean([r["cross_rho_base"] for r in valid])),
                                               "rand": float(np.mean([r["cross_rho_rand"] for r in valid]))},
                    "verdict": "widerspricht" if D.mean() <= 0 else
                    ("bestätigt" if p < ALPHA else "richtungsgleich, nicht signifikant")})
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
