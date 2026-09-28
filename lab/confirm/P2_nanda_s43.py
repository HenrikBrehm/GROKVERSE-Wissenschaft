"""Rule 20c (session 43): Nanda restricted / excluded loss on the STORED P2d (add 113) and P2e (mul 113, add 97) models with the
published sum-direction operator (Nanda et al. 2023; the study's `nanda_exact`, training/grokverse/analysis/mask_protocols.py —
NOT the old outer-product `legacy_broad_mask`). Absicherung ohne neues Training; the models were analysed before only with the P2
margin measure, so this is a new measure on known models (not a confirmation). UNTESTED. Loads torch models: run under the guard:
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/confirm/P2_nanda_s43.py [--selftest]

Operator (own implementation, so that the even group Z_112 of mul 113 is covered; for odd n it must equal the study's
`nanda_exact` operator exactly — checked in --selftest): for every output class c the logit surface L[., ., c] on the group
Z_n x Z_n is projected onto the constant plus, per key frequency k, span{cos(2 pi k (i + j)/n), sin(2 pi k (i + j)/n)}
(restricted); excluded = L minus the projection onto the sum directions of all keys (constant kept).
mul 113: rows and outputs re-indexed by the discrete logarithm (generator 3, as in P2e), pairs with a zero operand dropped;
the labels become (i + j) mod 112. Frequencies are those of the split json (P2e defines them over Z_112).
The logit of output class 0 (never correct for a product of non-zero elements) is dropped with the re-indexing.

Per model (arm F or G; key sets T = own 5 targets, U = the other arm's 5 targets):
  restr(K) = cross-entropy of the restricted logit grid on the UNSEEN pairs (in neither split of the seed)
  excl(K)  = cross-entropy of the excluded logit grid on the model's OWN train pairs
  r = log restr(U) - log restr(T),  e = log excl(T) - log excl(U)
Per seed: mean over the F and G models. Per task: mean over seeds, 95 % bootstrap CI (10 000, rng 20).
Readings fixed HERE, BEFORE computing (per task):
  'Ziele funktional (Nanda)'  r and e CI lower > 0
  'nicht'                     r and e CI upper < 0.1
  else 'gemischt'.
Descriptive: accuracy of the unrestricted models on the unseen pairs, restr/excl in absolute terms (mul: over 112 classes, not comparable
in absolute size to the add tasks), mask sizes n_own / n_unseen, n generalised.
Not covered: D59 (non-abelian; needs an irrep projection).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(ROOT / "training"))

TASKS = {"add113": {"p": 113, "task": "add", "seeds": range(2230, 2250), "raw": LAB / "confirm/p2d_raw", "spl": LAB / "confirm/p2d_splits",
                    "run": "EXP-016_baseline_seed{s}_thr1_p2d_seed{s}_{a}_devcuda", "stem": "p2d_seed{s}_{a}"},
         "mul113": {"p": 113, "task": "mul", "seeds": range(2270, 2290), "raw": LAB / "confirm/p2e_raw", "spl": LAB / "confirm/p2e_splits",
                    "run": "EXP-043_baseline_seed{s}_thr1_p2e_mul113_seed{s}_{a}_mul113_devcuda", "stem": "p2e_mul113_seed{s}_{a}"},
         "add97": {"p": 97, "task": "add", "seeds": range(2270, 2290), "raw": LAB / "confirm/p2e_raw", "spl": LAB / "confirm/p2e_splits",
                   "run": "EXP-043_baseline_seed{s}_thr1_p2e_add97_seed{s}_{a}_add97_devcuda", "stem": "p2e_add97_seed{s}_{a}"}}
GEN, N_BOOT, HI = 3, 10_000, 0.1


def sum_basis(n: int, K: list[int]) -> np.ndarray:
    """Orthonormal functions of (i + j) mod n on the n x n grid: constant plus cos/sin of each key k (k < n/2). Shape [m, n*n]."""
    s = (np.arange(n)[:, None] + np.arange(n)[None, :]) % n
    rows = [np.ones(n * n)]
    for k in K:
        rows += [np.cos(2 * np.pi * k * s / n).ravel(), np.sin(2 * np.pi * k * s / n).ravel()]
    B = np.array(rows)
    return B / np.linalg.norm(B, axis=1, keepdims=True)


def project(L: np.ndarray, n: int, K: list[int], which: str) -> np.ndarray:
    """L [n, n, C]: 'restricted' = projection onto const + sum directions of K; 'excluded' = L minus the sum-direction part."""
    B = sum_basis(n, K)
    X = L.reshape(n * n, -1)
    coef = B @ X
    P = B.T @ coef
    if which == "restricted":
        return P.reshape(L.shape)
    P_const = np.outer(B[0], coef[0])
    return (X - (P - P_const)).reshape(L.shape)


def ce(L: np.ndarray, mask: np.ndarray, labels: np.ndarray) -> tuple[float, float]:
    a, b = np.nonzero(mask)
    z = L[a, b, :]
    z = z - z.max(axis=1, keepdims=True)
    lse = np.log(np.exp(z).sum(axis=1))
    y = labels[a, b]
    return float(np.mean(lse - z[np.arange(len(y)), y])), float(np.mean(z.argmax(axis=1) == y))


def dlog_perm(p: int, gen: int) -> np.ndarray:
    """perm[i] = gen**i mod p for i = 0..p-2 (the element at log position i)."""
    return np.array([pow(gen, i, p) for i in range(p - 1)])


def grid(model_path: Path, p: int, task: str) -> np.ndarray:
    import torch
    from grokverse.config import get_config
    from grokverse.models import build_model
    cfg = get_config("arch25k", seed=0, steps=1, threads=1, p=p, task=task)
    model = build_model(cfg)
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()
    a, b = np.meshgrid(np.arange(p), np.arange(p), indexing="ij")
    x = torch.tensor(np.stack([a.ravel(), b.ravel(), np.full(p * p, cfg.equals_token)], axis=1), dtype=torch.long)
    with torch.no_grad():
        return model.logits_last(x)[:, :p].double().numpy().reshape(p, p, p)


def to_group(L: np.ndarray, masks: list[np.ndarray], p: int, task: str, gen: int = GEN):
    """Return (grid over Z_n x Z_n x Z_n, labels [n, n], masks in group coordinates, n)."""
    if task == "add":
        return L, (np.arange(p)[:, None] + np.arange(p)[None, :]) % p, masks, p
    g = dlog_perm(p, gen)
    n = p - 1
    Lg = L[np.ix_(g, g, g)]                         # rows a = g^i, b = g^j, output class g^m at position m
    return Lg, (np.arange(n)[:, None] + np.arange(n)[None, :]) % n, [m[np.ix_(g, g)] for m in masks], n


def mask_of(idx: np.ndarray, p: int) -> np.ndarray:
    m = np.zeros((p, p), bool)
    m[idx // p, idx % p] = True
    return m


def model_row(L: np.ndarray, labels: np.ndarray, n: int, T: list[int], U: list[int], own: np.ndarray, unseen: np.ndarray) -> dict:
    c_un, a_un = ce(L, unseen, labels)
    out = {"ce_unseen": c_un, "acc_unseen": a_un}
    for name, K in (("T", T), ("U", U)):
        out[f"restr_{name}"] = ce(project(L, n, K, "restricted"), unseen, labels)[0]
        out[f"excl_{name}"] = ce(project(L, n, K, "excluded"), own, labels)[0]
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
    for name, t in TASKS.items():
        p, task, rows = t["p"], t["task"], []
        for s in t["seeds"]:
            metas = {a: json.loads((t["spl"] / (t["stem"].format(s=s, a=a) + ".json")).read_text(encoding="utf-8")) for a in "FG"}
            idx = {a: np.load(t["spl"] / (t["stem"].format(s=s, a=a) + ".npy")) for a in "FG"}
            unseen_raw = ~(mask_of(idx["F"], p) | mask_of(idx["G"], p))
            row: dict = {"seed": s}
            for a in "FG":
                L_raw = grid(t["raw"] / t["run"].format(s=s, a=a) / "model_final.pt", p, task)
                L, labels, (own, unseen), n = to_group(L_raw, [mask_of(idx[a], p), unseen_raw], p, task)
                row[a] = model_row(L, labels, n, metas[a]["targets"], metas[a]["other_targets"], own, unseen)
                row[a]["n_own"], row[a]["n_unseen"] = int(own.sum()), int(unseen.sum())
            row["r"], row["e"] = (row["F"]["r"] + row["G"]["r"]) / 2, (row["F"]["e"] + row["G"]["e"]) / 2
            rows.append(row)
        r, e = np.array([x["r"] for x in rows]), np.array([x["e"] for x in rows])
        out[name] = {"n": len(rows), "r_mean": float(r.mean()), "r_ci95": boot_ci(r), "e_mean": float(e.mean()),
                     "e_ci95": boot_ci(e), "reading": reading(r, e),
                     "n_generalised": int(sum(min(x["F"]["acc_unseen"], x["G"]["acc_unseen"]) >= 0.9 for x in rows)),
                     "rows": rows}
        print(name, {k: v for k, v in out[name].items() if k != "rows"}, flush=True)
    (LAB / "confirm/P2_nanda_s43.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


def selftest() -> None:
    from types import SimpleNamespace
    from grokverse.analysis.mask_protocols import NandaExact, _apply
    rng = np.random.default_rng(0)
    p = 13
    L = rng.normal(size=(p, p, p))
    for K in ([3], [2, 5]):                         # own operator == the study's nanda_exact for odd n
        for which in ("restricted", "excluded"):
            ref = _apply(L, NandaExact(p, K, split="test"), which, SimpleNamespace(p=p, task="add"))
            assert np.allclose(project(L, p, K, which), ref, atol=1e-9), (K, which)
    a, b = np.meshgrid(np.arange(p), np.arange(p), indexing="ij")
    c = np.arange(p)
    Lc = 5 * np.cos(2 * np.pi * 3 * ((a + b)[..., None] - c[None, None, :]) / p)    # pure frequency-3 addition circuit
    full = np.ones((p, p), bool)
    row = model_row(Lc, (a + b) % p, p, [3], [5], full, full)
    assert row["restr_T"] < row["restr_U"] and row["excl_T"] > row["excl_U"] and row["r"] > 0 and row["e"] > 0, row
    q, gq = 13, 2                                     # multiplication: log re-indexing turns a*b into i+j (2 generates Z_13^*)
    g = dlog_perm(q, gq)
    assert sorted(g.tolist()) == list(range(1, q))
    Lm = np.zeros((q, q, q))
    for i in range(q - 1):
        for j in range(q - 1):
            Lm[g[i], g[j], (g[i] * g[j]) % q] = 1.0
    Lg, lab, _, n = to_group(Lm, [np.ones((q, q), bool)], q, "mul", gen=gq)
    assert n == q - 1 and all(Lg[i, j, lab[i, j]] == 1.0 for i in range(n) for j in range(n))
    assert len(set(dlog_perm(113, GEN).tolist())) == 112          # 3 generates Z_113^*
    assert reading(np.full(8, 0.5) + np.linspace(-0.01, 0.01, 8), np.full(8, 0.5)) == "Ziele funktional (Nanda)"
    assert reading(np.zeros(8), np.zeros(8)) == "nicht"
    import tempfile                                  # the real loading path: a random arch25k model through grid() (review s43)
    import torch
    from grokverse.config import get_config
    from grokverse.models import build_model
    for task in ("add", "mul"):
        with tempfile.TemporaryDirectory() as tmp:
            mp = Path(tmp) / "model_final.pt"
            torch.save(build_model(get_config("arch25k", seed=1, steps=1, threads=1, p=13, task=task)).state_dict(), mp)
            G = grid(mp, 13, task)
            assert G.shape == (13, 13, 13) and np.isfinite(G).all()
            Lg, lab, (m,), n = to_group(G, [np.ones((13, 13), bool)], 13, task, gen=2)
            assert Lg.shape == (n, n, n) and m.sum() == n * n
            model_row(Lg, lab, n, [1], [2], m, m)
    print("[P2_nanda] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
