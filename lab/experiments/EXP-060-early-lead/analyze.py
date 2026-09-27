"""EXP-060 (EXPLORATION, post hoc on stored EXP-058/059 runs, no new training): does the A-target lead that W_E has built up by the switch
time t predict the later persistence pi? Definition and caveats: README.md. Run under guarded_run.py.

Per seed s (400-409), normal switch runs at t in T and direction AB/BA: dW = W_E(t) - W_E(0) of the switch run (identical to the pure first
run up to t). lead = log[P_own(dW) / P_other(dW)] with own = targets of the first split; rel = ||dW|| / ||W_E(0)|| (rows 0..112).
x(s, t) = mean over both directions of lead; pi(s, t) from EXP-059 summary rows (t = 25 from the same rows, taken from EXP-058 runs).
Reported: pooled Spearman(x, pi), within-t Spearman across seeds (does the lead explain seed-to-seed spread at fixed t?), per-t means.
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
A = B.A                                   # EXP-056 helpers (loader, stems, group power)
T = B.T_NORMAL


def snaps(s: int, kind: str, t: int) -> tuple[np.ndarray, np.ndarray] | str:
    first, second = kind[0], kind[1]
    st1 = A.stem(s, B.OM, first)
    steps = 2000 + t
    pat = f"EXP-0*_baseline_seed{s}_thr*_{st1}_to_{A.stem(s, B.OM, second)}_at{t}" + A.SUF
    L = A.load_run(A.find_run(B.root_for(t), pat),
                   A.Expect(seed=s, device=A.DEV, max_steps=steps, split_file=A.SPL / f"{st1}.npy", test_file=A.SPL / f"seed{s}_test.npy",
                            switch_file=A.SPL / f"{A.stem(s, B.OM, second)}.npy", config={"p": 113, "task": "add"}, snapshots_at=(0, t)))
    if L.status != "ok":
        return f"{kind}@{t}: {L.status}: {L.reason}"
    return np.asarray(L.snapshot(0), dtype=np.float64), np.asarray(L.snapshot(t), dtype=np.float64)


def lead(W0: np.ndarray, Wt: np.ndarray, own: list[int], other: list[int]) -> tuple[float, float]:
    pw = A._a43.group_power(Wt - W0, "add", 113)[0]
    rel = float(np.linalg.norm((Wt - W0)[:113]) / np.linalg.norm(W0[:113]))
    return float(np.log(pw[[k - 1 for k in own]].sum() / pw[[k - 1 for k in other]].sum())), rel


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def main() -> None:
    summ = json.loads((E59 / "summary.json").read_text(encoding="utf-8"))
    rows = {r["seed"]: r for r in summ["rows"] if r["valid"]}
    pts, bad = [], []
    for s, r in rows.items():
        meta = json.loads((A.SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        for t in T:
            ab, ba = snaps(s, "AB", t), snaps(s, "BA", t)
            if isinstance(ab, str) or isinstance(ba, str):
                bad.append(ab if isinstance(ab, str) else ba)
                continue
            l1, r1 = lead(*ab, F, G)
            l2, r2 = lead(*ba, G, F)
            pts.append({"seed": s, "t": t, "x": (l1 + l2) / 2, "rel": (r1 + r2) / 2, "pi": r[f"pi_n{t}"]})
    x, y = np.array([p["x"] for p in pts]), np.array([p["pi"] for p in pts])
    within = {}
    for t in T:
        q = [p for p in pts if p["t"] == t]
        if len(q) >= 5:
            within[str(t)] = {"n": len(q), "spearman": spearman(np.array([p["x"] for p in q]), np.array([p["pi"] for p in q])),
                              "x_mean": float(np.mean([p["x"] for p in q])), "rel_mean": float(np.mean([p["rel"] for p in q])),
                              "pi_mean": float(np.mean([p["pi"] for p in q]))}
    out = {"n_points": len(pts), "n_bad": len(bad), "bad": bad[:3], "pooled_spearman": spearman(x, y) if len(pts) > 2 else None,
           "within_t": within, "points": pts}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "points"}, indent=1))


def selftest() -> None:
    assert abs(spearman(np.arange(5.0), np.arange(5.0) ** 3) - 1.0) < 1e-12
    rng = np.random.default_rng(0)
    W0 = rng.standard_normal((114, 8))
    a = np.arange(113)
    Wt = W0.copy()
    Wt[:113, 0] += np.cos(2 * np.pi * 3 * a / 113)
    l, rel = lead(W0, Wt, [3], [5])
    assert l > 10 and rel > 0
    print("[exp060] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
