"""EXP-061 (pilot): does the gradient of the NEW data already push along the learned structure of the OLD targets? Definition: README.md
(registered before any EXP-061 run and gradient computation). Run under guarded_run.py.

Per seed s, t, direction (first split X, second Y): model at step t (pure X run, --steps t --save-model), W0 = W_E snapshot at step 0.
g = dL_Y/dW_E[:113] on the full Y train set; dW = W_E(t) - W_E(0) (rows :113). Pi_T projects the rows onto Fourier frequencies T.
c_own = cos(-Pi_own g, Pi_own dW), c_other = cos(-Pi_other g, Pi_other dW); c(s, t) = mean of both directions.
V1: Spearman over t of the mean c_own > 0, mean c_own(50) > 0 and > mean c_own(10). V2: mean over t of within-t Spearman(c_own, pi) > 0.3.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
E59 = LAB / "experiments/EXP-059-momentum-exposure"
_spec = importlib.util.spec_from_file_location("exp059", E59 / "analyze.py")
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)
A = B.A
_s51 = importlib.util.spec_from_file_location("exp051", LAB / "experiments/EXP-051-functional-ablation/analyze.py")
E51 = importlib.util.module_from_spec(_s51)
_s51.loader.exec_module(E51)

P, TS, SEEDS = 113, (10, 20, 25, 35, 50), tuple(range(400, 410))


def project(M: np.ndarray, T: list[int]) -> np.ndarray:
    """Rows of M (P x d) projected onto the real Fourier subspace of frequencies T (cos and sin of each k)."""
    a = np.arange(P)
    Bm = np.concatenate([np.stack([np.cos(2 * np.pi * k * a / P), np.sin(2 * np.pi * k * a / P)], 1) for k in T], 1)
    Q, _ = np.linalg.qr(Bm)
    return Q @ (Q.T @ M)


def cos(u: np.ndarray, v: np.ndarray) -> float:
    nu, nv = np.linalg.norm(u), np.linalg.norm(v)
    return float((u * v).sum() / (nu * nv)) if nu > 0 and nv > 0 else float("nan")


def grad_we(model, idx: np.ndarray) -> np.ndarray:
    import torch
    model.zero_grad()
    a, b = idx // P, idx % P
    x = torch.from_numpy(np.stack([a, b, np.full(len(idx), P)], 1)).long()
    y = torch.from_numpy((a + b) % P).long()
    torch.nn.functional.cross_entropy(model.logits_last(x)[:, :P], y).backward()
    return model.W_E.grad.detach().numpy().astype(np.float64)[:P]


def one(s: int, t: int, first: str, second: str, own: list[int], other: list[int]) -> dict | str:
    st1 = A.stem(s, B.OM, first)
    d = A.find_run(HERE / f"raw_t{t}", f"EXP-0*_baseline_seed{s}_thr*_{st1}" + A.SUF)
    L = A.load_run(d, A.Expect(seed=s, device=A.DEV, max_steps=t, split_file=A.SPL / f"{st1}.npy", test_file=A.SPL / f"seed{s}_test.npy",
                               config={"p": 113, "task": "add"}, snapshots_at=(0, t), files=("model_final.pt",)))
    if L.status != "ok":
        return f"{first}@{t}: {L.status}: {L.reason}"
    m = E51.load_model(L.path)
    W = m.W_E.detach().numpy().astype(np.float64)[:P]
    W0, Wt = (np.asarray(L.snapshot(k), dtype=np.float64)[:P] for k in (0, t))
    if not np.allclose(W, Wt, atol=1e-5):
        return f"{first}@{t}: model W_E differs from the step-{t} snapshot"
    g = grad_we(m, np.load(A.SPL / f"{A.stem(s, B.OM, second)}.npy"))
    dW = Wt - W0
    return {"c_own": cos(-project(g, own), project(dW, own)), "c_other": cos(-project(g, other), project(dW, other))}


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def main() -> None:
    rows = {r["seed"]: r for r in json.loads((E59 / "summary.json").read_text(encoding="utf-8"))["rows"] if r["valid"]}
    pts, bad = [], []
    for s in SEEDS:
        meta = json.loads((A.SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        for t in TS:
            ab, ba = one(s, t, "A", "B", F, G), one(s, t, "B", "A", G, F)
            if isinstance(ab, str) or isinstance(ba, str):
                bad.append(ab if isinstance(ab, str) else ba)
                continue
            pts.append({"seed": s, "t": t, "c_own": (ab["c_own"] + ba["c_own"]) / 2, "c_other": (ab["c_other"] + ba["c_other"]) / 2,
                        "pi": rows[s][f"pi_n{t}"] if s in rows else None})
    means = {t: float(np.mean([p["c_own"] for p in pts if p["t"] == t])) for t in TS if any(p["t"] == t for p in pts)}
    within = {t: spearman(np.array([p["c_own"] for p in pts if p["t"] == t]), np.array([p["pi"] for p in pts if p["t"] == t]))
              for t in TS if sum(p["t"] == t and p["pi"] is not None for p in pts) >= 5}
    v1 = (len(means) == len(TS) and spearman(np.array(list(means)), np.array(list(means.values()))) > 0
          and means[50] > 0 and means[50] > means[10])
    v2 = len(within) == len(TS) and float(np.mean(list(within.values()))) > 0.3
    verdict = "Kandidat" if v1 and v2 else ("Uhr, keine Seed-Vorhersage" if v1 else "verworfen")
    out = {"n_points": len(pts), "n_bad": len(bad), "bad": bad[:3], "c_own_mean": means,
           "c_other_mean": {t: float(np.mean([p["c_other"] for p in pts if p["t"] == t])) for t in means},
           "within_t_spearman": within, "mean_within": float(np.mean(list(within.values()))) if within else None,
           "V1": v1, "V2": v2, "verdict": verdict if not bad else "nicht auswertbar", "points": pts}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "points"}, indent=1, default=str))


def selftest() -> None:
    rng = np.random.default_rng(0)
    M = rng.standard_normal((P, 6))
    Pm = project(M, [3, 7])
    assert np.allclose(project(Pm, [3, 7]), Pm) and np.allclose(project(M - Pm, [3, 7]), 0, atol=1e-10)
    a = np.arange(P)
    wave = np.outer(np.cos(2 * np.pi * 3 * a / P), np.ones(6))
    assert np.allclose(project(wave, [3]), wave) and np.allclose(project(wave, [4]), 0, atol=1e-10)
    assert abs(cos(wave, 2 * wave) - 1) < 1e-12 and abs(cos(wave, -wave) + 1) < 1e-12
    print("[exp061] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
