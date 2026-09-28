"""EXP-087 (pilot, exploration): does the R5 split speed-up run entirely through the early W_E target signal?

Written in session 39 (2026-09-28) before any EXP-087 run. Registration: README.md (this folder), readings fixed there.
Units u = 0..9 (init seed 3200 + u), calibration units 10..12 (seeds 3210-3212, never in the verdict). Every unit has its own
streams SeedSequence([TAG, u, ...]) (none from the init seed): held-out test set (20 % of all pairs), pool = rest, uniform R split,
one target set (5 of k = 1..56) and the EXP-018/R5 construction E2 (eps 2, same helpers as confirm_r5: wave, keyed).
Arms per unit (same init, same test set):  R, RP = R + planted targets, E2, E2P = E2 + planted targets, RN = R + norm-matched noise.
Plant: plant.py, planted power per target = C x median init frequency power (C from the calibration, grid below).
Every run: freq_ban, GPU, --threads 1, 8000 steps, --stop-after-gen 8000, W_E spectrum at 250. Event exactly as R5 (confirm_r5.event).

  python design.py --selftest | --splits | --calib-jobs | --calib-analyze | --jobs C | --analyze C
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

TAG = 20261087
P, N_TRAIN, N_FREQ, M, N_TEST = r5.P, r5.N_TRAIN, r5.N_FREQ, r5.M, r5.N_TEST
CAP = r5.CAP
SEED0, N_UNITS, CALIB_UNITS = 3200, 10, (10, 11, 12)
C_GRID = (0.5, 2.0, 8.0, 32.0)      # = amplitude multiples {0.5, 1, 2, 4} of the median init amplitude (power 2 m^2)
SHARE_GOAL = 0.30                    # mean W_E target share at 250 of E2 in R5 (0.304 / 0.312)
CALIB_STEPS = 250
ARMS = ("R", "RP", "E2", "E2P", "RN")
SPL = HERE / "splits"
RAW = HERE / "raw"
PY = (ROOT / ".venv-gpu/Scripts/python.exe").as_posix()
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
N_BOOT = 20_000


def stream(*key: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([TAG, *key]))


def targets(u: int) -> list[int]:
    return sorted(int(k) for k in stream(u, 1).choice(np.arange(1, N_FREQ + 1), size=M, replace=False))


def build_unit(u: int) -> dict[str, np.ndarray]:
    perm = stream(u, 0).permutation(P * P)
    test, pool = np.sort(perm[:N_TEST]), np.sort(perm[N_TEST:])
    w = r5.wave(targets(u), stream(u, 4))[pool]
    return {"test": test, "R": np.sort(stream(u, 3).choice(pool, size=N_TRAIN, replace=False)),
            "E2": r5.keyed(pool, np.clip(1.0 + 2.0 * w, 0.05, None), stream(u, 2).random(len(pool)))}


def split_path(u: int, name: str) -> Path:
    return SPL / f"u{u}_{name}.npy"


def write_splits() -> None:
    SPL.mkdir(exist_ok=True)
    for u in range(N_UNITS + len(CALIB_UNITS)):
        for name, x in build_unit(u).items():
            f = split_path(u, name)
            if f.exists():
                if not np.array_equal(np.load(f), x):
                    raise SystemExit(f"{f} differs from the deterministic rebuild")
                continue
            with open(f, "xb") as fh:
                np.save(fh, x.astype(np.int64))
    print(f"[exp087] splits ok in {SPL.relative_to(ROOT).as_posix()}")


def job(u: int, arm: str, c: float, steps: int = CAP) -> str:
    base = "E2" if arm.startswith("E2") else "R"
    cmd = (f"{PY} {FB} --seed {SEED0 + u} --condition baseline --threads 1 --device cuda "
           f"--out-root {RAW.relative_to(ROOT).as_posix()} --steps {steps} "
           f"--split-file {split_path(u, base).relative_to(ROOT).as_posix()} "
           f"--test-file {split_path(u, 'test').relative_to(ROOT).as_posix()} --spectra-at 250 --stop-after-gen {steps}")
    if arm in ("RP", "E2P", "RN"):
        cmd += f" --plant-targets {','.join(map(str, targets(u)))} --plant-c {c:g}"
    if arm == "RN":
        cmd += " --plant-noise"
    return cmd


def find_run(u: int, arm: str, c: float, steps: int) -> Path | None:
    """The run dir whose result.json config matches (seed, split, plant); None if absent, error if ambiguous."""
    want = {"plant_targets": targets(u) if arm in ("RP", "E2P", "RN") else None,
            "plant_c": c if arm in ("RP", "E2P", "RN") else None, "plant_noise": arm == "RN"}
    base = "E2" if arm.startswith("E2") else "R"
    hits = []
    for f in RAW.glob(f"*seed{SEED0 + u}_*/result.json"):
        res = json.loads(f.read_text(encoding="utf-8"))       # run-level fields are top-level in result.json (not in "config")
        if (res.get("max_steps") == steps and Path(str(res.get("split_file", ""))).name == split_path(u, base).name
                and all(res.get(k) == v for k, v in want.items())):
            hits.append(f.parent)
    if len(hits) > 1:
        raise SystemExit(f"u{u}:{arm}: {len(hits)} matching runs, ambiguous")
    return hits[0] if hits else None


def share_250(L, tg: list[int]) -> float:
    pw = L.spectrum(250)
    return float(pw[[k - 1 for k in tg]].sum() / pw.sum())


def load(u: int, arm: str, c: float, steps: int):
    d = find_run(u, arm, c, steps)
    if d is None:
        return "fehlt"
    base = "E2" if arm.startswith("E2") else "R"
    L = load_run(d, Expect(seed=SEED0 + u, device="cuda", max_steps=steps, split_file=split_path(u, base),
                           test_file=split_path(u, "test"), config={"p": P, "task": "add", "arch": "transformer"}, at=(250,)))
    return L if L.status == "ok" else f"{L.status}: {L.reason}"


# ---------------------------------------------------------------- calibration
def calib_jobs() -> list[str]:
    return [job(u, "RP", c, CALIB_STEPS) for u in CALIB_UNITS for c in C_GRID]


def choose_c(shares: dict[float, list[float]]) -> float:
    """C whose mean share at 250 is nearest SHARE_GOAL (ties -> smaller C)."""
    return min(sorted(shares), key=lambda c: abs(float(np.mean(shares[c])) - SHARE_GOAL))


def calib_analyze() -> None:
    shares: dict[float, list[float]] = {}
    for c in C_GRID:
        for u in CALIB_UNITS:
            L = load(u, "RP", c, CALIB_STEPS)
            if isinstance(L, str):
                raise SystemExit(f"calibration u{u} C={c:g}: {L} -> not evaluable, no pilot")
            shares.setdefault(c, []).append(share_250(L, targets(u)))
    c = choose_c(shares)
    out = {"shares": {f"{k:g}": v for k, v in shares.items()}, "goal": SHARE_GOAL, "chosen_c": c}
    (HERE / "calibration.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


# ---------------------------------------------------------------- pilot analysis
def lb(t: tuple[int, bool]) -> float:
    return math.log2(min(t[0], CAP))


def boot_ci(x: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    m = rng.choice(x, size=(N_BOOT, len(x)), replace=True).mean(axis=1)
    return float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))


def p_sign(x: np.ndarray) -> float:
    """one-sided exact sign test for median > 0 (zeros dropped)"""
    k, n = int((x > 0).sum()), int((x != 0).sum())
    return float(sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n) if n else 1.0


def reading(ci_plant: tuple[float, float], ci_med: tuple[float, float], rp_observed: int, rn_ok: bool, r_observed: int = 10) -> str:
    """README 'Lesart vorab' + Nachtrag b (both fixed before any pilot result was read). RP censored in > 2 units -> L_med biased
    toward 0: M-med not claimable; R censored in > 2 units -> L_plant biased toward 0: M-marker not claimable (Nachtrag b);
    more than one reading met -> unklar (Nachtrag b: no order among readings)."""
    if not rn_ok:
        return "nicht auswertbar (Normkontrolle RN schneller als R)"
    met = []
    if ci_plant[1] < 0.5:
        met.append("M-marker" if r_observed >= 8 else "unklar (R zu oft zensiert für M-marker)")
    if ci_plant[0] > 1 and -0.5 <= ci_med[0] and ci_med[1] <= 0.5:
        met.append("M-med" if rp_observed >= 8 else "unklar (RP zu oft zensiert für M-med)")
    if ci_plant[0] > 0 and ci_med[0] > 0.5:
        met.append("M-data")
    if len(met) > 1:
        return "unklar (mehrere Lesarten erfüllt: " + ", ".join(met) + ")"
    if not met:
        return "unklar"
    return met[0] if met[0].startswith("unklar") else met[0] + " gestützt"


def summarize(rows: list[dict], rng: np.random.Generator) -> dict:
    lr = np.array([r["logb"]["R"] for r in rows])
    lrp = np.array([r["logb"]["RP"] for r in rows])
    le2 = np.array([r["logb"]["E2"] for r in rows])
    le2p = np.array([r["logb"]["E2P"] for r in rows])
    lrn = np.array([r["logb"]["RN"] for r in rows])
    L = {"L_plant": lr - lrp, "L_med": lrp - le2, "L_E": le2 - le2p, "L_noise": lr - lrn}
    stats = {k: {"mean": float(v.mean()), "ci95": boot_ci(v, rng), "p_sign_gt0": p_sign(v), "values": v.tolist()} for k, v in L.items()}
    rp_obs = sum(r["observed"]["RP"] for r in rows)
    observed = {a: sum(r["observed"][a] for r in rows) for a in ARMS}
    rn_ok = stats["L_noise"]["ci95"][0] <= 0 or stats["L_noise"]["mean"] <= 0.5   # RN not clearly faster than R
    return {"n_units": len(rows), "stats": stats, "rp_observed": rp_obs, "observed_per_arm": observed,
            "reading": reading(tuple(stats["L_plant"]["ci95"]), tuple(stats["L_med"]["ci95"]), rp_obs, rn_ok, observed["R"])}


def analyze(c: float) -> None:
    rows, bad = [], []
    for u in range(N_UNITS):
        runs = {a: load(u, a, c, CAP) for a in ARMS}
        errs = [f"u{u}:{a}: {v}" for a, v in runs.items() if isinstance(v, str)]
        if errs:
            bad += errs
            continue
        viol = [f"u{u}:{a}: {w}" for a, L in runs.items() if (w := r5.dense_violation(L.res.get("dense")))]
        cks = {L.res.get("init_checksum_shared") for L in runs.values()}
        if viol or len(cks) != 1:
            bad += viol or [f"u{u}: init checksums differ"]
            continue
        ev = {a: r5.event(L.res["dense"], int(L.res["steps_completed"])) for a, L in runs.items()}
        rows.append({"unit": u, "logb": {a: lb(t) for a, t in ev.items()}, "observed": {a: t[1] for a, t in ev.items()},
                     "times": {a: list(t) for a, t in ev.items()},
                     "share_250": {a: share_250(L, targets(u)) for a, L in runs.items()},
                     # Nachtrag b (registered secondary): final top-5 W_E frequencies of each arm vs the planted/steered targets
                     "final_top5_on_targets": {a: len(set(L.res.get("final_top_m_freqs") or []) & set(targets(u)))
                                               for a, L in runs.items()}})
    out = {"c": c, "technical_failures": bad, "rows": rows}
    if bad:
        out["reading"] = "nicht auswertbar (technische Ausfälle)"
    else:
        out.update(summarize(rows, np.random.default_rng([TAG, 99])))
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


# ---------------------------------------------------------------- selftest
def selftest() -> None:
    b0, b1 = build_unit(0), build_unit(0)
    assert all(np.array_equal(b0[k], b1[k]) for k in b0), "unit build not deterministic"
    assert len(b0["R"]) == len(b0["E2"]) == N_TRAIN and len(b0["test"]) == N_TEST
    assert not np.intersect1d(b0["R"], b0["test"]).size and not np.intersect1d(b0["E2"], b0["test"]).size
    assert len(np.unique(b0["E2"])) == N_TRAIN
    assert targets(0) != targets(1) and len(set(targets(0))) == M
    assert not np.array_equal(build_unit(1)["test"], b0["test"])
    import confirm_splits as cs
    tg = targets(0)
    sh = {k: float(cs.m0(b0[k], "add", P)[[t - 1 for t in tg]].sum() / cs.m0(b0[k], "add", P).sum()) for k in ("R", "E2")}
    assert sh["E2"] > 2 * sh["R"], f"E2 not concentrated on the targets: {sh}"
    assert choose_c({0.5: [0.1], 2.0: [0.25], 8.0: [0.4], 32.0: [0.8]}) == 2.0
    assert choose_c({0.5: [0.2], 2.0: [0.4]}) == 0.5          # tie -> smaller C
    js = [job(0, a, 2.0) for a in ARMS]
    assert "--plant" not in js[0] and "--plant-noise" in js[4] and "--plant-noise" not in js[1] and "u0_E2.npy" in js[3]
    assert len(set(js)) == len(ARMS) and all("\\" not in j for j in js)
    rng = np.random.default_rng(0)

    def fake(plant: float, med: float, noise: float = 0.0, cens_rp: int = 0) -> list[dict]:
        rows = []
        for u in range(10):
            r = 12.5 + rng.normal(0, 0.2)
            rp, e2 = r - plant + rng.normal(0, 0.1), r - plant - med + rng.normal(0, 0.1)
            rows.append({"logb": {"R": r, "RP": rp, "E2": e2, "E2P": e2, "RN": r - noise},
                         "observed": {"R": True, "RP": u >= cens_rp, "E2": True, "E2P": True, "RN": True}})
        return rows
    g = np.random.default_rng(1)
    assert summarize(fake(2.5, 0.0), g)["reading"] == "M-med gestützt"
    assert summarize(fake(1.0, 1.5), g)["reading"] == "M-data gestützt"
    assert summarize(fake(0.0, 2.5), g)["reading"] == "M-marker gestützt"
    assert summarize(fake(2.5, 0.0, cens_rp=3), g)["reading"].startswith("unklar")
    assert summarize(fake(2.5, 0.0, noise=2.5), g)["reading"].startswith("nicht auswertbar")
    assert reading((0.1, 0.4), (0.6, 1.0), 10, True).startswith("unklar (mehrere")      # Nachtrag b: marker + data both met
    assert reading((-0.2, 0.3), (0.0, 0.2), 10, True, r_observed=7).startswith("unklar (R zu oft")
    assert reading((-0.2, 0.3), (0.0, 0.2), 10, True, r_observed=8) == "M-marker gestützt"
    print("[exp087] selftest ok")


if __name__ == "__main__":
    arg = sys.argv[1:]
    if arg == ["--selftest"]:
        selftest()
    elif arg == ["--splits"]:
        write_splits()
    elif arg == ["--calib-jobs"]:
        print("\n".join(calib_jobs()))
    elif arg == ["--calib-analyze"]:
        calib_analyze()
    elif len(arg) == 2 and arg[0] == "--jobs":
        print("\n".join(job(u, a, float(arg[1])) for u in range(N_UNITS) for a in ARMS))
    elif len(arg) == 2 and arg[0] == "--analyze":
        analyze(float(arg[1]))
    else:
        raise SystemExit(__doc__)
