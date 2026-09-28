"""Rule 20c (session 43): Nanda restricted / excluded loss on the STORED P2d (add 113) and P2e-add97 models, with the study's
corrected operator `nanda_exact` (constant + per key k the projection onto span{cos(w_k(a+b)), sin(w_k(a+b))};
training/grokverse/analysis/mask_protocols.py — NOT the old outer-product `legacy_broad_mask`). Absicherung ohne neues Training;
the models were analysed before only with the P2 margin measure, so this is a new measure on known models (not a confirmation).
UNTESTED. Loads torch models: run under the guard in the run window:
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/confirm/P2_nanda_s43.py [--selftest]

Per model (arm F or G of a seed; key sets T = own 5 targets, U = the other arm's 5 targets, both from the split json):
  restr(K) = cross-entropy of the restricted logit grid on the UNSEEN pairs (in neither split of the seed)
  excl(K)  = cross-entropy of the excluded logit grid on the model's OWN train pairs
  r = log restr(U) - log restr(T)     (own targets reproduce the function better than foreign ones: r > 0)
  e = log excl(T) - log excl(U)       (removing own targets hurts more than removing foreign ones: e > 0)
Per seed: mean over the F and G models. Per task: mean over seeds, 95 % bootstrap CI (10 000, rng 20).
Readings fixed HERE, BEFORE computing (per task):
  'Ziele funktional (Nanda)'  r and e CI lower > 0
  'nicht'                     r and e CI upper < 0.1
  else 'gemischt'.
Descriptive: accuracy of the unrestricted models on the unseen pairs, restr/excl in absolute terms, the same with the model's own
top-5 energy frequencies (reference), n generalised (unseen accuracy >= 0.9).
Not covered: mul 113 (needs the grid re-indexed by the discrete logarithm) and D59 (non-abelian; needs an irrep projection).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(ROOT / "training"))

TASKS = {"add113": {"p": 113, "seeds": range(2230, 2250), "raw": LAB / "confirm/p2d_raw", "spl": LAB / "confirm/p2d_splits",
                    "run": "EXP-016_baseline_seed{s}_thr1_p2d_seed{s}_{a}_devcuda", "stem": "p2d_seed{s}_{a}"},
         "add97": {"p": 97, "seeds": range(2270, 2290), "raw": LAB / "confirm/p2e_raw", "spl": LAB / "confirm/p2e_splits",
                   "run": "EXP-043_baseline_seed{s}_thr1_p2e_add97_seed{s}_{a}_add97_devcuda", "stem": "p2e_add97_seed{s}_{a}"}}
N_BOOT, HI = 10_000, 0.1


def ce(L: np.ndarray, mask: np.ndarray, p: int) -> tuple[float, float]:
    a, b = np.nonzero(mask)
    z = L[a, b, :]
    z = z - z.max(axis=1, keepdims=True)
    lse = np.log(np.exp(z).sum(axis=1))
    y = (a + b) % p
    return float(np.mean(lse - z[np.arange(len(y)), y])), float(np.mean(z.argmax(axis=1) == y))


def grid_logits(model_path: Path, p: int) -> np.ndarray:
    import torch
    from grokverse.config import get_config
    from grokverse.models import build_model
    cfg = get_config("arch25k", seed=0, steps=1, threads=1, p=p, task="add")
    model = build_model(cfg)
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()
    a, b = np.meshgrid(np.arange(p), np.arange(p), indexing="ij")
    x = torch.tensor(np.stack([a.ravel(), b.ravel(), np.full(p * p, cfg.equals_token)], axis=1), dtype=torch.long)
    with torch.no_grad():
        return model.logits_last(x)[:, :p].double().numpy().reshape(p, p, p)


def mask_of(idx: np.ndarray, p: int) -> np.ndarray:
    m = np.zeros((p, p), bool)
    m[idx // p, idx % p] = True
    return m


def model_row(L: np.ndarray, p: int, T: list[int], U: list[int], own: np.ndarray, unseen: np.ndarray) -> dict:
    from grokverse.analysis.mask_protocols import NandaExact, _apply
    ns = SimpleNamespace(p=p, task="add")
    out = {"acc_unseen": ce(L, unseen, p)[1], "ce_unseen": ce(L, unseen, p)[0]}
    for name, K in (("T", T), ("U", U)):
        pr = NandaExact(p, K, split="test")
        out[f"restr_{name}"] = ce(_apply(L, pr, "restricted", ns), unseen, p)[0]
        out[f"excl_{name}"] = ce(_apply(L, pr, "excluded", ns), own, p)[0]
    out["r"] = float(np.log(out["restr_U"]) - np.log(out["restr_T"]))
    out["e"] = float(np.log(out["excl_T"]) - np.log(out["excl_U"]))
    return out


def boot_ci(x: np.ndarray, seed: int = 20) -> list[float]:
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), size=(N_BOOT, len(x)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def reading(r: np.ndarray, e: np.ndarray) -> str:
    cr, cc = boot_ci(r), boot_ci(e)
    if cr[0] > 0 and cc[0] > 0:
        return "Ziele funktional (Nanda)"
    if cr[1] < HI and cc[1] < HI:
        return "nicht"
    return "gemischt"


def main() -> None:
    out: dict = {}
    for task, t in TASKS.items():
        p, rows = t["p"], []
        for s in t["seeds"]:
            metas = {a: json.loads((t["spl"] / (t["stem"].format(s=s, a=a) + ".json")).read_text(encoding="utf-8")) for a in "FG"}
            idx = {a: np.load(t["spl"] / (t["stem"].format(s=s, a=a) + ".npy")) for a in "FG"}
            unseen = ~(mask_of(idx["F"], p) | mask_of(idx["G"], p))
            row: dict = {"seed": s}
            for a in "FG":
                L = grid_logits(t["raw"] / t["run"].format(s=s, a=a) / "model_final.pt", p)
                row[a] = model_row(L, p, metas[a]["targets"], metas[a]["other_targets"], mask_of(idx[a], p), unseen)
            row["r"], row["e"] = (row["F"]["r"] + row["G"]["r"]) / 2, (row["F"]["e"] + row["G"]["e"]) / 2
            rows.append(row)
        r, e = np.array([x["r"] for x in rows]), np.array([x["e"] for x in rows])
        out[task] = {"n": len(rows), "r_mean": float(r.mean()), "r_ci95": boot_ci(r), "e_mean": float(e.mean()),
                     "e_ci95": boot_ci(e), "reading": reading(r, e),
                     "n_generalised": int(sum(min(x["F"]["acc_unseen"], x["G"]["acc_unseen"]) >= 0.9 for x in rows)),
                     "rows": rows}
        print(task, {k: v for k, v in out[task].items() if k != "rows"}, flush=True)
    (LAB / "confirm/P2_nanda_s43.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


def selftest() -> None:
    p = 13
    a, b = np.meshgrid(np.arange(p), np.arange(p), indexing="ij")
    c = np.arange(p)
    L = 5 * np.cos(2 * np.pi * 3 * ((a + b)[..., None] - c[None, None, :]) / p)     # pure frequency-3 addition circuit
    own = np.ones((p, p), bool)
    row = model_row(L, p, [3], [5], own, own)
    assert row["restr_T"] < row["restr_U"] and row["excl_T"] > row["excl_U"] and row["r"] > 0 and row["e"] > 0, row
    assert reading(np.full(8, 0.5) + np.linspace(-0.01, 0.01, 8), np.full(8, 0.5)) == "Ziele funktional (Nanda)"
    assert reading(np.zeros(8), np.zeros(8)) == "nicht"
    print("[P2_nanda] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
