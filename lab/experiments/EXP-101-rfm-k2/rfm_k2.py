"""EXP-101 (rule 20c): does the training split steer the features of a Recursive Feature Machine (RFM) like it steers W_E (K2)?

Own implementation of the Gaussian-kernel RFM of Mallinar et al. 2024 (arXiv 2407.20199; code lab/external/rfm-grokking,
GPL-3.0, NOT imported by the training path and not committed). Same algorithm as their train_kernel.py with
--kernel_type gaussian --ridge 0 --agop_power 0.5, centering=True:
    K = exp(-(x-z)^T M (x-z) / (2 L^2));  alpha = K^{-1} Y;  grad_j = M D_j / L^2 with
    D_j[c] = sum_i K_ij alpha_ic x_i - (sum_i K_ij alpha_ic) x_j;  G centred over j;  M <- sqrt(mean_j sum_c g g^T).
Differences, all numerical only: (1) D is computed from the one-hot structure (sum over rows with a_i = v) instead of
the dense n x c x d product (O(n m c) instead of O(n m c d)); (2) the PSD square root uses eigh with negative
eigenvalues clipped to 0 instead of scipy.linalg.sqrtm (global Python has no scipy; for a symmetric PSD matrix both give
the principal root). --selftest checks (1) against a dense re-implementation and, if the external repo is present,
against its get_grads with a sqrtm shim; and (2) S @ S == A.

Deterministic: no init randomness (M_0 = I, exact solve). The only source of variation is the split.

Measure (fixed before any run): M is 2p x 2p (one-hot of a, then of b). For each diagonal block B in {M_aa, M_bb}
the energy of frequency k is P_B(k) = f_k^H B f_k + f_{p-k}^H B f_{p-k} = 2 Re(f_k^H B f_k), f_k = exp(2 pi i k v / p)/sqrt(p),
k = 1..(p-1)/2. P(k) = P_aa(k) + P_bb(k) (analogue of the W_E group power: M plays the role of W^T W, NFA).
Delta_pow_RFM = log[P_F(T_F)/P_F(T_G)] + log[P_G(T_G)/P_G(T_F)] exactly as P1 (confirm_p1.delta_pow), at the final
iteration. Secondary: the same with the diagonal of each block removed ("offdiag"), and at iteration 5.

Readings (pilot, exploration; splits = P1 add113 seeds 1000-1009, arms F/G, targets from the split json):
  gate      the random arm R (same size, 30 %) of the same seeds must reach test acc >= 0.95 at the final iteration in
            >= 8/10 seeds; otherwise "RFM does not grok at p = 113 / 30 % with these settings" -> no K2 reading, report.
  positive  mean Delta_pow > 0 with bootstrap 95 % CI > 0 and >= 8/10 seeds positive -> "K2 also in RFM (pilot)".
  negative  CI inside [-0.5, 0.5] -> "no steering in RFM (pilot)".
  unclear   otherwise.
A pilot on 10 split pairs carries no confirmatory weight (rule 15b); a confirmation would use unseen P1 splits 1010-1049.

Usage (every run through the guard):
  python lab/tools/guarded_run.py -- python lab/experiments/EXP-101-rfm-k2/rfm_k2.py --selftest
  python lab/tools/guarded_run.py -- python lab/experiments/EXP-101-rfm-k2/rfm_k2.py --reproduce      # their default: p 61, 50 %
  python lab/tools/guarded_run.py -- python lab/experiments/EXP-101-rfm-k2/rfm_k2.py --run --seeds 1000-1009 --arms R,F,G
  python lab/tools/guarded_run.py -- python lab/experiments/EXP-101-rfm-k2/rfm_k2.py --analyze --seeds 1000-1009
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
ROOT = LAB.parent
SPLITS = LAB / "confirm" / "splits"
RAW = HERE / "raw"
EXTERNAL = LAB / "external" / "rfm-grokking"
P = 113
BANDWIDTH = 2.5          # their default
ITERS = 30               # their paper's p = 61 runs generalise within ~20 iterations; fixed before any run
GATE_ACC = 0.95
EARLY_ITER = 5
BOOT = 10000
DTYPE = torch.float64


# ---------------------------------------------------------------- RFM core

def gauss_kernel(X: torch.Tensor, Z: torch.Tensor, M: torch.Tensor, L: float) -> torch.Tensor:
    """K[i, j] = exp(-(x_i - z_j)^T M (x_i - z_j) / (2 L^2)); same algebra as their euclidean_distances_M + clamp."""
    xn = ((X @ M) * X).sum(1, keepdim=True)
    zn = ((Z @ M) * Z).sum(1, keepdim=True).T
    d2 = (xn + zn - 2.0 * X @ M @ Z.T).clamp_(min=0)
    return torch.exp(-d2 / (2 * L ** 2))


def psd_sqrt(A: torch.Tensor) -> torch.Tensor:
    A = 0.5 * (A + A.T)
    w, V = torch.linalg.eigh(A)
    return (V * w.clamp(min=0).sqrt()) @ V.T


def agop_D(K: torch.Tensor, alpha: torch.Tensor, ab: torch.Tensor, p: int) -> torch.Tensor:
    """D[j, c, :] = sum_i K_ij alpha_ic x_i - B_jc x_j for one-hot x = [e_a, e_b] (d = 2p); K is n x m (train x centres)."""
    n, m = K.shape
    c = alpha.shape[1]
    B = K.T @ alpha                                             # m x c
    C = torch.zeros(m, c, 2 * p, dtype=K.dtype)
    for slot in (0, 1):
        for v in range(p):
            rows = torch.nonzero(ab[:, slot] == v).flatten()
            if len(rows):
                C[:, :, slot * p + v] = K[rows].T @ alpha[rows]
    return C, B


def agop_update(Xtr: torch.Tensor, ab: torch.Tensor, alpha: torch.Tensor, K: torch.Tensor, M: torch.Tensor, L: float,
                p: int) -> torch.Tensor:
    """New M = sqrt(mean_j sum_c g_jc g_jc^T) with g_j = D_j M / L^2 centred over j (their centering=True)."""
    C, B = agop_D(K, alpha, ab, p)
    D = C - B[:, :, None] * Xtr[:, None, :]                   # m x c x d (centres = train points)
    del C                                                      # review s44: ~0.75 GB each at n = 3831
    D -= D.mean(0, keepdim=True)
    Dm = D.reshape(-1, D.shape[2])
    S = (Dm.T @ Dm) / D.shape[0]
    agop = M @ S @ M / L ** 4
    return psd_sqrt(agop)


def spectrum(M: torch.Tensor, p: int, offdiag: bool = False) -> np.ndarray:
    """P(k) = sum over the a- and b-block of 2 Re(f_k^H B f_k), k = 1..(p-1)/2."""
    Mn = M.numpy()
    v = np.arange(p)
    Kn = (p - 1) // 2
    Fk = np.exp(2j * np.pi * np.outer(np.arange(1, Kn + 1), v) / p) / np.sqrt(p)   # Kn x p
    out = np.zeros(Kn)
    for s in (0, 1):
        Bk = Mn[s * p:(s + 1) * p, s * p:(s + 1) * p].copy()
        if offdiag:
            np.fill_diagonal(Bk, 0.0)
        out += 2.0 * np.real(np.einsum("kv,vw,kw->k", Fk.conj(), Bk, Fk))
    return out


def onehot(ab: torch.Tensor, p: int) -> torch.Tensor:
    X = torch.zeros(len(ab), 2 * p, dtype=DTYPE)
    X[torch.arange(len(ab)), ab[:, 0]] = 1.0
    X[torch.arange(len(ab)), p + ab[:, 1]] = 1.0
    return X


def data(train_idx: np.ndarray, p: int, op: str = "add"):
    allidx = np.arange(p * p)
    te_idx = np.setdiff1d(allidx, train_idx)
    def mk(idx):
        ab = torch.from_numpy(np.stack([idx // p, idx % p], 1).astype(np.int64))
        y = (ab[:, 0] + ab[:, 1]) % p if op == "add" else (ab[:, 0] * ab[:, 1]) % p
        return ab, onehot(ab, p), torch.nn.functional.one_hot(y, p).to(DTYPE), y
    return mk(np.sort(train_idx)), mk(te_idx)


def rfm(train_idx: np.ndarray, p: int, iters: int, L: float = BANDWIDTH, log=print) -> dict:
    (ab, Xtr, Ytr, ytr), (_, Xte, _, yte) = data(train_idx, p)
    M = torch.eye(2 * p, dtype=DTYPE)
    hist = {"train_acc": [], "test_acc": [], "spec": [], "spec_offdiag": [], "trace": []}
    for it in range(iters + 1):             # iteration t: solve with M_t, evaluate, record spectrum of M_t, update
        K = gauss_kernel(Xtr, Xtr, M, L)
        try:
            alpha = torch.linalg.solve(K, Ytr)          # ridge 0 as theirs
        except torch.linalg.LinAlgError as e:
            hist["error"] = f"solve failed at iteration {it}: {e}"
            break
        tr = float(((K @ alpha).argmax(1) == ytr).double().mean())
        te = float(((gauss_kernel(Xte, Xtr, M, L) @ alpha).argmax(1) == yte).double().mean())
        for key, val in (("train_acc", tr), ("test_acc", te), ("spec", spectrum(M, p).tolist()),
                         ("spec_offdiag", spectrum(M, p, True).tolist()), ("trace", float(torch.trace(M)))):
            hist[key].append(val)
        if not all(np.isfinite(hist["spec"][-1])) or not np.isfinite(tr):
            hist["error"] = f"non-finite at iteration {it}"
            break
        log(f"  iter {it:2d}  train {tr:.4f}  test {te:.4f}  trace {hist['trace'][-1]:.3f}")
        if it < iters:
            M = agop_update(Xtr, ab, alpha, K, M, L, p)
    hist["M_final"] = M
    return hist


# ---------------------------------------------------------------- runs and bookkeeping

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def env() -> dict:
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except OSError:
        commit = None
    return {"python": sys.version.split()[0], "torch": torch.__version__, "numpy": np.__version__,
            "threads": torch.get_num_threads(), "platform": platform.platform(), "commit": commit,
            "script_sha256": sha(Path(__file__))}


def split_path(seed: int, arm: str) -> Path:
    return SPLITS / f"confirm_exp1_eps2.0_add{P}_seed{seed}_{arm}.npy"


def out_path(seed: int, arm: str) -> Path:
    return RAW / f"rfm_add{P}_seed{seed}_{arm}_it{ITERS}_bw{BANDWIDTH}.json"


def write_atomic(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj), encoding="utf-8")
    os.replace(tmp, path)


def run_one(seed: int, arm: str) -> None:
    out = out_path(seed, arm)
    if out.exists() and json.loads(out.read_text(encoding="utf-8")).get("status") == "completed":
        print(f"skip {out.name} (completed)")
        return
    sp = split_path(seed, arm)
    meta = json.loads(sp.with_suffix(".json").read_text(encoding="utf-8"))
    idx = np.load(sp)
    if meta.get("p") != P or meta.get("task") != "add" or len(idx) != meta.get("n_train") or len(set(idx.tolist())) != len(idx):
        raise SystemExit(f"split {sp.name}: metadata mismatch")
    print(f"run seed {seed} arm {arm} (n_train {len(idx)})")
    t0 = time.time()
    h = rfm(idx, P, ITERS)
    M = h.pop("M_final")
    out.parent.mkdir(parents=True, exist_ok=True)               # s45: the first real run failed here (raw/ did not exist)
    mp = out.with_suffix(".M.npy")
    tmp = mp.with_name(mp.name + ".tmp")
    with open(tmp, "wb") as fh:                                   # atomic like write_atomic (Astra point 3)
        np.save(fh, M.numpy())
    os.replace(tmp, mp)
    rec = {"status": "error" if "error" in h else "completed", "seed": seed, "arm": arm, "p": P, "task": "add",
           "iters": ITERS, "bandwidth": BANDWIDTH, "ridge": 0.0, "agop_power": 0.5, "centering": True,
           "targets": meta.get("targets"), "split_file": str(sp.relative_to(ROOT)).replace("\\", "/"),
           "split_sha256": sha(sp), "seconds": round(time.time() - t0, 1), "env": env(), **h}
    write_atomic(out, rec)
    print(f"  -> {rec['status']} in {rec['seconds']} s, final test acc {h['test_acc'][-1]:.4f}")


def delta_pow(pF: np.ndarray, pG: np.ndarray, F: list[int], G: list[int]) -> float | None:
    s = lambda pw, S: float(pw[[k - 1 for k in S]].sum())   # noqa: E731  (same as confirm_p1.delta_pow)
    sums = [s(pw, S) for pw in (pF, pG) for S in (F, G)]
    if not all(np.isfinite(x) and x > 0 for x in sums):
        return None
    return float(np.log(sums[0] / sums[1]) + np.log(sums[3] / sums[2]))


def load(seed: int, arm: str) -> dict | None:
    f = out_path(seed, arm)
    if not f.exists():
        return None
    r = json.loads(f.read_text(encoding="utf-8"))
    if r.get("status") != "completed" or r.get("split_sha256") != sha(split_path(seed, arm)) or len(r["spec"]) != ITERS + 1:
        return None
    return r


def participation(P: np.ndarray) -> float | None:
    P = np.clip(P, 0, None)
    return float(P.sum() ** 2 / (P ** 2).sum()) if (P ** 2).sum() > 0 else None


def boot_ci(d: np.ndarray, rng: np.random.Generator) -> list[float]:
    m = rng.choice(d, size=(BOOT, len(d)), replace=True).mean(1)
    return [float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))]


def analyze(seeds: list[int]) -> dict:
    """Counts ("8/10") are over VALID rows (missing runs or non-positive target sums drop out of the denominator);
    read n and n_pos in pilot_summary_it<ITERS>.json alongside the reading. dpow_offdiag may be None for many seeds: a block
    without its diagonal is not PSD, its P(k) can be negative, and delta_pow then refuses (expected, not a data fault)."""
    rng = np.random.default_rng(101)
    rows, missing = [], []
    for s in seeds:
        r = {a: load(s, a) for a in "RFG"}
        if r["F"] is None or r["G"] is None:
            missing.append(s)
            continue
        T = {"F": r["F"]["targets"], "G": r["G"]["targets"]}
        row = {"seed": s, "acc_R": r["R"]["test_acc"][-1] if r["R"] else None,
               "acc_F": r["F"]["test_acc"][-1], "acc_G": r["G"]["test_acc"][-1],
               # descriptive: how sparse is the RFM spectrum at all? participation ratio (sum P)^2 / sum P^2 over k
               # (56 = flat, 1 = one frequency); the transformer uses ~5 frequencies
               "pr": {a: participation(np.array(r[a]["spec_offdiag"][-1])) for a in "RFG" if r[a]}}
        for key, it in (("dpow", -1), ("dpow_offdiag", -1), ("dpow_iter5", EARLY_ITER), ("dpow_iter1", 1)):
            spec = "spec_offdiag" if key == "dpow_offdiag" else "spec"
            row[key] = delta_pow(np.array(r["F"][spec][it]), np.array(r["G"][spec][it]), T["F"], T["G"])
        # descriptive (s44): Delta_pow per iteration; iteration 1 = first AGOP update from M_0 = I, the RFM counterpart
        # of the first-order account (the first update is fixed by the split and the initial kernel predictor)
        row["dpow_curve"] = [delta_pow(np.array(a), np.array(b), T["F"], T["G"]) for a, b in zip(r["F"]["spec"], r["G"]["spec"])]
        rows.append(row)
    accR = [r["acc_R"] for r in rows if r["acc_R"] is not None]
    gate = len(accR) >= 8 and sum(a >= GATE_ACC for a in accR) >= 8
    out = {"n": len(rows), "missing": missing, "gate_passed": gate, "rows": rows}
    for key in ("dpow", "dpow_offdiag", "dpow_iter5", "dpow_iter1"):
        d = np.array([r[key] for r in rows if r[key] is not None])
        if len(d) >= 2:
            out[key] = {"n": len(d), "mean": float(d.mean()), "ci95": boot_ci(d, rng), "n_pos": int((d > 0).sum())}
    if not gate:
        out["reading"] = "gate failed: RFM does not generalise on the random 30 % split -> no K2 reading"
    elif "dpow" in out:
        m = out["dpow"]
        if m["ci95"][0] > 0 and m["n_pos"] >= 8:
            out["reading"] = "positive: K2 also in RFM (pilot)"
        elif -0.5 <= m["ci95"][0] and m["ci95"][1] <= 0.5:
            out["reading"] = "negative: no steering in RFM (pilot)"
        else:
            out["reading"] = "unclear"
    write_atomic(HERE / f"pilot_summary_it{ITERS}.json", out)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    return out


# ---------------------------------------------------------------- self-test and reproduction

def dense_update(Xtr, alpha, K, M, L):
    """Direct transcription of their get_grads (dense n x c x d), sqrt by psd_sqrt."""
    n, d = Xtr.shape
    c = alpha.shape[1]
    X1 = (Xtr @ M).reshape(n, 1, d)
    step2 = (K.T @ (alpha.reshape(n, c, 1) @ X1).reshape(-1, c * d)).reshape(-1, c, d)
    step3 = (alpha.T @ K).T.reshape(n, c, 1) @ X1
    G = (step2 - step3) * -1 / L ** 2
    G = G - G.mean(0)
    agop = sum(g.T @ g for g in G) / n
    return psd_sqrt(agop)


def selftest() -> None:
    torch.manual_seed(0)
    p, L = 11, 2.5
    rng = np.random.default_rng(0)
    idx = rng.choice(p * p, size=60, replace=False)
    (ab, Xtr, Ytr, _), _ = data(idx, p)
    A = torch.randn(2 * p, 2 * p, dtype=DTYPE)
    M = torch.eye(2 * p, dtype=DTYPE) + 0.05 * (A @ A.T)
    K = gauss_kernel(Xtr, Xtr, M, L)
    alpha = torch.linalg.solve(K, Ytr)
    # session 45 (diagnosed in the window, _diag_s45.py): compare the AGOP BEFORE the square root. The one-hot AGOP has two
    # structural null directions (constant block sums), whose roundoff eigenvalues (~1e-16) psd_sqrt turns into ~1e-8, so the
    # post-sqrt matrices differ by ~2e-9 although the two AGOPs agree to ~1e-15. The run path is unchanged.
    global psd_sqrt
    keep_sqrt, psd_sqrt = psd_sqrt, (lambda X: X)
    try:
        fast, dense = agop_update(Xtr, ab, alpha, K, M, L, p), dense_update(Xtr, alpha, K, M, L)
    finally:
        psd_sqrt = keep_sqrt
    err = float((fast - dense).abs().max() / dense.abs().max())
    print(f"fast vs dense AGOP (before sqrt): rel. max error {err:.2e}")
    assert err < 1e-10
    B = torch.randn(7, 7, dtype=DTYPE)
    S = psd_sqrt(B @ B.T)
    assert float((S @ S - B @ B.T).abs().max()) < 1e-10 and float((S - S.T).abs().max()) < 1e-12
    # spectrum: a circulant block with a single frequency k0 has all its off-trace energy at k0
    v = np.arange(p)
    k0 = 3
    circ = np.cos(2 * np.pi * k0 * (v[:, None] - v[None, :]) / p)
    Mc = torch.zeros(2 * p, 2 * p, dtype=DTYPE)
    Mc[:p, :p] = torch.from_numpy(circ)
    sp = spectrum(Mc, p)
    assert abs(sp[k0 - 1] - p) < 1e-9 and np.abs(np.delete(sp, k0 - 1)).max() < 1e-9, sp
    assert abs(spectrum(torch.eye(2 * p, dtype=DTYPE), p).sum() - 2 * (p - 1)) < 1e-9     # flat floor 2 per k per block
    assert abs(delta_pow(np.array([4.0, 1.0]), np.array([1.0, 4.0]), [1], [2]) - 2 * np.log(4)) < 1e-12
    assert delta_pow(np.array([4.0, 0.0]), np.array([1.0, 4.0]), [1], [2]) is None
    # against the original code (external repo, sqrtm shimmed), if present
    if (EXTERNAL / "models" / "gaussian_kernel.py").exists():
        import types
        shim = types.ModuleType("scipy")
        shim.linalg = types.SimpleNamespace(sqrtm=lambda a: psd_sqrt(torch.from_numpy(a)).numpy())
        sys.modules.setdefault("scipy", shim)       # both sides use psd_sqrt here; its correctness is the S@S check above
        sys.path.insert(0, str(EXTERNAL))
        from models import gaussian_kernel as gk                                   # noqa: E402
        Kx = gk.gaussian_M(Xtr, Xtr, L, M)
        assert float((Kx - K).abs().max()) < 1e-12
        Mx, _ = gk.gaussian_M_update(Xtr, Xtr, L, M, alpha, K=Kx, centering=True, agop_power=0.5)
        err2 = float((Mx - psd_sqrt(fast)).abs().max() / Mx.abs().max())   # s45: fast is now the pre-sqrt AGOP
        print(f"fast vs external get_grads: rel. max error {err2:.2e}")
        assert err2 < 1e-8
    else:
        print("external repo missing: comparison with the original code skipped")
    print("selftest ok")


def reproduce() -> None:
    """Their default setting (p 61, x+y, 50 % random split, bandwidth 2.5, ridge 0, 50 iterations would be theirs; we
    stop at ITERS). Expectation from their paper: test accuracy near 1.0 after ~20 iterations. Output only printed + saved."""
    p = 61
    idx = np.random.default_rng(61).permutation(p * p)[: int(0.5 * p * p)]
    t0 = time.time()
    h = rfm(idx, p, ITERS)
    h.pop("M_final")
    write_atomic(HERE / f"reproduce_p61_it{ITERS}.json", {"p": p, "frac": 0.5, "iters": ITERS, "seconds": round(time.time() - t0, 1),
                                               "env": env(), **h})
    ok = h["test_acc"][-1] >= GATE_ACC                         # fixed before any run: otherwise blocker, no pilot runs
    print(f"p 61 / 50 %: final test acc {h['test_acc'][-1]:.4f}, {time.time() - t0:.0f} s -> "
          f"{'PASS' if ok else 'FAIL (blocker: own RFM does not reproduce the original setting)'}")


def seed_list(s: str) -> list[int]:
    a, _, b = s.partition("-")
    return list(range(int(a), int(b or a) + 1))


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    for f in ("--selftest", "--reproduce", "--run", "--analyze"):
        g.add_argument(f, action="store_true")
    ap.add_argument("--seeds", default="1000-1009")
    ap.add_argument("--arms", default="R,F,G")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--iters", type=int, default=ITERS, help="only for the pre-registered fallback (60), see README")
    a = ap.parse_args()
    globals()["ITERS"] = a.iters                                # part of the output file name
    torch.set_num_threads(a.threads)
    if a.selftest:
        selftest()
    elif a.reproduce:
        reproduce()
    elif a.run:
        for s in seed_list(a.seeds):
            for arm in a.arms.split(","):
                run_one(s, arm)
    else:
        analyze(seed_list(a.seeds))


if __name__ == "__main__":
    main()
