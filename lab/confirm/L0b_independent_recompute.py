"""Independent re-computation of the frozen confirmation block L0b, built only from
L0b_REGISTRATION.md, L0b_manifest.json, the split files in l0b_splits/ and the raw runs in l0b_raw/
(confirm_l0b.py, confirm_p1.py, result_loader.py and EXP-043 analyze.py deliberately NOT read).

Power definition (checked only numerically against the EXP-106 pilot summary, seed 3700: o for all
six runs and Delta_pow for both arms agree to ~1e-16): rows 0..112 of W_E, DFT over the token index,
|F_k|^2 summed over the embedding dimension, frequency k = 1..56 combines k and p-k; DC excluded.

--selftest: synthetic checks in a temp dir only. --analyze: reads all 420 runs, prints and writes
L0b_independent_summary.json. Bootstrap uses its own RNG seed, so CIs agree with the official ones
only approximately; per-seed x values, t and p must agree exactly."""
from __future__ import annotations

import argparse, hashlib, json, math, sys, tempfile
from pathlib import Path
from typing import Callable, Optional

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CONF = ROOT / "lab/confirm"
MANIFEST, SPLITS, RAW = CONF / "L0b_manifest.json", CONF / "l0b_splits", CONF / "l0b_raw"
OFFICIAL, OUT = CONF / "L0b_summary.json", CONF / "L0b_independent_summary.json"
P, NFREQ, BUDGET, MID = 113, 56, 30000, 10000
O_SET = (11, 12, 22, 23, 34, 45)
ARMS = {"iid16w": ("iid", ""), "stride16w": ("stride", "_ordstride")}  # order, dir-name suffix
SPLIT_NAMES = ("F", "G", "R")
DELTA, H3_MARGIN, ALPHA, N_BOOT, SEED_BOOT = 0.02, 2.0, 0.05, 10_000, 30_09_2063
HS = ("H1", "H2", "H3", "H4")


class Unusable(Exception):
    """Any technical violation that makes the whole block 'nicht auswertbar'."""


# ----------------------------------------------------------------------------- spectra
def group_power(we: np.ndarray) -> np.ndarray:
    """Power per frequency k = 1..56 (index k-1) of the first 113 embedding rows."""
    w = np.asarray(we, dtype=np.float64)
    if w.ndim != 2 or w.shape[0] < P:
        raise Unusable(f"W_E snapshot shape {w.shape}")
    pw = (np.abs(np.fft.fft(w[:P], axis=0)) ** 2).sum(axis=1)
    out = np.array([pw[k] + pw[P - k] for k in range(1, NFREQ + 1)])
    if not np.all(np.isfinite(out)) or out.sum() <= 0:
        raise Unusable("power not finite / zero")
    return out


def share(pw: np.ndarray, freqs: tuple | list) -> float:
    return float(pw[[k - 1 for k in freqs]].sum() / pw.sum())


def mass(pw: np.ndarray, freqs: tuple | list) -> float:
    return float(pw[[k - 1 for k in freqs]].sum())


def delta_pow(pw_f: np.ndarray, pw_g: np.ndarray, tf: list, tg: list) -> float:
    d = math.log(mass(pw_f, tf) / mass(pw_f, tg)) + math.log(mass(pw_g, tg) / mass(pw_g, tf))
    if not math.isfinite(d):
        raise Unusable("Delta_pow not finite")
    return d


# ----------------------------------------------------------------------------- statistics
def betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the regularized incomplete beta (modified Lentz)."""
    tiny, qab, qap, qam = 1e-300, a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 10_000):
        m2 = 2 * m
        for aa in (m * (b - m) * x / ((qam + m2) * (a + m2)),
                   -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))):
            d = 1.0 + aa * d
            d = 1.0 / (d if abs(d) > tiny else tiny)
            c = 1.0 + aa / c
            c = c if abs(c) > tiny else tiny
            h *= d * c
        if abs(d * c - 1.0) < 1e-15:
            return h
    raise RuntimeError("betacf did not converge")


def betainc(a: float, b: float, x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbt) * betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * betacf(b, a, 1.0 - x) / b


def t_sf(t: float, df: float) -> float:
    """P(T_df >= t)."""
    if math.isinf(t):
        return 0.0 if t > 0 else 1.0
    half = 0.5 * betainc(df / 2.0, 0.5, df / (df + t * t))
    return half if t > 0 else 1.0 - half


def t_greater(x: np.ndarray, mu0: float) -> tuple[float, float]:
    """One-sample one-sided t test of mean > mu0 -> (t, p)."""
    n, m, sd = len(x), float(np.mean(x)), float(np.std(x, ddof=1))
    if sd == 0.0:
        t = math.inf if m > mu0 else (-math.inf if m < mu0 else 0.0)
        return t, (0.0 if m > mu0 else 1.0)
    t = (m - mu0) / (sd / math.sqrt(n))
    return t, t_sf(t, n - 1)


def tost(x: np.ndarray, delta: float) -> dict:
    t_lo, p_lo = t_greater(x, -delta)          # mean > -delta
    t_hi, p_hi = t_greater(-np.asarray(x), -delta)  # mean < +delta  <=>  -mean > -delta
    return {"t_lower": t_lo, "p_lower": p_lo, "t_upper": -t_hi, "p_upper": p_hi, "p": max(p_lo, p_hi)}


def holm_adjusted(ps: dict[str, float]) -> dict[str, float]:
    order, out, run = sorted(ps, key=lambda k: ps[k]), {}, 0.0
    for i, k in enumerate(order):
        run = max(run, min(1.0, (len(order) - i) * ps[k]))
        out[k] = run
    return out


def boot_ci(x: np.ndarray, rng: np.random.Generator) -> list[float]:
    idx = rng.integers(0, len(x), size=(N_BOOT, len(x)))
    return [float(v) for v in np.percentile(x[idx].mean(axis=1), [2.5, 97.5])]


def ci_ok(h: str, ci: list[float]) -> bool:
    lo, hi = ci
    return {"H1": lo > 0, "H2": -DELTA < lo and hi < DELTA, "H3": lo > -H3_MARGIN, "H4": lo > 0}[h]


def family(xs: dict[str, np.ndarray]) -> dict:
    tests = {"H1": dict(zip(("t", "p"), t_greater(xs["H1"], 0.0))), "H2": tost(xs["H2"], DELTA),
             "H3": dict(zip(("t", "p"), t_greater(xs["H3"], -H3_MARGIN))),
             "H4": dict(zip(("t", "p"), t_greater(xs["H4"], 0.0)))}
    adj = holm_adjusted({h: tests[h]["p"] for h in HS})
    rng, res = np.random.default_rng(SEED_BOOT), {}
    for h in HS:
        ci = boot_ci(xs[h], rng)
        ok = adj[h] < ALPHA and ci_ok(h, ci)
        res[h] = {"n": len(xs[h]), "mean": float(np.mean(xs[h])), "sd": float(np.std(xs[h], ddof=1)),
                  **tests[h], "p_holm": adj[h], "ci95": ci, "ci_rule": ci_ok(h, ci),
                  "verdict": "bestätigt" if ok else "nicht bestätigt"}
    return res


# ----------------------------------------------------------------------------- runs
def t_gen(res: dict) -> tuple[int, bool]:
    """(bounded time, observed). Never generalised -> censored at the budget."""
    s = res["transitions"]["primary"]["generalization"]["first_crossing_step"]
    if s is None:
        return BUDGET, False
    if type(s) is not int or not 0 < s <= BUDGET:
        raise Unusable(f"bad first_crossing_step {s!r}")
    return s, True


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_dir(raw: Path, seed: int, split: str, arm: str) -> Path:
    return raw / f"EXP-018_baseline_seed{seed}_thr1_l0b_seed{seed}_{split}_bs16{ARMS[arm][1]}_wd0.1_devcuda"


def load_run(d: Path, seed: int, split: str, arm: str, splits: Path) -> Optional[dict]:
    """None = missing / not finished; Unusable = technical fault; else per-run measures."""
    rj = d / "result.json"
    if not rj.is_file():
        return None
    r = json.loads(rj.read_text(encoding="utf-8"))
    if r.get("status") != "completed":
        return None
    cfg, fp, mb = r.get("config") or {}, r.get("fingerprint_fields") or {}, (r.get("events") or {}).get("minibatch") or {}
    order = ARMS[arm][0]
    checks = {
        "seed": r.get("seed") == cfg.get("seed") == seed, "condition": r.get("condition") == "baseline",
        "task": (cfg.get("task"), cfg.get("p")) == ("add", P), "device": r.get("device") == "cuda",
        "split file": Path(str(r.get("split_file"))).name == f"l0b_seed{seed}_{split}.npy",
        "split hash": fp.get("split_file_sha256") == sha(splits / f"l0b_seed{seed}_{split}.npy"),
        "test hash": fp.get("test_file_sha256") == sha(splits / f"l0b_seed{seed}_test.npy"),
        "batch": r.get("batch_size") == 16 == mb.get("batch_size"),
        "order": r.get("order") == order == mb.get("order"),
        "optimizer": r.get("optimizer") == "adamw" and (cfg.get("lr"), cfg.get("beta1"), cfg.get("beta2"))
        == (0.001, 0.9, 0.98),
        "wd": cfg.get("weight_decay") == 0.1, "threads": cfg.get("threads") == 1,
        "budget": r.get("steps_completed") == BUDGET == cfg.get("steps") == r.get("max_steps"),
        "stop_after_gen": r.get("stop_after_generalization") == BUDGET,
        "no ban": r.get("banned_freqs") is None and r.get("ban_from_step") is None,
    }
    if not all(checks.values()):
        raise Unusable(f"{d.name}: failed {[k for k, ok in checks.items() if not ok]}")
    we, steps = np.load(d / "we_snapshots.npy"), np.load(d / "we_snapshot_steps.npy").tolist()
    if we.ndim != 3 or len(steps) != we.shape[0] or steps[-1] != BUDGET or MID not in steps:
        raise Unusable(f"{d.name}: snapshots {we.shape} steps {steps}")
    pw, pw_mid = group_power(we[-1]), group_power(we[steps.index(MID)])
    tg, obs = t_gen(r)
    return {"pw": pw, "o": share(pw, O_SET), "o_mid": share(pw_mid, O_SET), "t_gen": tg, "gen_observed": obs,
            "peak": int(np.argmax(pw)) + 1, "init": r.get("init_checksum_shared")}


def load_block(splits: Path, raw: Path, seeds: list[int]) -> tuple[dict, list, list]:
    """-> (runs, missing, technical errors). Targets from l0b_seed{s}.json."""
    runs, missing, errors = {}, [], []
    for s in seeds:
        meta = json.loads((splits / f"l0b_seed{s}.json").read_text(encoding="utf-8"))
        tf, tg = meta["targets"]["F"], meta["targets"]["G"]
        if meta.get("seed") != s or set(tf) & set(O_SET) or set(tg) & set(O_SET) or set(tf) & set(tg):
            errors.append(f"seed {s}: target meta")
        for sp in SPLIT_NAMES:
            for arm in ARMS:
                try:
                    r = load_run(run_dir(raw, s, sp, arm), s, sp, arm, splits)
                except (Unusable, OSError, ValueError, KeyError, TypeError) as e:
                    errors.append(f"{s} {sp} {arm}: {type(e).__name__}: {e}")
                    continue
                if r is None:
                    missing.append(f"{s}/{sp}/{arm}")
                else:
                    runs[(s, sp, arm)] = {**r, "targets": {"F": tf, "G": tg}}
    return runs, missing, errors


def seed_x(runs: dict, s: int) -> dict:
    g = lambda sp, arm: runs[(s, sp, arm)]  # noqa: E731
    tf, tg = g("F", "iid16w")["targets"]["F"], g("F", "iid16w")["targets"]["G"]
    dp = {a: delta_pow(g("F", a)["pw"], g("G", a)["pw"], tf, tg) for a in ARMS}
    lt = [math.log2(g(sp, "stride16w")["t_gen"] / g(sp, "iid16w")["t_gen"]) for sp in ("F", "G")]
    return {"seed": s,
            "x_H1": g("R", "stride16w")["o"] - g("R", "iid16w")["o"],
            "x_H2": float(np.mean([g(sp, "stride16w")["o"] - g(sp, "iid16w")["o"] for sp in ("F", "G")])),
            "x_H3": dp["stride16w"] - dp["iid16w"], "x_H4": float(np.mean(lt)),
            "dpow_iid16w": dp["iid16w"], "dpow_stride16w": dp["stride16w"]}


def run_view(k: tuple, r: dict) -> dict:
    tf, tg = r["targets"]["F"], r["targets"]["G"]
    return {"run": "/".join(map(str, k)), "o": r["o"], "o_mid": r["o_mid"], "t_gen": r["t_gen"],
            "gen_observed": r["gen_observed"], "peak_freq": r["peak"], "P_own_targets_F": mass(r["pw"], tf),
            "P_targets_G": mass(r["pw"], tg), "log_P_F_over_P_G": math.log(mass(r["pw"], tf) / mass(r["pw"], tg))}


def compare_official(rows: list[dict]) -> Optional[dict]:
    if not OFFICIAL.is_file():
        return None
    off = json.loads(OFFICIAL.read_text(encoding="utf-8"))
    found: list[dict] = []

    def walk(o: object) -> None:
        if isinstance(o, dict):
            if "seed" in o and "x_H1" in o:
                found.append(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(off)
    by = {r["seed"]: r for r in found}
    diff = {}
    for h in HS:
        pairs = [(r[f"x_{h}"], by[r["seed"]].get(f"x_{h}")) for r in rows if r["seed"] in by]
        pairs = [(a, b) for a, b in pairs if isinstance(b, (int, float))]
        diff[f"x_{h}"] = max((abs(a - b) for a, b in pairs), default=None)
    return {"n_matched_seeds": len([r for r in rows if r["seed"] in by]), "max_abs_diff": diff}


def analyze() -> dict:
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if (tuple(man["order_freqs"]), man["delta_equiv"], man["h3_margin"], man["budget"], man["batch_size"],
            man["weight_decay"], man["o_mid_step"]) != (O_SET, DELTA, H3_MARGIN, BUDGET, 16, 0.1, MID):
        return {"block": "nicht auswertbar", "reason": "manifest constants differ from this script"}
    seeds = man["seeds"]
    runs, missing, errors = load_block(SPLITS, RAW, seeds)
    res: dict = {"n_seeds": len(seeds), "runs_expected": 6 * len(seeds), "runs_loaded": len(runs),
                 "missing": len(missing), "missing_list": missing, "technical_errors": errors,
                 "loaded_runs": [run_view(k, v) for k, v in sorted(runs.items())]}
    complete = [s for s in seeds if all((s, sp, a) in runs for sp in SPLIT_NAMES for a in ARMS)]
    partial = sorted({s for s, sp, a in runs})
    for s in partial:  # Delta_pow parts per arm where the F/G pair is complete
        for a in ARMS:
            if (s, "F", a) in runs and (s, "G", a) in runs:
                r = runs[(s, "F", a)]
                res.setdefault("dpow_available", {})[f"{s}/{a}"] = delta_pow(
                    r["pw"], runs[(s, "G", a)]["pw"], r["targets"]["F"], r["targets"]["G"])
    rows = [seed_x(runs, s) for s in complete]
    res["rows"] = rows
    if missing or errors:
        res["block"] = "nicht auswertbar"
        res["reason"] = f"{len(missing)} runs missing, {len(errors)} technical errors"
        res["official_comparison"] = compare_official(rows)
        return res
    inits = {s: {runs[(s, sp, a)]["init"] for sp in SPLIT_NAMES for a in ARMS} for s in seeds}
    res["init_checksum_per_seed_unique"] = all(len(v) == 1 and None not in v for v in inits.values())
    xs = {h: np.array([r[f"x_{h}"] for r in rows]) for h in HS}
    res["block"] = "auswertbar"
    res["family"] = family(xs)
    cens = {f"{sp}/{a}": sum(not runs[(s, sp, a)]["gen_observed"] for s in seeds) for sp in SPLIT_NAMES for a in ARMS}
    res["descriptive"] = {
        "never_generalised": cens,
        "o_mean_end": {f"{sp}/{a}": float(np.mean([runs[(s, sp, a)]["o"] for s in seeds])) for sp in SPLIT_NAMES for a in ARMS},
        "o_mean_step10000": {f"{sp}/{a}": float(np.mean([runs[(s, sp, a)]["o_mid"] for s in seeds])) for sp in SPLIT_NAMES for a in ARMS},
        "peak_in_O_fraction": {f"{sp}/{a}": float(np.mean([runs[(s, sp, a)]["peak"] in O_SET for s in seeds])) for sp in SPLIT_NAMES for a in ARMS},
        "dpow_iid16w_mean": float(np.mean([r["dpow_iid16w"] for r in rows]))}
    res["official_comparison"] = compare_official(rows)
    return res


# ----------------------------------------------------------------------------- selftest
def planted(amps: dict[int, float], rng: np.random.Generator, extra_row: bool = False) -> np.ndarray:
    """W_E with cos/sin waves on orthonormal directions: power_k = p^2 * amp_k^2 exactly."""
    q, _ = np.linalg.qr(rng.normal(size=(128, 128)))
    a = np.arange(P)[:, None]
    w = np.full((P, 128), 0.7)  # DC offset must not count
    for i, (k, amp) in enumerate(amps.items()):
        w += amp * (np.cos(2 * np.pi * k * a / P) * q[:, 2 * i] + np.sin(2 * np.pi * k * a / P) * q[:, 2 * i + 1])
    return np.vstack([w, rng.normal(size=(1, 128)) * 50]) if extra_row else w


def rejected(fn: Callable[[], object]) -> bool:
    try:
        fn()
    except Unusable:
        return True
    return False


def selftest() -> int:
    rng = np.random.default_rng(1)
    base = {k: 0.1 for k in range(1, NFREQ + 1)}
    pw = group_power(planted({**base, 11: 1.0, 34: 2.0, 5: 3.0}, rng, extra_row=True))
    want = np.array([P * P * (base | {11: 1.0, 34: 2.0, 5: 3.0})[k] ** 2 for k in range(1, NFREQ + 1)])
    assert np.allclose(pw, want, rtol=1e-9), "planted power"
    tot = 0.01 * 53 + 1 + 4 + 9
    assert abs(share(pw, O_SET) - (0.01 * 4 + 1 + 4) / tot) < 1e-12
    tf, tg = [5, 13], [1, 8]
    pf = group_power(planted({**base, 5: 2.0, 13: 2.0}, rng))
    pg = group_power(planted({**base, 1: 1.0, 8: 1.0}, rng))
    assert abs(delta_pow(pf, pg, tf, tg) - (math.log(8 / 0.02) + math.log(2 / 0.02))) < 1e-9
    assert rejected(lambda: group_power(np.zeros((50, 8))))
    # t tail: closed forms (df 1, 2) and table quantiles
    for t in (-2.0, 0.3, 1.0, 5.0):
        assert abs(t_sf(t, 1) - (0.5 - math.atan(t) / math.pi)) < 1e-12
        assert abs(t_sf(t, 2) - (0.5 - t / (2 * math.sqrt(t * t + 2)))) < 1e-12
        u = t / math.sqrt(3)
        assert abs(t_sf(t, 3) - (0.5 - (math.atan(u) + u / (1 + u * u)) / math.pi)) < 1e-12
    for t, df, p in ((2.015048, 5, 0.05), (2.228139, 10, 0.025), (2.527977, 20, 0.01),
                     (2.000298, 60, 0.025), (1.959964, 1e7, 0.025), (0.0, 69, 0.5)):
        assert abs(t_sf(t, df) - p) < 2e-6, (t, df, t_sf(t, df))
    # t test / TOST
    x = np.array([0.1, 0.3, 0.2, 0.4])  # mean .25, sd .129099, se .0645497 -> t 3.87298, df 3
    t, p = t_greater(x, 0.0)
    assert abs(t - 3.872983346) < 1e-8 and abs(p - 0.0152331458) < 1e-9 and p < 0.02
    tt = tost(np.array([0.001, -0.002, 0.003, 0.0, -0.001]), DELTA)
    assert tt["p"] == max(tt["p_lower"], tt["p_upper"]) and tt["p"] < 1e-4
    assert tost(np.array([0.03, 0.05, 0.04]), DELTA)["p"] > 0.5  # clearly outside +delta
    assert t_greater(np.full(5, 0.3), 0.0) == (math.inf, 0.0)
    adj = holm_adjusted({"H1": 0.01, "H2": 0.04, "H3": 0.002, "H4": 0.3})
    assert np.allclose([adj[h] for h in HS], [0.03, 0.08, 0.008, 0.3])
    assert ci_ok("H2", [-0.019, 0.019]) and not ci_ok("H2", [-0.021, 0.0]) and ci_ok("H3", [-1.9, 3])
    g = np.random.default_rng(5)
    fam = family({"H1": 0.15 + 0.1 * g.normal(size=70), "H2": 0.003 * g.normal(size=70),
                  "H3": -0.5 + g.normal(size=70), "H4": 0.6 + 0.5 * g.normal(size=70)})
    assert all(fam[h]["verdict"] == "bestätigt" for h in HS), fam
    fam = family({"H1": 0.1 * g.normal(size=70), "H2": 0.05 + 0.003 * g.normal(size=70),
                  "H3": -3 + g.normal(size=70), "H4": 0.6 + 0.5 * g.normal(size=70)})
    assert [fam[h]["verdict"] == "bestätigt" for h in HS] == [False, False, False, True], fam
    # censoring
    rr = lambda s: {"transitions": {"primary": {"generalization": {"first_crossing_step": s}}}}  # noqa: E731
    assert t_gen(rr(None)) == (BUDGET, False) and t_gen(rr(7200)) == (7200, True)
    assert rejected(lambda: t_gen(rr(0))) and rejected(lambda: t_gen(rr(30001)))
    loader_selftest(rng)
    print(json.dumps({"selftest": "ok"}))
    return 0


def loader_selftest(rng: np.random.Generator) -> None:
    """One synthetic seed with six runs: planted spectra -> known x values; faults are caught."""
    s, tf, tg = 9000, [5, 13], [1, 8]
    with tempfile.TemporaryDirectory() as td:
        sp, rw = Path(td) / "s", Path(td) / "r"
        sp.mkdir(); rw.mkdir()
        (sp / f"l0b_seed{s}.json").write_text(json.dumps({"seed": s, "targets": {"F": tf, "G": tg}}))
        for i, name in enumerate(("F", "G", "R", "test")):
            np.save(sp / f"l0b_seed{s}_{name}.npy", np.arange(7) + 100 * i)
        base = {k: 0.1 for k in range(1, NFREQ + 1)}
        amps = {("F", "iid16w"): {5: 2.0}, ("F", "stride16w"): {5: 2.0, 11: 0.5},
                ("G", "iid16w"): {1: 1.0}, ("G", "stride16w"): {1: 1.0},
                ("R", "iid16w"): {}, ("R", "stride16w"): {12: 1.0}}
        tgen = {("F", "iid16w"): 4000, ("F", "stride16w"): 8000, ("G", "iid16w"): 7500, ("G", "stride16w"): None,
                ("R", "iid16w"): 5000, ("R", "stride16w"): 5000}

        def write(bad: tuple = (), field: str = "", val: object = None) -> None:
            for (spn, arm), a in amps.items():
                d = run_dir(rw, s, spn, arm)
                d.mkdir(exist_ok=True)
                w = planted({**base, **a}, rng)
                np.save(d / "we_snapshots.npy", np.stack([w * 0.5, w]))
                np.save(d / "we_snapshot_steps.npy", np.array([MID, BUDGET]))
                r = {"status": "completed", "seed": s, "condition": "baseline", "device": "cuda",
                     "split_file": f"x/l0b_seed{s}_{spn}.npy", "batch_size": 16, "order": ARMS[arm][0],
                     "optimizer": "adamw", "steps_completed": BUDGET, "max_steps": BUDGET,
                     "stop_after_generalization": BUDGET, "banned_freqs": None, "ban_from_step": None,
                     "init_checksum_shared": "c",
                     "config": {"seed": s, "task": "add", "p": P, "lr": 0.001, "beta1": 0.9, "beta2": 0.98,
                                "weight_decay": 0.1, "threads": 1, "steps": BUDGET},
                     "fingerprint_fields": {"split_file_sha256": sha(sp / f"l0b_seed{s}_{spn}.npy"),
                                            "test_file_sha256": sha(sp / f"l0b_seed{s}_test.npy")},
                     "events": {"minibatch": {"batch_size": 16, "order": ARMS[arm][0]}},
                     "transitions": {"primary": {"generalization": {"first_crossing_step": tgen[(spn, arm)]}}}}
                if (spn, arm) == bad:
                    r[field] = val
                (d / "result.json").write_text(json.dumps(r))

        write()
        runs, missing, errors = load_block(sp, rw, [s])
        assert not missing and not errors, (missing, errors)
        x = seed_x(runs, s)
        tot = lambda extra: 0.01 * NFREQ + sum(v * v - 0.01 for v in extra.values())  # noqa: E731
        o_f_s = (0.01 * 5 + 0.25) / tot({5: 2.0, 11: 0.5})
        o_f_i, o_g = 0.06 / tot({5: 2.0}), 0.06 / tot({1: 1.0})
        assert abs(x["x_H1"] - ((0.05 + 1) / tot({12: 1.0}) - 0.06 / tot({}))) < 1e-9
        assert abs(x["x_H2"] - 0.5 * ((o_f_s - o_f_i) + (o_g - o_g))) < 1e-9
        dp_i = math.log(4.01 / 0.02) + math.log(1.01 / 0.02)
        dp_s = math.log(4.01 / 0.02) + math.log(1.01 / 0.02)  # 11 is in no target set
        assert abs(x["x_H3"] - (dp_s - dp_i)) < 1e-9 and abs(x["dpow_iid16w"] - dp_i) < 1e-9
        assert abs(x["x_H4"] - 0.5 * (math.log2(8000 / 4000) + math.log2(BUDGET / 7500))) < 1e-12
        assert abs(runs[(s, "F", "iid16w")]["o_mid"] - o_f_i) < 1e-6  # scale-free share
        for bad in ((("R", "stride16w"), "order", "iid"), (("F", "iid16w"), "batch_size", 32),
                    (("G", "iid16w"), "seed", 1), (("G", "stride16w"), "steps_completed", 29000),
                    (("F", "stride16w"), "split_file", f"x/l0b_seed{s}_G.npy")):
            write(*bad)
            assert load_block(sp, rw, [s])[2], bad
        write((("R", "iid16w")), "status", "running")
        assert load_block(sp, rw, [s])[1] == [f"{s}/R/iid16w"]


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    for flag in ("--selftest", "--analyze"):
        g.add_argument(flag, action="store_true")
    if ap.parse_args().selftest:
        return selftest()
    res = analyze()
    txt = json.dumps(res, indent=1, ensure_ascii=False)
    OUT.write_text(txt + "\n", encoding="utf-8")
    short = {k: v for k, v in res.items() if k not in ("loaded_runs", "missing_list")}
    short["missing_list_head"] = res.get("missing_list", [])[:12]
    print(json.dumps(short, indent=1, ensure_ascii=False))
    for r in res.get("loaded_runs", []):
        print(json.dumps(r, ensure_ascii=False))
    return 0 if res["block"] == "auswertbar" else 2


if __name__ == "__main__":
    sys.exit(main())
