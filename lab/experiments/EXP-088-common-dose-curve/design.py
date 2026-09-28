"""EXP-088: do data-steered and planted early W_E target signal lie on ONE dose curve "target share at 250 -> grokking time"?

Written in session 39 (2026-09-28) after the EXP-087 pilot (seen: README "Bereits gesehene Daten"), before any EXP-088 run.
Registration: README.md (this folder). Units u = 0..19 (init seed 3230 + u), own streams SeedSequence([TAG, u, ...]).
Per unit (same init, same held-out test set, same five targets, same keys and wave phases for all engineered arms):
  data arms   E2, E4, E8   EXP-018/R5 construction with eps 2, 4, 8
  plant arms  P1, P2, P4   uniform random split R + planted target power C x median init power, C = 1, 2, 4 (plant.py)
  reference   R            uniform random split (descriptive only)
Every run: freq_ban, GPU, --threads 1, 8000 steps, --stop-after-gen 8000, W_E spectrum at 250. Event exactly as R5 (confirm_r5.event).
Primary (fixed in the README): data curve log2 b = a_u + beta * s fitted by least squares on the data arms (unit intercepts,
common slope); residual of a plant arm = log2 b - (a_u + beta * s); unit statistic r_u = mean residual of its eligible plant arms
(share within the unit's data-share range +- 0.03); 90 % unit-bootstrap CI of mean r_u (refit per resample) inside [-0.5, 0.5] ->
"gemeinsame Kurve"; 95 % CI lower bound > 0.5 -> "Eingriff langsamer als sein Anteil"; 95 % CI upper bound < -0.5 ->
"Eingriff schneller als sein Anteil"; otherwise "unklar". Fewer than 15 eligible units -> "nicht auswertbar".

  python design.py --selftest | --splits | --jobs | --analyze
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "tools"))
import confirm_r5 as r5  # noqa: E402  (read-only reuse: wave, keyed, event, dense_violation, constants)
from result_loader import Expect, load_run  # noqa: E402

TAG = 20261088
P, N_TRAIN, N_FREQ, M, N_TEST, CAP = r5.P, r5.N_TRAIN, r5.N_FREQ, r5.M, r5.N_TEST, r5.CAP
SEED0, N_UNITS = 3230, 20
DATA_EPS = {"E2": 2.0, "E4": 4.0, "E8": 8.0}
PLANT_C = {"P1": 1.0, "P2": 2.0, "P4": 4.0}
ARMS = ("R",) + tuple(DATA_EPS) + tuple(PLANT_C)
MARGIN, RANGE_PAD, MIN_UNITS, N_BOOT = 0.5, 0.03, 15, 20_000
SPL, RAW = HERE / "splits", HERE / "raw"
PY = (ROOT / ".venv-gpu/Scripts/python.exe").as_posix()
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"


def stream(*key: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([TAG, *key]))


def targets(u: int) -> list[int]:
    return sorted(int(k) for k in stream(u, 1).choice(np.arange(1, N_FREQ + 1), size=M, replace=False))


def build_unit(u: int) -> dict[str, np.ndarray]:
    perm = stream(u, 0).permutation(P * P)
    test, pool = np.sort(perm[:N_TEST]), np.sort(perm[N_TEST:])
    w = r5.wave(targets(u), stream(u, 4))[pool]
    keys = stream(u, 2).random(len(pool))
    sets = {"test": test, "R": np.sort(stream(u, 3).choice(pool, size=N_TRAIN, replace=False))}
    for arm, eps in DATA_EPS.items():
        sets[arm] = r5.keyed(pool, np.clip(1.0 + eps * w, 0.05, None), keys)
    return sets


def split_name(arm: str) -> str:
    return "R" if arm in PLANT_C else arm


def split_path(u: int, name: str) -> Path:
    return SPL / f"u{u}_{name}.npy"


def write_splits() -> None:
    SPL.mkdir(exist_ok=True)
    for u in range(N_UNITS):
        for name, x in build_unit(u).items():
            f = split_path(u, name)
            if f.exists():
                if not np.array_equal(np.load(f), x):
                    raise SystemExit(f"{f} differs from the deterministic rebuild")
                continue
            with open(f, "xb") as fh:
                np.save(fh, x.astype(np.int64))
    print(f"[exp088] splits ok in {SPL.relative_to(ROOT).as_posix()}")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def job(u: int, arm: str) -> str:
    cmd = (f"{PY} {FB} --seed {SEED0 + u} --condition baseline --threads 1 --device cuda --out-root {rel(RAW)} --steps {CAP} "
           f"--split-file {rel(split_path(u, split_name(arm)))} --test-file {rel(split_path(u, 'test'))} "
           f"--spectra-at 250 --stop-after-gen {CAP}")
    if arm in PLANT_C:
        cmd += f" --plant-targets {','.join(map(str, targets(u)))} --plant-c {PLANT_C[arm]:g}"
    return cmd


def jobs() -> list[str]:
    """seeded random run order (execution order only; cannot change a result)"""
    js = [job(u, a) for u in range(N_UNITS) for a in ARMS]
    return [js[i] for i in stream(99).permutation(len(js))]


def find_run(u: int, arm: str) -> Path | None:
    want = {"plant_targets": targets(u) if arm in PLANT_C else None, "plant_c": PLANT_C.get(arm), "plant_noise": False}
    hits = []
    for f in RAW.glob(f"*seed{SEED0 + u}_*/result.json"):
        res = json.loads(f.read_text(encoding="utf-8"))     # run-level fields are top-level in result.json
        if (res.get("max_steps") == CAP and Path(str(res.get("split_file", ""))).name == split_path(u, split_name(arm)).name
                and all(res.get(k) == v for k, v in want.items())):
            hits.append(f.parent)
    if len(hits) > 1:
        raise SystemExit(f"u{u}:{arm}: {len(hits)} matching runs, ambiguous")
    return hits[0] if hits else None


def load(u: int, arm: str):
    d = find_run(u, arm)
    if d is None:
        return "fehlt"
    L = load_run(d, Expect(seed=SEED0 + u, device="cuda", max_steps=CAP, split_file=split_path(u, split_name(arm)),
                           test_file=split_path(u, "test"), config={"p": P, "task": "add", "arch": "transformer"}, at=(250,)))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    if (why := r5.dense_violation(L.res.get("dense"))):
        return f"defekt: {why}"
    return L


def share_250(L, tg: list[int]) -> float:
    pw = L.spectrum(250)
    return float(pw[[k - 1 for k in tg]].sum() / pw.sum())


# ---------------------------------------------------------------- analysis (pure functions, tested in the selftest)
def fit_curve(units: list[dict]) -> tuple[float, dict[int, float]]:
    """least squares log2 b = a_u + beta * s on the data arms: common slope beta (within-unit), unit intercepts a_u"""
    xs, ys = [], []
    for un in units:
        s = np.array([un["s"][a] for a in DATA_EPS])
        y = np.array([un["y"][a] for a in DATA_EPS])
        xs.append(s - s.mean())
        ys.append(y - y.mean())
    x, y = np.concatenate(xs), np.concatenate(ys)
    beta = float((x * y).sum() / (x * x).sum())
    a = {un["unit"]: float(np.mean([un["y"][k] - beta * un["s"][k] for k in DATA_EPS])) for un in units}
    return beta, a


def eligible(un: dict, arm: str) -> bool:
    ds = [un["s"][a] for a in DATA_EPS]
    return min(ds) - RANGE_PAD <= un["s"][arm] <= max(ds) + RANGE_PAD


def unit_residuals(units: list[dict]) -> tuple[np.ndarray, float]:
    beta, a = fit_curve(units)
    r = []
    for un in units:
        arms = [k for k in PLANT_C if eligible(un, k)]
        r.append(np.mean([un["y"][k] - (a[un["unit"]] + beta * un["s"][k]) for k in arms]) if arms else np.nan)
    return np.array(r), beta


def reading(ci90: tuple[float, float], ci95: tuple[float, float], n_eligible: int) -> str:
    if n_eligible < MIN_UNITS:
        return "nicht auswertbar (zu wenige Einheiten mit Eingriffsarmen im Datenbereich)"
    if -MARGIN <= ci90[0] and ci90[1] <= MARGIN:
        return "gemeinsame Kurve"
    if ci95[0] > MARGIN:
        return "Eingriff langsamer als sein Anteil"
    if ci95[1] < -MARGIN:
        return "Eingriff schneller als sein Anteil"
    return "unklar"


def verdict(units: list[dict], rng: np.random.Generator) -> dict:
    r, beta = unit_residuals(units)
    keep = [un for un, v in zip(units, r) if np.isfinite(v)]
    n = len(keep)
    if n < MIN_UNITS:
        return {"n_eligible": n, "beta": beta, "reading": reading((0, 0), (0, 0), n)}
    r = r[np.isfinite(r)]
    boot = []
    for _ in range(N_BOOT):
        idx = rng.integers(0, n, n)
        sample = [dict(keep[i], unit=j) for j, i in enumerate(idx)]     # relabel so duplicated units keep own intercepts
        rb, _ = unit_residuals(sample)
        boot.append(np.nanmean(rb))
    boot = np.array(boot)
    ci90 = (float(np.quantile(boot, 0.05)), float(np.quantile(boot, 0.95)))
    ci95 = (float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975)))
    return {"n_eligible": n, "beta": beta, "mean_residual": float(r.mean()), "ci90": ci90, "ci95": ci95,
            "n_positive": int((r > 0).sum()), "residuals": r.tolist(), "reading": reading(ci90, ci95, n)}


def analyze() -> None:
    units, bad, censored = [], [], []
    for u in range(N_UNITS):
        runs = {a: load(u, a) for a in ARMS}
        errs = [f"u{u}:{a}: {v}" for a, v in runs.items() if isinstance(v, str)]
        if errs:
            bad += errs
            continue
        if len({L.res.get("init_checksum_shared") for L in runs.values()}) != 1:
            bad.append(f"u{u}: init checksums differ")
            continue
        ev = {a: r5.event(L.res["dense"], int(L.res["steps_completed"])) for a, L in runs.items()}
        tg = targets(u)
        un = {"unit": u, "s": {a: share_250(L, tg) for a, L in runs.items()}, "y": {a: math.log2(min(t[0], CAP)) for a, t in ev.items()},
              "observed": {a: t[1] for a, t in ev.items()},
              "final_top5_on_targets": {a: len(set(L.res.get("final_top_m_freqs") or []) & set(tg)) for a, L in runs.items()}}
        if not all(un["observed"][a] for a in tuple(DATA_EPS) + tuple(PLANT_C)):
            censored.append(u)          # README: a censored data or plant arm removes the unit from the primary fit
            continue
        units.append(un)
    out = {"technical_failures": bad, "censored_units": censored, "units": units}
    if bad:
        out["reading"] = "nicht auswertbar (technische Ausfälle)"
    else:
        out.update(verdict(units, np.random.default_rng([TAG, 7])))
        out["descriptive"] = {a: {"share_250": float(np.mean([un["s"][a] for un in units])),
                                  "gm_time": float(2 ** np.mean([un["y"][a] for un in units]))} for a in ARMS} if units else {}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k not in ("units", "residuals")}, indent=1))


# ---------------------------------------------------------------- selftest
def _fake(rng: np.random.Generator, offset: float, n: int = 20, beta: float = -12.0) -> list[dict]:
    units = []
    for u in range(n):
        a_u = 13.5 + rng.normal(0, 0.3)
        s = {"E2": 0.31, "E4": 0.40, "E8": 0.49, "P1": 0.30, "P2": 0.40, "P4": 0.50}
        s = {k: v + rng.normal(0, 0.02) for k, v in s.items()}
        y = {k: a_u + beta * v + rng.normal(0, 0.2) + (offset if k in PLANT_C else 0.0) for k, v in s.items()}
        units.append({"unit": u, "s": s, "y": y})
    return units


def selftest() -> None:
    b0 = build_unit(0)
    assert all(np.array_equal(b0[k], build_unit(0)[k]) for k in b0), "not deterministic"
    assert all(len(b0[k]) == N_TRAIN for k in ("R",) + tuple(DATA_EPS)) and len(b0["test"]) == N_TEST
    assert all(not np.intersect1d(b0[k], b0["test"]).size for k in ("R",) + tuple(DATA_EPS))
    import confirm_splits as cs
    tg = targets(0)
    sh = {k: float(cs.m0(b0[k], "add", P)[[t - 1 for t in tg]].sum() / cs.m0(b0[k], "add", P).sum()) for k in ("R", "E2", "E4", "E8")}
    assert sh["R"] < sh["E2"] < sh["E4"] < sh["E8"], f"dose order of the mask target share violated: {sh}"
    js = jobs()
    assert len(js) == N_UNITS * len(ARMS) and len(set(js)) == len(js) and all("\\" not in j for j in js)
    assert "--plant-c 4" in job(3, "P4") and "u3_R.npy" in job(3, "P4") and "--plant" not in job(3, "E8")
    g = np.random.default_rng(1)
    bt, _ = fit_curve(_fake(g, 0.0))
    assert abs(bt + 12.0) < 1.5, f"slope not recovered: {bt}"
    global N_BOOT
    keep, N_BOOT = N_BOOT, 400
    try:
        assert verdict(_fake(g, 0.0), g)["reading"] == "gemeinsame Kurve"
        assert verdict(_fake(g, 1.2), g)["reading"] == "Eingriff langsamer als sein Anteil"
        assert verdict(_fake(g, -1.2), g)["reading"] == "Eingriff schneller als sein Anteil"
        assert verdict(_fake(g, 0.5), g)["reading"] == "unklar"
        far = _fake(g, 0.0)
        for un in far[:6]:
            for k in PLANT_C:
                un["s"][k] = 0.9                               # all plant arms outside the data range -> unit not eligible
        assert verdict(far, g)["reading"].startswith("nicht auswertbar")
    finally:
        N_BOOT = keep
    print("[exp088] selftest ok")


if __name__ == "__main__":
    arg = sys.argv[1:]
    if arg == ["--selftest"]:
        selftest()
    elif arg == ["--splits"]:
        write_splits()
    elif arg == ["--jobs"]:
        print("\n".join(jobs()))
    elif arg == ["--analyze"]:
        analyze()
    else:
        raise SystemExit(__doc__)
