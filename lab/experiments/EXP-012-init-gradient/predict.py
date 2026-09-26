"""EXP-012: which init-computable frequency measure predicts the final frequency set?

Predictors per frequency k = 1..56, all at step 0 (definition: README.md):
  E0  power of W_E[:p]                        (EXP-009 reference)
  U0  power of W_U[:, :p]^T (unembedding over output tokens)
  G0  power of the full-batch gradient dL/dW_E[:p] at step 0
  A1  power of sign(G0)  (~ first Adam step without weight decay)
Measure: rbar = mean normalized rank of K in the predictor's ordering (0 = strongest).

Phase 1 (exploration): seeds 0-9, stored runs. Init is rebuilt (set_seed, make_dataset,
build_model, same order as training) and must equal the stored ckpt_step000000.pt; K = EXP-009 k_final.
Phase 2 (confirmation): seeds 10-19, EXP-003d baselines. Rebuilt init must match the run's
step-0 spectrum; K = final_top_m_freqs.

Run only through lab/tools/guarded_run.py (one forward/backward per seed, seconds).
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(ROOT / "training"))
sys.path.insert(0, str(LAB / "experiments/EXP-001-freq-ban"))

import freq_ban as fb  # noqa: E402
from grokverse.config import get_config  # noqa: E402
from grokverse.data import make_dataset  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.seed import set_seed  # noqa: E402

PREDICTORS = ("E0", "U0", "G0", "A1")
CANDIDATES = ("U0", "G0", "A1")          # phase 1 picks the best of these
STORED = ROOT / "training/runs/txf_add_p113_wd1.0_frac0.3_seed{s}_arch25k"
BASE_D = LAB / "experiments/EXP-003-early-prediction/raw_d/EXP-001_baseline_t2000_m5_seed{s}_thr4"
EXP009 = LAB / "experiments/EXP-009-freq-commitment/summary.json"
M, N_FREQ, ALPHA, MIN_VALID = 5, 56, 0.05, 8
N_MC, MC_SEED = 100_000, 0


def init_predictors(seed: int) -> tuple[dict[str, np.ndarray], torch.nn.Module]:
    cfg = get_config("arch25k", seed=seed, threads=4)
    torch.set_num_threads(cfg.threads)
    set_seed(cfg.seed)
    data = make_dataset(cfg)
    model = build_model(cfg)
    p = cfg.p
    basis = fb.fourier_basis(p)
    loss = F.cross_entropy(model.logits_last(data["train_x"])[:, :p], data["train_y"])
    loss.backward()
    W_E = model.W_E.detach().numpy().astype(np.float64)[:p]
    G = model.W_E.grad.numpy().astype(np.float64)[:p]
    W_U = model.W_U.detach().numpy().astype(np.float64)[:, :p].T
    preds = {"E0": fb.freq_power(W_E, basis), "U0": fb.freq_power(W_U, basis),
             "G0": fb.freq_power(G, basis), "A1": fb.freq_power(np.sign(G), basis)}
    return preds, model


def rbar(power: np.ndarray, K: list[int]) -> float:
    rank = np.argsort(np.argsort(-power, kind="stable"), kind="stable")
    return float((rank[[k - 1 for k in K]] / (N_FREQ - 1)).mean())


def seed_row(seed: int, phase: int, k009: dict[int, list[int]]) -> dict:
    row: dict = {"seed": seed, "valid": False}
    preds, model = init_predictors(seed)
    if phase == 1:
        ck = torch.load(Path(str(STORED).format(s=seed)) / "ckpt_step000000.pt",
                        map_location="cpu", weights_only=True)
        same = all(torch.equal(ck[n], getattr(model, n).detach()) for n in ck)
        if not same:
            row["reason"] = "rebuilt init != stored ckpt_step000000"
            return row
        K = k009[seed]
    else:
        d = Path(str(BASE_D).format(s=seed))
        if not (d / "result.json").exists():
            row["reason"] = "baseline missing"
            return row
        res = json.loads((d / "result.json").read_text(encoding="utf-8"))
        if res["status"] != "completed":
            row["reason"] = f"baseline status {res['status']}"
            return row
        spec, steps = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()
        if not np.allclose(spec[steps.index(0)], preds["E0"], rtol=1e-5):
            row["reason"] = "rebuilt init spectrum != baseline step-0 spectrum"
            return row
        K = res["final_top_m_freqs"]
        if 250 in steps:                          # reference only, not a predictor
            row["rbar_E250"] = rbar(spec[steps.index(250)], K)
    row.update({"valid": True, "K": K, **{f"rbar_{n}": rbar(preds[n], K) for n in PREDICTORS}})
    return row


def mc_null_p(value: float, n_seeds: int) -> float:
    rng = np.random.default_rng(MC_SEED)
    picks = rng.random((N_MC, n_seeds, N_FREQ)).argsort(axis=2)[:, :, :M]
    null = (picks / (N_FREQ - 1)).mean(axis=(1, 2))
    return float((np.sum(null <= value) + 1) / (N_MC + 1))


def sign_flip_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", type=int, choices=(1, 2), required=True)
    ap.add_argument("--predictor", choices=CANDIDATES, help="phase 2: the predictor chosen in phase 1")
    a = ap.parse_args()
    k009 = {}
    for r in json.loads(EXP009.read_text(encoding="utf-8"))["runs"]:
        if r["run"].startswith("txf_add_p113_wd1.0_frac0.3_seed"):
            k009[int(r["run"].split("seed")[1].split("_")[0])] = r["k_final"]
    seeds = range(0, 10) if a.phase == 1 else range(10, 20)
    rows = [seed_row(s, a.phase, k009) for s in seeds]
    valid = [r for r in rows if r["valid"]]
    out: dict = {"phase": a.phase, "rows": rows, "n_valid": len(valid)}
    if len(valid) >= MIN_VALID:
        means = {n: float(np.mean([r[f"rbar_{n}"] for r in valid])) for n in PREDICTORS}
        out["rbar_mean"] = means
        out["p_vs_null"] = {n: mc_null_p(means[n], len(valid)) for n in PREDICTORS}
        if a.phase == 1:
            out["chosen"] = min(CANDIDATES, key=lambda n: means[n])
        else:
            if a.predictor is None:
                raise SystemExit("phase 2 needs --predictor (the phase-1 choice)")
            X = a.predictor
            diff = np.array([r["rbar_E0"] - r[f"rbar_{X}"] for r in valid])
            p = sign_flip_p(diff)
            out.update({"predictor": X, "diff_mean": float(diff.mean()), "p_vs_E0": p,
                        "verdict": "widerspricht" if means[X] >= means["E0"] else
                        ("bestätigt" if p < ALPHA and out["p_vs_null"][X] < ALPHA
                         else "richtungsgleich, nicht signifikant")})
            if all("rbar_E250" in r for r in valid):
                out["rbar_E250_mean"] = float(np.mean([r["rbar_E250"] for r in valid]))
    else:
        out["verdict"] = "nicht auswertbar"
    (HERE / f"summary_phase{a.phase}.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})


if __name__ == "__main__":
    main()
