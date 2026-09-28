"""Session 46: independent re-check of P2_nanda_s43 (Nanda restricted / excluded loss on the stored P2d/P2e/P2f models).

Written without importing or copying P2_nanda_s43.py: only file locations / data formats were taken from it. The math
(sum-direction projector, discrete-log re-indexing, dihedral group law and irreps, CE, bootstrap) is re-derived here.
Differences in method (same target quantity):
  - projection via the normal equations / pseudo-inverse of the raw (non-orthonormalised) feature matrix, not QR;
  - excluded = L minus the projection onto the key directions only (the constant is orthogonal to them; asserted);
  - D59 group law derived from the faithful 2x2 matrix representation s -> diag(1,-1), r -> R(2 pi / n), element index
    i < n: r^i, i >= n: s r^(i - n) (the EXP-046 data convention), not from dihedral.py;
  - own bootstrap (10 000 resamples, rng 4646), so CIs differ from the original within Monte-Carlo noise.
Adds a one-sided sign test (#seeds with r > 0, e > 0; binomial p under p = 1/2).
Run under the guard:
  PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 python lab/tools/guarded_run.py -- python lab/confirm/P2_nanda_recheck_s46.py
"""
from __future__ import annotations

import json
import sys
from math import comb
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(ROOT / "training"))
C = LAB / "confirm"
OUT = C / "P2_nanda_recheck_s46.json"
ORIG = C / "P2_nanda_s43.json"
N_BOOT, BOOT_SEED, GENERATOR = 10_000, 4646, 3

JOBS = [
    ("add113", 113, "add", range(2230, 2250), "p2d_raw", "p2d_splits",
     "EXP-016_baseline_seed{s}_thr1_p2d_seed{s}_{a}_devcuda", "p2d_seed{s}_{a}"),
    ("mul113", 113, "mul", range(2270, 2290), "p2e_raw", "p2e_splits",
     "EXP-043_baseline_seed{s}_thr1_p2e_mul113_seed{s}_{a}_mul113_devcuda", "p2e_mul113_seed{s}_{a}"),
    ("add97", 97, "add", range(2270, 2290), "p2e_raw", "p2e_splits",
     "EXP-043_baseline_seed{s}_thr1_p2e_add97_seed{s}_{a}_add97_devcuda", "p2e_add97_seed{s}_{a}"),
    ("D59", 118, "D", range(2340, 2360), "p2f_raw", "p2f_splits",
     "EXP-046_seed{s}_p2f_D59_seed{s}_{a}_devcuda", "p2f_D59_seed{s}_{a}"),
]


# ---------------------------------------------------------------- groups: labels and key features on the G x G grid
def cyclic_features(n: int, keys: list[int]) -> np.ndarray:
    """[2*len(keys), n*n] rows cos/sin(2 pi k (x + y) / n), x = row element, y = column element."""
    x = np.arange(n)
    s = np.add.outer(x, x)
    ang = [2.0 * np.pi * k * s / n for k in keys]
    return np.array([f(a).ravel() for a in ang for f in (np.cos, np.sin)])


def dihedral_mats(nd: int, k: int) -> np.ndarray:
    """[2 nd, 2, 2]: element i < nd -> R(k)^i, i >= nd -> S R(k)^(i - nd)."""
    th = 2.0 * np.pi * k / nd
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    S = np.diag([1.0, -1.0])
    rot = [np.linalg.matrix_power(R, m) for m in range(nd)]
    return np.array(rot + [S @ M for M in rot])


def dihedral_table(nd: int) -> np.ndarray:
    """table[a, b] = index of a*b, found by matching products of the faithful k=1 representation."""
    M = dihedral_mats(nd, 1)
    prod = np.einsum("aij,bjk->abik", M, M).reshape(2 * nd, 2 * nd, 4)
    flat = M.reshape(2 * nd, 4)
    d = np.abs(prod[:, :, None, :] - flat[None, None, :, :]).sum(-1)
    T = d.argmin(-1)
    assert np.all(d.min(-1) < 1e-8)
    return T


def dihedral_features(nd: int, keys: list[int], T: np.ndarray) -> np.ndarray:
    rows = []
    for k in keys:
        Mk = dihedral_mats(nd, k)[T]                 # rho_k(x y) on the grid
        rows += [Mk[..., i, j].ravel() for i in range(2) for j in range(2)]
    return np.array(rows)


def dlog_order(p: int, g: int) -> np.ndarray:
    out, x = [], 1
    for _ in range(p - 1):
        out.append(x)
        x = x * g % p
    assert len(set(out)) == p - 1, "not a generator"
    return np.array(out)


# ---------------------------------------------------------------- operator
def split_projection(X: np.ndarray, F: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """X [N, C], F [m, N] key features. Returns (restricted, excluded):
    restricted = const part + key part of X, excluded = X - key part."""
    N = X.shape[0]
    one = np.ones((N, 1))
    assert np.abs(F @ one).max() < 1e-6 * N, "constant not orthogonal to key features"
    const = one @ (one.T @ X) / N
    A = F.T                                          # [N, m]
    key = A @ np.linalg.solve(A.T @ A, A.T @ X)
    return const + key, X - key


def xent(Lflat: np.ndarray, rows: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    z = Lflat[rows]
    m = z.max(1, keepdims=True)
    logZ = np.log(np.exp(z - m).sum(1)) + m[:, 0]
    return float(np.mean(logZ - z[np.arange(len(rows)), y])), float(np.mean(z.argmax(1) == y))


# ---------------------------------------------------------------- model loading
def logit_cube(path: Path, p: int, task: str) -> np.ndarray:
    import torch
    from grokverse.config import get_config
    from grokverse.models import build_model
    cfg = get_config("arch25k", seed=0, steps=1, threads=1, p=p, task="add" if task == "D" else task)
    net = build_model(cfg)
    net.load_state_dict(torch.load(path, map_location="cpu"))
    net.eval()
    a = np.repeat(np.arange(p), p)
    b = np.tile(np.arange(p), p)
    tok = torch.tensor(np.stack([a, b, np.full(p * p, cfg.equals_token)], 1), dtype=torch.long)
    with torch.no_grad():
        out = net.logits_last(tok)[:, :p].double().numpy()
    return out.reshape(p, p, p)


def eval_model(L: np.ndarray, lab: np.ndarray, own: np.ndarray, unseen: np.ndarray, featT: np.ndarray,
               featU: np.ndarray) -> dict:
    G = L.shape[0]
    X = L.reshape(G * G, -1)
    y = lab.ravel()
    iu, io = np.flatnonzero(unseen.ravel()), np.flatnonzero(own.ravel())
    res = {}
    res["ce_unseen"], res["acc_unseen"] = xent(X, iu, y[iu])
    for nm, Fm in (("T", featT), ("U", featU)):
        R, E = split_projection(X, Fm)
        res[f"restr_{nm}"] = xent(R, iu, y[iu])[0]
        res[f"excl_{nm}"] = xent(E, io, y[io])[0]
    res["r"] = float(np.log(res["restr_U"] / res["restr_T"]))
    res["e"] = float(np.log(res["excl_T"] / res["excl_U"]))
    res["n_own"], res["n_unseen"] = int(len(io)), int(len(iu))
    return res


def to_mask(idx: np.ndarray, p: int) -> np.ndarray:
    m = np.zeros(p * p, bool)
    m[idx] = True
    return m.reshape(p, p)


def run_task(name, p, task, seeds, raw, spl, run, stem) -> list[dict]:
    rows = []
    if task == "D":
        nd = p // 2
        T = dihedral_table(nd)
    for s in seeds:
        meta = {a: json.loads((C / spl / f"{stem.format(s=s, a=a)}.json").read_text(encoding="utf-8")) for a in "FG"}
        tr = {a: to_mask(np.load(C / spl / f"{stem.format(s=s, a=a)}.npy"), p) for a in "FG"}
        unseen_raw = ~(tr["F"] | tr["G"])
        row = {"seed": s}
        for a in "FG":
            L = logit_cube(C / raw / run.format(s=s, a=a) / "model_final.pt", p, task)
            own, uns = tr[a], unseen_raw
            if task == "add":
                lab = np.add.outer(np.arange(p), np.arange(p)) % p
                fT, fU = cyclic_features(p, meta[a]["targets"]), cyclic_features(p, meta[a]["other_targets"])
            elif task == "mul":
                o = dlog_order(p, GENERATOR)            # position i <-> element 3^i
                L = L[o][:, o][:, :, o]
                own, uns = own[np.ix_(o, o)], uns[np.ix_(o, o)]
                n = p - 1
                lab = np.add.outer(np.arange(n), np.arange(n)) % n
                assert np.array_equal(o[lab], (np.outer(o, o) % p))
                fT, fU = cyclic_features(n, meta[a]["targets"]), cyclic_features(n, meta[a]["other_targets"])
            else:
                lab = T
                fT = dihedral_features(nd, meta[a]["targets"], T)
                fU = dihedral_features(nd, meta[a]["other_targets"], T)
            row[a] = eval_model(L, lab, own, uns, fT, fU)
        row["r"] = 0.5 * (row["F"]["r"] + row["G"]["r"])
        row["e"] = 0.5 * (row["F"]["e"] + row["G"]["e"])
        rows.append(row)
        print(f"  {name} seed {s}: r={row['r']:+.4f} e={row['e']:+.4f} accF={row['F']['acc_unseen']:.3f} "
              f"accG={row['G']['acc_unseen']:.3f}", flush=True)
    return rows


def bootstrap(x: np.ndarray, rng: np.random.Generator) -> list[float]:
    means = np.array([x[rng.integers(0, len(x), len(x))].mean() for _ in range(N_BOOT)])
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def sign_test(x: np.ndarray) -> dict:
    n, k = len(x), int((x > 0).sum())
    return {"n_pos": k, "n": n, "p_one_sided": sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n}


def selfcheck() -> None:
    T = dihedral_table(5)
    assert all(sorted(T[i]) == list(range(10)) for i in range(10)) and not np.array_equal(T, T.T)
    for k in (1, 2):
        M = dihedral_mats(5, k)
        assert np.allclose(np.einsum("aij,bjk->abik", M, M), M[T])
    rng = np.random.default_rng(0)
    X = rng.normal(size=(13 * 13, 13))
    Rr, E = split_projection(X, cyclic_features(13, [2, 5]))
    const = X.mean(0, keepdims=True)
    assert np.allclose((Rr - const) + E, X)          # key part + excluded = X


def main() -> None:
    import torch
    torch.set_num_threads(2)
    if OUT.exists():
        raise SystemExit(f"{OUT} exists; not overwriting")
    selfcheck()
    rng = np.random.default_rng(BOOT_SEED)
    mine: dict = {"_meta": {"note": "independent recheck of P2_nanda_s43 (session 46)", "n_boot": N_BOOT,
                            "boot_seed": BOOT_SEED}}
    for job in JOBS:
        rows = run_task(*job)
        r, e = np.array([x["r"] for x in rows]), np.array([x["e"] for x in rows])
        gen = [x for x in rows if min(x["F"]["acc_unseen"], x["G"]["acc_unseen"]) >= 0.9]
        mine[job[0]] = {"n": len(rows), "r_mean": float(r.mean()), "r_ci95": bootstrap(r, rng),
                        "e_mean": float(e.mean()), "e_ci95": bootstrap(e, rng),
                        "sign_r": sign_test(r), "sign_e": sign_test(e), "n_generalised": len(gen),
                        "generalised_only": {"n": len(gen), "r_mean": float(np.mean([x["r"] for x in gen])) if gen else None,
                                             "e_mean": float(np.mean([x["e"] for x in gen])) if gen else None},
                        "rows": rows}
    # only now read the original
    orig = json.loads(ORIG.read_text(encoding="utf-8"))
    cmp = {}
    print("\ntask     quantity   recheck                         original                        max|rel diff| per-seed")
    for name, *_ in JOBS:
        o, m = orig.get(name), mine[name]
        if o is None:
            print(name, "missing in original")
            continue
        per_seed = {}
        for q in ("r", "e"):
            a = np.array([x[q] for x in m["rows"]])
            b = np.array([x[q] for x in o["rows"]])
            per_seed[q] = float(np.max(np.abs(a - b) / np.maximum(np.abs(b), 1e-12)))
            print(f"{name:8s} {q}_mean  {m[q + '_mean']:+.6f} CI [{m[q + '_ci95'][0]:+.4f},{m[q + '_ci95'][1]:+.4f}]   "
                  f"{o[q + '_mean']:+.6f} CI [{o[q + '_ci95'][0]:+.4f},{o[q + '_ci95'][1]:+.4f}]   {per_seed[q]:.2e}")
        print(f"{name:8s} sign: r>0 {m['sign_r']['n_pos']}/{m['n']} (p={m['sign_r']['p_one_sided']:.2e}), "
              f"e>0 {m['sign_e']['n_pos']}/{m['n']} (p={m['sign_e']['p_one_sided']:.2e}); n_gen {m['n_generalised']} "
              f"vs {o.get('n_generalised')}")
        cmp[name] = {"orig_r_mean": o["r_mean"], "orig_r_ci95": o["r_ci95"], "orig_e_mean": o["e_mean"],
                     "orig_e_ci95": o["e_ci95"], "orig_reading": o.get("reading"),
                     "max_rel_diff_per_seed": per_seed,
                     "rel_diff_mean": {q: abs(m[q + "_mean"] - o[q + "_mean"]) / max(abs(o[q + "_mean"]), 1e-12)
                                       for q in ("r", "e")}}
    mine["comparison"] = cmp
    OUT.write_text(json.dumps(mine, indent=1), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
