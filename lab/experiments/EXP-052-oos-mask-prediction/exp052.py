"""EXP-052: frozen out-of-sample prediction of the W_E spectrum from the train split alone (K1 beyond add mod 113).

Cases: the 20 random-split (arm R, eps 0) runs of EXP-043 (add mod 97 and mul mod 113, seeds 70-79, GPU, 2000 steps),
which had NOT been run when the predictions were frozen (session 14, 2026-09-26). Definition: README.md.

  --predict   pure numpy on the split files: M0, M0c, count spectrum in group coordinates -> predictions.json (frozen)
  --predict-d59  Nachtrag a (before any run): the same for the 10 D_59 random splits of EXP-046 -> predictions_d59.json
  --predict-intadd  Nachtrag b (before any run): non-modular a + b (EXP-048 arm R), k = 6..56 only -> predictions_intadd.json
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
E46 = LAB / "experiments/EXP-046-dihedral-steering"
E48 = LAB / "experiments/EXP-048-intadd-steering"
sys.path.insert(0, str(E43))
sys.path.append(str(E46))                  # appended: EXP-046 also has a make_split.py (must not shadow EXP-043)
sys.path.insert(0, str(LAB / "tools"))
from make_split import group_coords, mask_power, n_freq  # noqa: E402
from result_loader import Expect, find_run, load_run  # noqa: E402
import dihedral as dh  # noqa: E402  (EXP-046: D_n, irreps, non-abelian M0)

TASKS = (("add", 97), ("mul", 113))
SEEDS = tuple(range(70, 80))
STEP, EXTRA_STEPS, M, ALPHA, MIN_VALID = 2000, (50, 250, 500, 1000), 5, 0.05, 8
N_PERM, PERM_SEED = 20_000, 52
PRED = HERE / "predictions.json"
PRED_D59 = HERE / "predictions_d59.json"
PRED_INT = HERE / "predictions_intadd.json"
P_INT, KMAX_INT, KLO_INT, SEEDS_INT = 113, 56, 6, tuple(range(160, 170))   # EXP-048: k <= 5 carry the number line
N59, SEEDS_D59, EXTRA_D59 = 59, tuple(range(140, 150)), (250, 500, 1000)   # D_59 spectra every 250 steps (group_train)
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


def spectra_d59(idx: np.ndarray) -> dict[str, np.ndarray]:
    """Non-abelian analogues on D_59, irreps k = 1..29: M0 = dihedral.mask_power (EXP-046), M0c = the same with the left and
    right indicator summed before the norm, CNT = irrep power of the left and right token-count vectors."""
    n, G = N59, 2 * N59
    T = dh.compose_table(n)
    Mk = np.zeros((G, G))
    Mk[idx // G, idx % G] = 1.0
    inv = np.argmax(T == 0, axis=1)
    t, c = np.arange(G)[:, None], np.arange(G)[None, :]
    left, right = Mk[t, T[inv[t], c]], Mk[T[c, inv[t]], t]
    B, labels = dh.irrep_basis(n)
    m0c = []
    for k in range(1, dh.n_irrep2(n) + 1):
        r = dh.rho(n, k).reshape(G, 4)
        m0c.append(2.0 * float((((left + right).T @ r) ** 2).sum()))
    cnt = dh.irrep_power(Mk.sum(1)[:, None], B, labels, n) + dh.irrep_power(Mk.sum(0)[:, None], B, labels, n)
    return {"M0": dh.mask_power(idx, n), "M0c": np.array(m0c), "CNT": cnt}


def spectra_intadd(idx: np.ndarray) -> dict[str, np.ndarray]:
    """Integer addition (outputs 0..224): M0 as EXP-048 make_split.mask_power, M0c coherent, CNT of the a/b counts;
    returned for k = KLO_INT..56 only (index 0 = k 6)."""
    P, NC = P_INT, 2 * P_INT - 1
    Mk = np.zeros((P, P))
    Mk[idx // P, idx % P] = 1.0
    t, c = np.arange(P)[:, None], np.arange(NC)[None, :]
    o = c - t
    ok = (o >= 0) & (o < P)
    oc = np.clip(o, 0, P - 1)
    L, R = np.where(ok, Mk[t, oc], 0.0), np.where(ok, Mk[oc, t], 0.0)
    fold = lambda x: (x[1:KMAX_INT + 1] + x[P - KMAX_INT:][::-1])[KLO_INT - 1:]   # noqa: E731
    FL, FR = np.fft.fft(L, axis=0), np.fft.fft(R, axis=0)
    return {"M0": fold((np.abs(FL) ** 2 + np.abs(FR) ** 2).sum(axis=1)), "M0c": fold((np.abs(FL + FR) ** 2).sum(axis=1)),
            "CNT": fold(np.abs(np.fft.fft(Mk.sum(1))) ** 2 + np.abs(np.fft.fft(Mk.sum(0))) ** 2)}


def detrend_dft_intadd(W: np.ndarray) -> np.ndarray:
    """EXP-048 primary measurement: per column remove the least-squares line in a, DFT power k = 1..56; here k >= 6."""
    X = np.stack([np.ones(P_INT), np.arange(P_INT, dtype=float)], 1)
    D = W - X @ np.linalg.lstsq(X, W, rcond=None)[0]
    pw = (np.abs(np.fft.fft(D, axis=0)) ** 2).sum(axis=1)
    return (pw[1:KMAX_INT + 1] + pw[P_INT - KMAX_INT:][::-1])[KLO_INT - 1:]


def predict_intadd() -> None:
    if PRED_INT.exists():
        raise SystemExit(f"{PRED_INT.name} exists: predictions are frozen (delete only with a JOURNAL entry)")
    out: dict = {"frozen": "session 14, 2026-09-26, Nachtrag b, before any EXP-048 run", "k_first": KLO_INT, "cases": {}}
    for s in SEEDS_INT:
        name = f"split_intadd113_seed{s}_eps0.0_R"
        f = E48 / f"splits/{name}.npy"
        sp = spectra_intadd(np.load(f))
        out["cases"][f"intadd_seed{s}"] = {
            "split_file": f.relative_to(LAB.parent).as_posix(), "split_sha256": file_sha256(f),
            **{f"{k}_top5": [x + KLO_INT - 1 for x in top(v)] for k, v in sp.items()}, **{k: v.tolist() for k, v in sp.items()}}
    PRED_INT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"[exp052] wrote {PRED_INT.name}: {len(out['cases'])} cases (k = {KLO_INT}..{KMAX_INT})")


def predict_d59() -> None:
    if PRED_D59.exists():
        raise SystemExit(f"{PRED_D59.name} exists: predictions are frozen (delete only with a JOURNAL entry)")
    out: dict = {"frozen": "session 14, 2026-09-26, Nachtrag a, before any EXP-046 run", "cases": {}}
    for s in SEEDS_D59:
        f = E46 / f"splits/split_D{N59}_seed{s}_eps0.0_R.npy"
        sp = spectra_d59(np.load(f))
        meta = json.loads(f.with_name(f"split_D{N59}_seed{s}_eps0.0_R.json").read_text(encoding="utf-8"))
        if top(sp["M0"]) != meta["M0_top5"]:
            raise SystemExit(f"M0 top-5 differs from EXP-046 make_split for {f.name}")
        out["cases"][f"D59_seed{s}"] = {
            "split_file": f.relative_to(LAB.parent).as_posix(), "split_sha256": file_sha256(f),
            **{f"{k}_top5": top(v) for k, v in sp.items()}, **{k: v.tolist() for k, v in sp.items()}}
    PRED_D59.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"[exp052] wrote {PRED_D59.name}: {len(out['cases'])} cases")


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
    for s in SEEDS_D59:                                  # Nachtrag a: D_59 M0 reproduces EXP-046 make_split (30 splits)
        for arm, eps in (("F", "2.0"), ("G", "2.0"), ("R", "0.0")):
            st = f"split_D{N59}_seed{s}_eps{eps}_{arm}"
            sp = spectra_d59(np.load(E46 / f"splits/{st}.npy"))
            meta = json.loads((E46 / f"splits/{st}.json").read_text(encoding="utf-8"))
            assert top(sp["M0"]) == meta["M0_top5"], st
            assert len(sp["M0c"]) == len(sp["CNT"]) == dh.n_irrep2(N59) and np.all(sp["M0c"] >= 0), st
            n_checked += 1
    import importlib.util                              # Nachtrag b: intadd M0 = EXP-048 make_split.mask_power (k >= 6)
    spec = importlib.util.spec_from_file_location("make_split_048", E48 / "make_split.py")
    mk48 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mk48)
    for s in SEEDS_INT:
        for arm, eps in (("F", "2.0"), ("G", "2.0"), ("R", "0.0")):
            idx = np.load(E48 / f"splits/split_intadd113_seed{s}_eps{eps}_{arm}.npy")
            assert np.allclose(spectra_intadd(idx)["M0"], mk48.mask_power(idx)[KLO_INT - 1:]), (s, arm)
            n_checked += 1
    a_ = np.arange(P_INT, dtype=float)
    ramp = np.outer(a_, np.linspace(1, 2, 4))
    wave = np.outer(np.cos(2 * np.pi * 9 * a_ / P_INT), np.ones(4))
    assert detrend_dft_intadd(5 * ramp).max() < 1e-12 * P_INT ** 3
    assert int(np.argmax(detrend_dft_intadd(5 * ramp + wave))) + KLO_INT == 9
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


def run_powers_043(task: str, p: int, s: int, f: Path) -> tuple[str | None, dict[int, np.ndarray]]:
    """W_E power in the EXP-043 group basis at 0, the extra steps and 2000 (None = valid)."""
    L = load_run(find_run(E43 / "raw", f"EXP-043_baseline_seed{s}_thr*_{stem(task, p, s)}_{task}{p}_devcuda"),
                 Expect(seed=s, device="cuda", max_steps=STEP, split_file=f, config={"p": p, "task": task},
                        snapshots_at=(0, STEP) + EXTRA_STEPS))
    if L.status != "ok":
        return f"{L.status}: {L.reason}", {}
    return None, {t: group_power(L.snapshot(t), task, p) for t in (0, STEP) + EXTRA_STEPS}


def run_powers_d59(s: int, f: Path) -> tuple[str | None, dict[int, np.ndarray]]:
    """Irrep power of W_E as logged by EXP-046 group_train.py (spectra.npy) at 0, 250, 500, 1000, 2000."""
    L = load_run(find_run(E46 / "raw", f"EXP-046_seed{s}_split_D{N59}_seed{s}_eps0.0_R_devcuda"),
                 Expect(seed=s, device="cuda", max_steps=STEP, split_file=f, config={"p": 2 * N59, "group": f"D{N59}"},
                        at=(0, STEP) + EXTRA_D59))
    if L.status != "ok":
        return f"{L.status}: {L.reason}", {}
    return None, {t: L.spectrum(t) for t in (0, STEP) + EXTRA_D59}


def run_powers_intadd(s: int, f: Path) -> tuple[str | None, dict[int, np.ndarray]]:
    """Detrended final W_E (we_final.npy, step 2000) of the EXP-048 R run; no step-0 W_E is stored -> no E0 here."""
    L = load_run(find_run(E48 / "raw", f"EXP-048_seed{s}_split_intadd113_seed{s}_eps0.0_R_devcuda"),
                 Expect(seed=s, device="cuda", max_steps=STEP, split_file=f, config={"p": 225}, at=(STEP,),
                        files=("we_final.npy",)))
    if L.status != "ok":
        return f"{L.status}: {L.reason}", {}
    return None, {STEP: detrend_dft_intadd(np.load(L.path / "we_final.npy").astype(np.float64))}


def case_rows(name: str, seeds: tuple[int, ...], pred: dict, spec_fn, run_fn, extra: tuple[int, ...],
              rng: np.random.Generator, off: int = 0) -> tuple[dict, list[dict]]:
    """off: frequency of vector index 0 minus 1 (0 for k = 1.., 5 for intadd k = 6..)."""
    rows, W = [], {}
    for s in seeds:
        c = pred[f"{name}_seed{s}"]
        f = LAB.parent / c["split_file"]
        if file_sha256(f) != c["split_sha256"]:
            raise SystemExit(f"split file changed after freezing: {f}")
        sp = spec_fn(np.load(f))
        for k in PREDICTORS:                           # the frozen numbers must be what the code computes today
            if not np.allclose(sp[k], c[k]):
                raise SystemExit(f"frozen {k} differs from today's computation: {name} seed {s}")
        why, pw_at = run_fn(s, f)
        if why is not None:
            rows.append({"seed": s, "valid": False, "reason": why})
            continue
        pw = W[s] = pw_at[STEP]
        K = top(pw)
        r = {"seed": s, "valid": True, "K": [k + off for k in K]}
        for k in PREDICTORS:
            r[f"rho_{k}"], r[f"rbar_{k}"] = spearman(sp[k], pw), rbar(sp[k], K)
            r[f"ov_{k}"] = len(set(c[f"{k}_top5"]) & set(r["K"]))
        if 0 in pw_at:
            r["E0_top5"] = [k + off for k in top(pw_at[0])]
            r["rho_E0"], r["rbar_E0"] = spearman(pw_at[0], pw), rbar(pw_at[0], K)
        r["rho_M0_at"] = {t: spearman(sp["M0"], pw_at[t]) for t in extra}
        rows.append(r)
    valid = [r for r in rows if r["valid"]]
    t_out: dict = {"n_valid": len(valid), "rows": rows}
    if len(valid) < MIN_VALID:
        t_out["verdict"] = "nicht auswertbar"
        return t_out, []
    vs = [r["seed"] for r in valid]
    Rm = np.array([[spearman(np.array(pred[f"{name}_seed{j}"]["M0"]), W[i]) for j in vs] for i in vs])
    t_out["rho_M0_matched"] = float(np.trace(Rm) / len(vs))
    t_out["rho_M0_foreign"] = float((Rm.sum() - np.trace(Rm)) / (len(vs) * (len(vs) - 1)))
    t_out["p_primary"] = perm_p(Rm, rng)
    # Nachtrag d (descriptive, N28): identify each run's split among the case's candidates by the highest rho (chance 1/n)
    t_out["ident_top1"] = float(np.mean(np.argmax(Rm, axis=1) == np.arange(len(vs))))
    t_out["ident_rank_mean"] = float(np.mean([1 + int((Rm[i] > Rm[i, i]).sum()) for i in range(len(vs))]))
    t_out["ident_chance_top1"] = 1.0 / len(vs)
    for k in PREDICTORS + (("E0",) if all("rho_E0" in r for r in valid) else ()):
        t_out[f"rho_{k}_mean"] = float(np.mean([r[f"rho_{k}"] for r in valid]))
        t_out[f"rbar_{k}_mean"] = float(np.mean([r[f"rbar_{k}"] for r in valid]))
    t_out["rho_M0_at_mean"] = {t: float(np.mean([r["rho_M0_at"][t] for r in valid])) for t in extra}
    return t_out, valid


def analyze() -> None:
    pred = json.loads(PRED.read_text(encoding="utf-8"))["cases"]
    rng = np.random.default_rng(PERM_SEED)
    out: dict = {"tasks": {}}
    all_rows = []
    for task, p in TASKS:
        out["tasks"][f"{task}{p}"], valid = case_rows(
            f"{task}{p}", SEEDS, pred, lambda idx, t=task, q=p: spectra(idx, t, q),
            lambda s, f, t=task, q=p: run_powers_043(t, q, s, f), EXTRA_STEPS, rng)
        all_rows += valid
    pred59 = json.loads(PRED_D59.read_text(encoding="utf-8"))["cases"]   # Nachtrag a: third case of the family
    out["tasks"]["D59"], valid = case_rows("D59", SEEDS_D59, pred59, spectra_d59, run_powers_d59, EXTRA_D59, rng)
    all_rows += valid
    predi = json.loads(PRED_INT.read_text(encoding="utf-8"))["cases"]   # Nachtrag b: fourth case, non-modular
    out["tasks"]["intadd"], valid = case_rows("intadd", SEEDS_INT, predi, spectra_intadd, run_powers_intadd, (), rng,
                                              off=KLO_INT - 1)
    all_rows += valid
    ps = {t: v.get("p_primary", 1.0) for t, v in out["tasks"].items()}   # review s14: family fixed at four, missing = p 1
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
            d = np.array([r[f"rho_{a}"] - r[f"rho_{b}"] for r in all_rows if f"rho_{b}" in r])   # E0: not for intadd
            sec[name] = {"mean_diff": float(d.mean()), "n_pos": int((d > 0).sum()), "n": len(d), "p_one_sided": sign_flip_p(d, rng)}
        out["secondary"] = sec
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({t: {k: v for k, v in d.items() if k != "rows"} for t, d in out["tasks"].items()}, indent=1))
    print(json.dumps(out.get("secondary"), indent=1))


if __name__ == "__main__":
    arg = sys.argv[1:]
    if arg == ["--predict"]:
        predict()
    elif arg == ["--predict-intadd"]:
        predict_intadd()
    elif arg == ["--predict-d59"]:
        predict_d59()
    elif arg == ["--selftest"]:
        selftest()
    elif arg == []:
        analyze()
    else:
        raise SystemExit(__doc__)
