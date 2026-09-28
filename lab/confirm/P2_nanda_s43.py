"""Rule 20c (session 43): Nanda restricted / excluded loss on the STORED P2d (add 113), P2e (mul 113, add 97) and P2f (D59) models
(4 tasks x 20 seeds x arms F/G = 160 models) with the
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
Pre-run review (session 45, before any run; readings above unchanged): the readings use ALL 20 seeds per task, including models
that did not generalise (P2e mul 113 19/20, P2f D59 17/20 generalised). Descriptive only: the same r/e means over the seeds whose
two models both reach acc_unseen >= 0.9 ("generalised-only"). Every model file is checked against its sha256 in the block's
bindings before loading; the output is never overwritten and is saved after each task; it records the git commit.
Nanda's operator projects per output class onto cos/sin(w_k(i + j)), which is broader than the joint cos(w_k(i + j - c)) form;
this reproduces the study operator and is described that way in the paper.
Descriptive: accuracy of the unrestricted models on the unseen pairs, restr/excl in absolute terms (mul: over 112 classes, not comparable
in absolute size to the add tasks), mask sizes n_own / n_unseen, n generalised.
D59 (P2f): the analogue of the sum directions are the matrix coefficients rho_k(g h)_ij of the key 2-dim irreps (Schur
orthogonal), orthonormalized together with the constant; labels are the composition table (EXP-046 dihedral.py).
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
                   "run": "EXP-043_baseline_seed{s}_thr1_p2e_add97_seed{s}_{a}_add97_devcuda", "stem": "p2e_add97_seed{s}_{a}"},
         "D59": {"p": 118, "task": "D", "n": 59, "seeds": range(2340, 2360), "raw": LAB / "confirm/p2f_raw", "spl": LAB / "confirm/p2f_splits",
                 "run": "EXP-046_seed{s}_p2f_D59_seed{s}_{a}_devcuda", "stem": "p2f_D59_seed{s}_{a}"}}
GEN, N_BOOT, HI = 3, 10_000, 0.1
BIND = {"add113": "p2d_bindings", "mul113": "p2e_bindings", "add97": "p2e_bindings", "D59": "p2f_bindings"}   # review s45
OUT = LAB / "confirm/P2_nanda_s43.json"


def bound_hashes(dirname: str) -> dict[str, set[str]]:
    """path (repo-relative, posix) -> set of sha256 recorded in the block's binding files."""
    out: dict[str, set[str]] = {}
    for f in sorted((LAB / "confirm" / dirname).glob("*.json")):
        for path, h in json.loads(f.read_text(encoding="utf-8")).get("files", {}).items():
            out.setdefault(path, set()).add(h)
    return out


def check_bound(path: Path, bound: dict[str, set[str]]) -> None:
    import hashlib
    rel = path.relative_to(ROOT).as_posix()
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    if h not in bound.get(rel, set()):
        raise SystemExit(f"[P2_nanda] {rel}: sha256 not in the block's bindings, refusing to load")


def sum_basis(n: int, K: list[int]) -> np.ndarray:
    """Orthonormal functions of (i + j) mod n on the n x n grid: constant plus cos/sin of each key k (k < n/2). Shape [m, n*n]."""
    s = (np.arange(n)[:, None] + np.arange(n)[None, :]) % n
    rows = [np.ones(n * n)]
    for k in K:
        rows += [np.cos(2 * np.pi * k * s / n).ravel(), np.sin(2 * np.pi * k * s / n).ravel()]
    B = np.array(rows)
    return B / np.linalg.norm(B, axis=1, keepdims=True)


def dihedral_basis(nd: int, K: list[int]) -> np.ndarray:
    """D_nd (order 2 nd): constant plus the 4 matrix coefficients rho_k(g h)_ij per key irrep k, orthonormalized. [m, G*G]."""
    sys.path.insert(0, str(LAB / "experiments/EXP-046-dihedral-steering"))
    from dihedral import compose_table, rho
    T = compose_table(nd)
    rows = [np.ones(T.size)]
    for k in K:
        R = rho(nd, k)[T]                               # [G, G, 2, 2]
        rows += [R[..., i, j].ravel() for i in range(2) for j in range(2)]
    Q, _ = np.linalg.qr(np.array(rows).T)
    B = Q.T
    return B * np.sign(B[0].sum())                      # constant row first, positive


def project(L: np.ndarray, n: int, K: list[int], which: str, basis=None) -> np.ndarray:
    """L [n, n, C]: 'restricted' = projection onto const + key directions of K; 'excluded' = L minus the key-direction part.
    basis: [m, n*n] orthonormal with the constant first (default: sum directions of Z_n)."""
    B = sum_basis(n, K) if basis is None else basis
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
    cfg = get_config("arch25k", seed=0, steps=1, threads=1, p=p, task="add" if task == "D" else task)   # D59: as group_train.py
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
    if task == "D":                                   # EXP-046 element order already is the group; labels = composition table
        sys.path.insert(0, str(LAB / "experiments/EXP-046-dihedral-steering"))
        from dihedral import compose_table
        return L, compose_table(p // 2), masks, p
    g = dlog_perm(p, gen)
    n = p - 1
    Lg = L[np.ix_(g, g, g)]                         # rows a = g^i, b = g^j, output class g^m at position m
    return Lg, (np.arange(n)[:, None] + np.arange(n)[None, :]) % n, [m[np.ix_(g, g)] for m in masks], n


def mask_of(idx: np.ndarray, p: int) -> np.ndarray:
    m = np.zeros((p, p), bool)
    m[idx // p, idx % p] = True
    return m


def model_row(L: np.ndarray, labels: np.ndarray, n: int, T: list[int], U: list[int], own: np.ndarray, unseen: np.ndarray,
              nd: int | None = None) -> dict:
    c_un, a_un = ce(L, unseen, labels)
    out = {"ce_unseen": c_un, "acc_unseen": a_un}
    for name, K in (("T", T), ("U", U)):
        B = dihedral_basis(nd, K) if nd else None
        out[f"restr_{name}"] = ce(project(L, n, K, "restricted", B), unseen, labels)[0]
        out[f"excl_{name}"] = ce(project(L, n, K, "excluded", B), own, labels)[0]
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
    import subprocess
    if OUT.exists():
        raise SystemExit(f"[P2_nanda] {OUT} exists: never overwrite (move it aside by hand if a rerun is intended)")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    out: dict = {"_meta": {"git_commit": commit, "note": "rule 20c, new measure on known models (not a confirmation)"}}
    tmp = OUT.with_suffix(".partial.json")
    for name, t in TASKS.items():
        p, task, rows = t["p"], t["task"], []
        bound = bound_hashes(BIND[name])
        for s in t["seeds"]:
            metas = {a: json.loads((t["spl"] / (t["stem"].format(s=s, a=a) + ".json")).read_text(encoding="utf-8")) for a in "FG"}
            idx = {a: np.load(t["spl"] / (t["stem"].format(s=s, a=a) + ".npy")) for a in "FG"}
            unseen_raw = ~(mask_of(idx["F"], p) | mask_of(idx["G"], p))
            row: dict = {"seed": s}
            for a in "FG":
                mp = t["raw"] / t["run"].format(s=s, a=a) / "model_final.pt"
                check_bound(mp, bound)
                L_raw = grid(mp, p, task)
                L, labels, (own, unseen), n = to_group(L_raw, [mask_of(idx[a], p), unseen_raw], p, task)
                row[a] = model_row(L, labels, n, metas[a]["targets"], metas[a]["other_targets"], own, unseen, t.get("n"))
                row[a]["n_own"], row[a]["n_unseen"] = int(own.sum()), int(unseen.sum())
            row["r"], row["e"] = (row["F"]["r"] + row["G"]["r"]) / 2, (row["F"]["e"] + row["G"]["e"]) / 2
            rows.append(row)
        r, e = np.array([x["r"] for x in rows]), np.array([x["e"] for x in rows])
        out[name] = {"n": len(rows), "r_mean": float(r.mean()), "r_ci95": boot_ci(r), "e_mean": float(e.mean()),
                     "e_ci95": boot_ci(e), "reading": reading(r, e),
                     "n_generalised": int(sum(min(x["F"]["acc_unseen"], x["G"]["acc_unseen"]) >= 0.9 for x in rows)),
                     "rows": rows}
        gen = [x for x in rows if min(x["F"]["acc_unseen"], x["G"]["acc_unseen"]) >= 0.9]   # descriptive, review s45
        out[name]["generalised_only"] = {"n": len(gen), "r_mean": float(np.mean([x["r"] for x in gen])) if gen else None,
                                         "e_mean": float(np.mean([x["e"] for x in gen])) if gen else None}
        print(name, {k: v for k, v in out[name].items() if k != "rows"}, flush=True)
        tmp.write_text(json.dumps(out, indent=1), encoding="utf-8")                        # keep partial results on a crash
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    tmp.unlink()


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
    sys.path.insert(0, str(LAB / "experiments/EXP-046-dihedral-steering"))
    from dihedral import compose_table, rho
    nd, G = 5, 10                                    # D5: basis orthonormal; a pure irrep-1 circuit is reproduced by T=[1], not by U=[2]
    Bd = dihedral_basis(nd, [1, 2])
    assert np.allclose(Bd @ Bd.T, np.eye(len(Bd)), atol=1e-9) and len(Bd) == 9
    Td = compose_table(nd)
    r1 = rho(nd, 1)
    Ld = 5 * np.einsum("ghij,cij->ghc", r1[Td], r1)   # score(c) = tr(rho(gh) rho(c)^T) is maximal at c = gh
    fullg = np.ones((G, G), bool)
    Lg2, labg, _, ng = to_group(Ld, [fullg], G, "D")
    rowd = model_row(Lg2, labg, ng, [1], [2], fullg, fullg, nd)
    assert rowd["restr_T"] < rowd["restr_U"] and rowd["excl_T"] > rowd["excl_U"], rowd
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
