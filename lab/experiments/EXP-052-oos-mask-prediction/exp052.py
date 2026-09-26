"""EXP-052: frozen out-of-sample prediction of the W_E spectrum from the train split alone (K1 beyond add mod 113).

Cases: the 20 random-split (arm R, eps 0) runs of EXP-043 (add mod 97 and mul mod 113, seeds 70-79, GPU, 2000 steps),
which had NOT been run when the predictions were frozen (session 14, 2026-09-26). Definition: README.md.

  --predict   pure numpy on the split files: M0, M0c, count spectrum in group coordinates -> predictions.json (frozen)
  --selftest  pure numpy: our M0 reproduces make_split.py (F/G targets = M0 top-5, R "M0_top5") for all 60 splits
  (default)   analysis after the EXP-043 R runs: run through guarded_run.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
E43 = LAB / "experiments/EXP-043-generalize-steering"
sys.path.insert(0, str(E43))
sys.path.insert(0, str(LAB / "tools"))
from make_split import group_coords, mask_power, n_freq  # noqa: E402
from result_loader import Expect, find_run, load_run  # noqa: E402

TASKS = (("add", 97), ("mul", 113))
SEEDS = tuple(range(70, 80))
STEP, EXTRA_STEPS, M, ALPHA, MIN_VALID = 2000, (50, 250, 500, 1000), 5, 0.05, 8
N_PERM, PERM_SEED = 20_000, 52
PRED = HERE / "predictions.json"
PREDICTORS = ("M0", "M0c", "CNT")


def stem(task: str, p: int, s: int) -> str:
    return f"split_{task}{p}_seed{s}_eps0.0_R"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def spectra(idx: np.ndarray, task: str, p: int) -> dict[str, np.ndarray]:
    """M0 (EXP-015), M0c (left + right before |.|^2) and the per-position token-count spectrum, all in group coordinates
    (mul: pairs with a zero dropped), k = 1..(n-1)//2 with k and n-k combined (Nyquist of even n excluded)."""
    u, v, valid, n = group_coords(task, p)
    Mk = np.zeros((n, n))
    sel = np.zeros(p * p, bool)
    sel[idx] = True
    sel &= valid
    Mk[u[sel], v[sel]] = 1.0
    t = np.arange(n)
    o = (t[None, :] - t[:, None]) % n
    L, R = Mk[t[:, None], o], Mk[o, t[:, None]]
    K = n_freq(n)
    fold = lambda x: x[1:K + 1] + x[n - K:][::-1]   # noqa: E731
    FL, FR = np.fft.fft(L, axis=0), np.fft.fft(R, axis=0)
    return {"M0": fold((np.abs(FL) ** 2 + np.abs(FR) ** 2).sum(axis=1)),
            "M0c": fold((np.abs(FL + FR) ** 2).sum(axis=1)),
            "CNT": fold(np.abs(np.fft.fft(Mk.sum(1))) ** 2 + np.abs(np.fft.fft(Mk.sum(0))) ** 2)}


def top(pw: np.ndarray) -> list[int]:
    return sorted(int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:M])


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx = np.argsort(np.argsort(x, kind="stable"), kind="stable")
    ry = np.argsort(np.argsort(y, kind="stable"), kind="stable")
    return float(np.corrcoef(rx, ry)[0, 1])


def rbar(pw: np.ndarray, K: list[int]) -> float:
    rank = np.argsort(np.argsort(-pw, kind="stable"), kind="stable")
    return float((rank[[k - 1 for k in K]] / (len(pw) - 1)).mean())


def predict() -> None:
    if PRED.exists():
        raise SystemExit(f"{PRED.name} exists: predictions are frozen (delete only with a JOURNAL entry)")
    out: dict = {"frozen": "session 14, 2026-09-26, before any EXP-043 R run", "cases": {}}
    for task, p in TASKS:
        for s in SEEDS:
            f = E43 / f"splits/{stem(task, p, s)}.npy"
            sp = spectra(np.load(f), task, p)
            meta = json.loads(f.with_name(f"{stem(task, p, s)}.json").read_text(encoding="utf-8"))
            if top(sp["M0"]) != meta["M0_top5"]:          # integrity guard: same M0 as make_split.py recorded
                raise SystemExit(f"M0 top-5 differs from make_split for {f.name}")
            out["cases"][f"{task}{p}_seed{s}"] = {
                "split_file": f.relative_to(LAB.parent).as_posix(), "split_sha256": file_sha256(f),
                **{f"{k}_top5": top(v) for k, v in sp.items()}, **{k: v.tolist() for k, v in sp.items()}}
    PRED.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"[exp052] wrote {PRED.name}: {len(out['cases'])} cases")


def selftest() -> None:
    """Our M0 must equal make_split.mask_power and reproduce the recorded top-5 of every EXP-043 split (60 files)."""
    n_checked = 0
    for task, p in TASKS:
        for s in SEEDS:
            for arm, eps in (("F", "2.0"), ("G", "2.0"), ("R", "0.0")):
                st = f"split_{task}{p}_seed{s}_eps{eps}_{arm}"
                idx = np.load(E43 / f"splits/{st}.npy")
                meta = json.loads((E43 / f"splits/{st}.json").read_text(encoding="utf-8"))
                sp = spectra(idx, task, p)
                assert np.allclose(sp["M0"], mask_power(idx, task, p)), st
                assert top(sp["M0"]) == meta["M0_top5"], (st, top(sp["M0"]), meta["M0_top5"])
                if arm != "R":
                    assert top(sp["M0"]) == sorted(meta["targets"]), st
                assert np.all(sp["M0c"] >= 0) and np.all(sp["CNT"] >= 0)
                n_checked += 1
    # M0c: identical left/right structure (symmetric mask) -> |FL + FR|^2 = 4|FL|^2 = 2 M0 exactly
    for task, p in TASKS:
        u, v, valid, n = group_coords(task, p)
        rng = np.random.default_rng(0)
        pairs = rng.choice(np.flatnonzero(valid), 500, replace=False)
        ua, va = u[pairs], v[pairs]
        flat = lambda uu, vv: np.flatnonzero(valid & np.isin(u * n + v, uu * n + vv))  # noqa: E731
        sym = np.union1d(flat(ua, va), flat(va, ua))
        sp = spectra(sym, task, p)
        assert np.allclose(sp["M0c"], 2 * sp["M0"]), task
    assert abs(spearman(np.arange(10.0), np.arange(10.0) ** 3) - 1) < 1e-12
    print(f"[exp052] selftest ok ({n_checked} splits)", flush=True)


def group_power(W: np.ndarray, task: str, p: int) -> np.ndarray:
    sys.path.insert(0, str(E43))
    from analyze import group_power as gp43   # the EXP-043 K measurement, unchanged
    return gp43(W, task, p)[0]


def perm_p(R: np.ndarray, rng: np.random.Generator) -> float:
    """R[i, j] = rho(prediction of split j, W_E spectrum of run i); matched = diagonal. One-sided: diagonal larger."""
    n = len(R)
    obs = np.trace(R) / n
    null = np.array([R[np.arange(n), rng.permutation(n)].mean() for _ in range(N_PERM)])
    return float((np.sum(null >= obs - 1e-12) + 1) / (N_PERM + 1))


def sign_flip_p(d: np.ndarray, rng: np.random.Generator) -> float:
    """One-sided (mean d > 0); exact for n <= 16, else Monte Carlo."""
    if len(d) <= 16:
        import itertools
        flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    else:
        flips = rng.choice((1, -1), size=(N_PERM, len(d)))
    return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def holm(ps: dict[str, float]) -> dict[str, float]:
    order = sorted(ps, key=ps.get)
    adj, run = {}, 0.0
    for i, k in enumerate(order):
        run = max(run, min(1.0, (len(order) - i) * ps[k]))
        adj[k] = run
    return adj


def analyze() -> None:
    pred = json.loads(PRED.read_text(encoding="utf-8"))["cases"]
    rng = np.random.default_rng(PERM_SEED)
    out: dict = {"tasks": {}}
    all_rows = []
    for task, p in TASKS:
        rows, W = [], {}
        for s in SEEDS:
            c = pred[f"{task}{p}_seed{s}"]
            f = LAB.parent / c["split_file"]
            if file_sha256(f) != c["split_sha256"]:
                raise SystemExit(f"split file changed after freezing: {f}")
            sp = spectra(np.load(f), task, p)
            for k in PREDICTORS:                       # the frozen numbers must be what the code computes today
                assert np.allclose(sp[k], c[k]), (task, s, k)
            L = load_run(find_run(E43 / "raw", f"EXP-043_baseline_seed{s}_thr*_{stem(task, p, s)}_*"),
                         Expect(seed=s, device="cuda", max_steps=STEP, split_file=f, config={"p": p, "task": task},
                                snapshots_at=(0, STEP) + EXTRA_STEPS))
            if L.status != "ok":
                rows.append({"seed": s, "valid": False, "reason": f"{L.status}: {L.reason}"})
                continue
            pw = group_power(L.snapshot(STEP), task, p)
            W[s] = pw
            K = top(pw)
            r = {"seed": s, "valid": True, "K": K, "E0_top5": top(group_power(L.snapshot(0), task, p))}
            for k in PREDICTORS:
                r[f"rho_{k}"], r[f"rbar_{k}"], r[f"ov_{k}"] = spearman(sp[k], pw), rbar(sp[k], K), len(set(c[f"{k}_top5"]) & set(K))
            e0 = group_power(L.snapshot(0), task, p)
            r["rho_E0"], r["rbar_E0"] = spearman(e0, pw), rbar(e0, K)
            r["rho_M0_at"] = {t: spearman(sp["M0"], group_power(L.snapshot(t), task, p)) for t in EXTRA_STEPS}
            rows.append(r)
        valid = [r for r in rows if r["valid"]]
        t_out: dict = {"n_valid": len(valid), "rows": rows}
        if len(valid) < MIN_VALID:
            t_out["verdict"] = "nicht auswertbar"
            out["tasks"][f"{task}{p}"] = t_out
            continue
        vs = [r["seed"] for r in valid]
        Rm = np.array([[spearman(np.array(pred[f"{task}{p}_seed{j}"]["M0"]), W[i]) for j in vs] for i in vs])
        t_out["rho_M0_matched"] = float(np.trace(Rm) / len(vs))
        t_out["rho_M0_foreign"] = float((Rm.sum() - np.trace(Rm)) / (len(vs) * (len(vs) - 1)))
        t_out["p_primary"] = perm_p(Rm, rng)
        for k in PREDICTORS + ("E0",):
            t_out[f"rho_{k}_mean"] = float(np.mean([r[f"rho_{k}"] for r in valid]))
            t_out[f"rbar_{k}_mean"] = float(np.mean([r[f"rbar_{k}"] for r in valid]))
        t_out["rho_M0_at_mean"] = {t: float(np.mean([r["rho_M0_at"][t] for r in valid])) for t in EXTRA_STEPS}
        out["tasks"][f"{task}{p}"] = t_out
        all_rows += valid
    ps = {t: v["p_primary"] for t, v in out["tasks"].items() if "p_primary" in v}
    adj = holm(ps)
    for t, v in out["tasks"].items():
        if t in adj:
            v["p_primary_holm"] = adj[t]
            v["verdict"] = ("K1 gilt hier (Split sagt Spektrum voraus)" if adj[t] < ALPHA and v["rho_M0_matched"] > v["rho_M0_foreign"]
                            else "nicht bestätigt")
    if len(all_rows) >= 2 * MIN_VALID:                 # secondaries, pooled over tasks (runs are independent)
        sec = {}
        for name, a, b in (("S1_M0c_better_than_M0", "M0c", "M0"), ("S2_M0_better_than_E0", "M0", "E0"),
                           ("S3_M0_better_than_CNT", "M0", "CNT")):
            d = np.array([r[f"rho_{a}"] - r[f"rho_{b}"] for r in all_rows])
            sec[name] = {"mean_diff": float(d.mean()), "n_pos": int((d > 0).sum()), "n": len(d), "p_one_sided": sign_flip_p(d, rng)}
        out["secondary"] = sec
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({t: {k: v for k, v in d.items() if k != "rows"} for t, d in out["tasks"].items()}, indent=1))
    print(json.dumps(out.get("secondary"), indent=1))


if __name__ == "__main__":
    arg = sys.argv[1:]
    if arg == ["--predict"]:
        predict()
    elif arg == ["--selftest"]:
        selftest()
    elif arg == []:
        analyze()
    else:
        raise SystemExit(__doc__)
