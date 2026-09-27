"""R5 confirmation (programme A, paper observation "engineered splits grok earlier"): do spectrally concentrated training splits
generalise earlier than uniform ones, because of the concentration (not of any structured non-uniformity), and graded with it?
Session 31, UNTESTED (written outside the run window). Registration: lab/confirm/R5_REGISTRATION_DRAFT.md (version 2, session 31),
design points from the Codex design review of session 30 (lab/confirm/R5_codex_design_review_s30.txt).

Unit u (init seed 2720 + u; reserved 2720-2779): its own streams SeedSequence([R5_TAG, u, ...]), none drawn from the init seed:
common held-out test set T*_u (20 % of all pairs), pool = rest, one uniform key vector for all engineered arms, two target sets A/B
(5 of k = 1..56, independent of the init). Seven training sets of 3831 pairs, all evaluated on T*_u:
  R      uniform random from the pool
  E2_0   EXP-018 construction (wave over targets A, eps 2, floor 0.05, Efraimidis-Spirakis keys)     E2_1  same with targets B
  D_0    per anti-diagonal c = a + b exactly as many pairs as the REALISED E2_0 mask, positions uniform within c (Codex s30 blocker 1);
         redrawn (substream r = 0..19) until the frozen tolerances vs E2_0 hold (degree CV of a and b, swap share, test swap share
         within 0.04; target share of M0 <= 0.12)                                                    D_1   same for E2_1
  E1_0, E8_0   as E2_0 with eps 1 and 8 (same keys and wave phases): dose arms
Every run: freq_ban, GPU, --threads 1, 8000 steps, --stop-after-gen 8000 (no early stop: a stop after a transient first crossing would
censor engineered arms in their favour), W_E spectrum at 250.
Event (Codex s30 blocker 2): first test evaluation s with test acc >= 0.95 at s, s + 25 and s + 50, and train acc >= 0.99 at some step
<= s; none within 8000 -> censored at 8000. Bounded time b = min(event, 8000).
Primary family (Holm over 3 at 0.05; per contrast p = max(p_flip, p_sign), Codex s30 blocker 3):
  H-ER   L = log2 b(R) - mean_j log2 b(E2_j) > 0          (engineered earlier than uniform)
  H-ED   L = mean_j [log2 b(D_j) - log2 b(E2_j)] > 0       (earlier than the per-output-matched control: concentration, not marginals)
  H-dose L = log2 b(E1_0) - log2 b(E8_0) > 0              (graded: weakly concentrated later than strongly concentrated)
p_flip = one-sided sign-flip permutation p of mean L (Monte Carlo, fixed seed); p_sign = exact one-sided binomial p over the units whose
order is determined under censoring (aggregates: geometric mean of bounded times, observed only if all parts are observed).
Effect size (point estimate, Codex s30 blocker 4): 2 ** mean L = geometric mean ratio of bounded times, with a 95 % bootstrap CI.
Any missing or broken run, an identity violation -> "nicht auswertbar". Descriptive only: W_E target share at 250 per arm, first-crossing
steps, final test accuracy, share of arms generalised by 2000 / 8000, the matching statistics of D.

  python lab/tools/confirm_r5.py --hash-code | --splits M | --jobs M | --run M -- <cmd> | --analyze M | --selftest
"""
from __future__ import annotations

import json
import math
import shlex
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "tools"))
import confirm_p1 as c1  # noqa: E402  (read-only reuse: interp, bootstrap, holm)
import confirm_splits as cs  # noqa: E402  (m0 of a flat index split)
from bound_block import Block, selftest_binding  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

RAW = LAB / "confirm" / "r5_raw"
BIND = LAB / "confirm" / "r5_bindings"
SPL = LAB / "confirm" / "r5_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
P, N_TRAIN, N_FREQ, M = 113, 3831, 56, 5
N_TEST = int(round(0.2 * P * P))
CAP, EVAL, CONSEC, ACC_TEST, ACC_TRAIN = 8000, 25, 3, 0.95, 0.99
SPEC_AT = (250,)
ALPHA, R5_TAG, N_FLIP = 0.05, 20261001, 100_000
SEED0, SEED_MAX = 2720, 2779
# N_UNITS: fixed before freezing from lab/confirm/R5_power_sim.py on the EXP-018 pilot (rule in the registration: smallest n in
# {20, 30, 40, 50, 60} with simulated power >= 0.8 for H-ER and H-ED together; 60 if none). 20 is the floor, not a decision.
N_UNITS = 20
REGISTERED = {"units": N_UNITS, "steps": CAP, "device": "cuda", "threads": 1}
ARMS = ("R", "E2_0", "D_0", "E2_1", "D_1", "E1_0", "E8_0")
EPS = {"E1_0": 1.0, "E2_0": 2.0, "E8_0": 8.0, "E2_1": 2.0}
TOL, TSHARE_D_MAX, D_TRIES = 0.04, 0.12, 20
CODE_FILES = ("lab/tools/confirm_r5.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/result_loader.py",
              "lab/tools/confirm_splits.py", "lab/experiments/EXP-043-generalize-steering/make_split.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py",
              "lab/experiments/EXP-001-freq-ban/freq_ban.py")


# ---------------------------------------------------------------- design
def stream(*key: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([R5_TAG, *key]))


def init_seed(u: int) -> int:
    return SEED0 + u


def targets(u: int, j: int) -> list[int]:
    return sorted(int(k) for k in stream(u, 1, j).choice(np.arange(1, N_FREQ + 1), size=M, replace=False))


def wave(freqs: list[int], rng: np.random.Generator) -> np.ndarray:
    """EXP-016/018 construction: mean_k cos(2 pi k a / p + phi_{k, a+b}) over all p*p pairs (flat a*p + b)."""
    a, b = np.arange(P).repeat(P), np.tile(np.arange(P), P)
    phi = rng.uniform(0, 2 * np.pi, size=(len(freqs), P))
    return np.mean([np.cos(2 * np.pi * k * a / P + phi[i, (a + b) % P]) for i, k in enumerate(freqs)], axis=0)


def keyed(pool: np.ndarray, w: np.ndarray, u: np.ndarray) -> np.ndarray:
    return np.sort(pool[np.argsort(-(u ** (1.0 / w)))[:N_TRAIN]])


def antidiag(x: np.ndarray) -> np.ndarray:
    return (x // P + x % P) % P


def match_stats(x: np.ndarray, test: np.ndarray) -> dict[str, float]:
    a, b = x // P, x % P
    ca, cb = np.bincount(a, minlength=P), np.bincount(b, minlength=P)
    off, ta, tb = a != b, test // P, test % P
    toff = ta != tb
    return {"cv_a": float(ca.std() / ca.mean()), "cv_b": float(cb.std() / cb.mean()),
            "swap": float(np.isin(b[off] * P + a[off], x).mean()), "test_swap": float(np.isin(tb[toff] * P + ta[toff], x).mean())}


def target_share(x: np.ndarray, tg: list[int]) -> float:
    pw = cs.m0(x, "add", P)
    return float(pw[[k - 1 for k in tg]].sum() / pw.sum())


def matched_d(e: np.ndarray, pool: np.ndarray, test: np.ndarray, tg: list[int], u: int, j: int) -> tuple[np.ndarray, int]:
    """Per anti-diagonal exactly E's realised count, positions uniform within the pool; first substream within the tolerances."""
    ce, cp = np.bincount(antidiag(e), minlength=P), antidiag(pool)
    se = match_stats(e, test)
    for r in range(D_TRIES):
        rng = stream(u, 5, j, r)
        d = np.sort(np.concatenate([rng.choice(pool[cp == c], size=ce[c], replace=False) for c in range(P)]))
        sd = match_stats(d, test)
        if all(abs(sd[k] - se[k]) <= TOL for k in se) and target_share(d, tg) <= TSHARE_D_MAX:
            return d, r
    raise SystemExit(f"R5 unit {u}: no matched D_{j} within {D_TRIES} draws (design failure, before any run)")


def build_unit(u: int) -> dict:
    perm = stream(u, 0).permutation(P * P)
    test, pool = np.sort(perm[:N_TEST]), np.sort(perm[N_TEST:])
    keys = stream(u, 2).random(len(pool))
    sets: dict = {"test": test, "R": np.sort(stream(u, 3).choice(pool, size=N_TRAIN, replace=False))}
    meta: dict = {"unit": u, "init": init_seed(u), "targets": {}, "d_substream": {}}
    for j in (0, 1):
        tg = targets(u, j)
        meta["targets"][j] = tg
        w = wave(tg, stream(u, 4, j))[pool]
        for arm, eps in EPS.items():
            if arm.endswith(f"_{j}"):
                sets[arm] = keyed(pool, np.clip(1.0 + eps * w, 0.05, None), keys)
        sets[f"D_{j}"], meta["d_substream"][j] = matched_d(sets[f"E2_{j}"], pool, test, tg, u, j)
    return {"sets": {k: v.astype(np.int64) for k, v in sets.items()}, "meta": meta}


def arm_targets(u: int, arm: str) -> list[list[int]]:
    return [targets(u, 0), targets(u, 1)] if arm == "R" else [targets(u, int(arm[-1]))]


def split_path(u: int, arm: str) -> Path:
    return SPL / f"r5_u{u}_{arm}.npy"


def check_units(man: dict) -> int:
    n = man["units"]
    if not isinstance(n, int) or isinstance(n, bool) or n != N_UNITS or init_seed(n - 1) > SEED_MAX:
        raise SystemExit(f"R5 units must be {N_UNITS} (registration), got {n!r}")
    return n


def write_splits(man: dict) -> None:
    n = check_units(man)
    SPL.mkdir(parents=True, exist_ok=True)
    names = ("test",) + ARMS
    if any(split_path(u, a).exists() for u in range(n) for a in names):
        raise SystemExit("R5 splits exist already: never overwrite")
    for u in range(n):
        b = build_unit(u)
        for a in names:
            with open(split_path(u, a), "xb") as f:
                np.save(f, b["sets"][a])
        with open(SPL / f"r5_u{u}.json", "x", encoding="utf-8") as f:
            json.dump({**b["meta"], "match": {a: match_stats(b["sets"][a], b["sets"]["test"]) for a in ARMS},
                       "target_share_m0": {a: [target_share(b["sets"][a], tg) for tg in arm_targets(u, a)] for a in ARMS}}, f, indent=1)


def split_mismatch(u: int) -> str | None:
    b = build_unit(u)["sets"]
    for a in ("test",) + ARMS:
        f = split_path(u, a)
        if not f.exists():
            return f"unit {u}: {a} missing"
        if not np.array_equal(np.load(f), b[a]):
            return f"unit {u}: {a} differs from the deterministic rebuild"
    return None


def job(man: dict, u: int, arm: str) -> str:
    return (f"{c1.interp(man)} {FB} --seed {init_seed(u)} --condition baseline --threads {man['threads']} --device {man['device']} "
            f"--out-root lab/confirm/r5_raw --steps {man['steps']} --split-file lab/confirm/r5_splits/{split_path(u, arm).name} "
            f"--test-file lab/confirm/r5_splits/{split_path(u, 'test').name} --spectra-at {','.join(str(t) for t in SPEC_AT)} "
            f"--stop-after-gen {man['steps']}")


def trainer_jobs(man: dict) -> list[str]:
    return [job(man, u, a) for u in range(check_units(man)) for a in ARMS]


def expected_run_id(cmd: list[str]) -> str:
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    dev = (g("--device") or "cpu").replace(":", "")
    return (f"EXP-018_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}"
            + ("" if dev == "cpu" else f"_dev{dev}"))


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_r5", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_r5.py")


# ---------------------------------------------------------------- event and statistics
def event(dense: dict, last: int) -> tuple[int, bool]:
    """(step, observed): first test evaluation s with CONSEC consecutive evaluations >= ACC_TEST (s, s + 25, ...) and train acc >=
    ACC_TRAIN at some step <= s. Not found (or the run ended before step `last`) -> (CAP, False)."""
    ts, ta = [int(x) for x in dense["test_steps"]], [float(x) for x in dense["test_acc"]]
    rs, ra = [int(x) for x in dense["train_steps"]], [float(x) for x in dense["train_acc"]]
    if last < CAP or any(b - a != EVAL for a, b in zip(ts, ts[1:])):
        return CAP, False
    mem = min((s for s, v in zip(rs, ra) if v >= ACC_TRAIN), default=None)
    for i in range(len(ts) - CONSEC + 1):
        if mem is not None and mem <= ts[i] and all(ta[i + q] >= ACC_TEST for q in range(CONSEC)):
            return ts[i], True
    return CAP, False


def lb(t: tuple[int, bool]) -> float:
    return math.log2(min(t[0], CAP))


def agg(ts: list[tuple[int, bool]]) -> tuple[float, bool]:
    """Geometric mean of bounded times; observed only if every part is observed (else a lower bound)."""
    return 2 ** float(np.mean([lb(t) for t in ts])), all(t[1] for t in ts)


def order(early: tuple[float, bool], late: tuple[float, bool]) -> int | None:
    """+1 if `early` is surely earlier than `late`, -1 if surely later, None if tied or undetermined under censoring."""
    (ge, oe), (gl, ol) = early, late
    if oe and ol:
        return None if ge == gl else (1 if ge < gl else -1)
    if oe and ge < gl:
        return 1
    if ol and gl < ge:
        return -1
    return None


CONTRASTS = {"H-ER": ("E2", "R"), "H-ED": ("E2", "D"), "H-dose": ("E8_0", "E1_0")}   # (predicted earlier, predicted later)


def contrast(t: dict[str, tuple[int, bool]], h: str) -> tuple[float, int | None]:
    if h == "H-ER":
        e, x = [t["E2_0"], t["E2_1"]], [t["R"]]
        return lb(t["R"]) - np.mean([lb(v) for v in e]), order(agg(e), agg(x))
    if h == "H-ED":
        L = float(np.mean([lb(t[f"D_{j}"]) - lb(t[f"E2_{j}"]) for j in (0, 1)]))
        return L, order(agg([t["E2_0"], t["E2_1"]]), agg([t["D_0"], t["D_1"]]))
    return lb(t["E1_0"]) - lb(t["E8_0"]), order(agg([t["E8_0"]]), agg([t["E1_0"]]))


def p_flip(L: np.ndarray, rng: np.random.Generator) -> float:
    signs = rng.choice((-1.0, 1.0), size=(N_FLIP, len(L)))
    return float(((signs * L).mean(axis=1) >= L.mean() - 1e-12).mean())


def p_sign(k: int, n: int) -> float:
    return 1.0 if n == 0 else sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n


def verdict(rows: list[dict], n_planned: int, rng: np.random.Generator) -> dict:
    n_tech = sum(1 for r in rows if r.get("technical"))
    if n_tech or len(rows) != n_planned or n_planned < 3:
        return {"n": len(rows), "n_technical": n_tech, "verdict": "nicht auswertbar"}
    out: dict = {"n": len(rows), "n_technical": 0}
    ps = {}
    for h in CONTRASTS:
        L = np.array([r["L"][h] for r in rows])
        det = [r["order"][h] for r in rows if r["order"][h] is not None]
        pf, pg = p_flip(L, rng), p_sign(sum(1 for o in det if o > 0), len(det))
        ps[h] = max(pf, pg)
        ci = c1.boot_ci(L, rng)
        out[h] = {"mean_L": float(L.mean()), "ratio_geo": float(2 ** L.mean()), "ratio_ci95": [float(2 ** ci[0]), float(2 ** ci[1])],
                  "p_flip": pf, "p_sign": pg, "n_determined": len(det), "n_positive_order": sum(1 for o in det if o > 0), "p": ps[h]}
    ph = c1.holm(ps)
    for h in CONTRASTS:
        out[h]["p_holm"] = ph[h]
        out[h]["verdict"] = "bestätigt" if ph[h] < ALPHA else "nicht bestätigt"
    desc: dict = {}
    for a in ARMS:
        ev = [r["times"][a] for r in rows]
        desc[a] = {"observed": sum(1 for t in ev if t[1]), "by_2000": sum(1 for t in ev if t[1] and t[0] <= 2000),
                   "median_bounded": float(np.median([min(t[0], CAP) for t in ev])),
                   "we_target_share_250_mean": float(np.mean([r["we_share_250"][a] for r in rows])),
                   "first_crossing_median": float(np.median([r["first_crossing"][a] or CAP for r in rows]))}
    out["descriptive"] = desc
    return out


# ---------------------------------------------------------------- analysis
def one_run(man: dict, u: int, arm: str) -> dict | str:
    d, tag = run_dir(shlex.split(job(man, u, arm))), f"u{u}:{arm}"
    if not d.exists():
        return f"{tag}: fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt: {why}"
    L = load_run(d, Expect(seed=init_seed(u), device=man["device"], max_steps=man["steps"], split_file=split_path(u, arm),
                           test_file=split_path(u, "test"),
                           config={"p": P, "task": "add", "arch": "transformer", "lr": 1e-3, "weight_decay": 1.0},
                           at=SPEC_AT))
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt after load: {why}"
    res = L.res
    pw = L.spectrum(250)
    share = float(np.mean([pw[[k - 1 for k in tg]].sum() / pw.sum() for tg in arm_targets(u, arm)]))
    return {"event": event(res["dense"], int(res["steps_completed"])), "init_checksum": res.get("init_checksum_shared"),
            "first_crossing": (res.get("events") or {}).get("generalization_step"), "we_share_250": share,
            "test_final": (res.get("final_acc") or {}).get("test")}


def unit_row(man: dict, u: int) -> dict:
    runs = {a: one_run(man, u, a) for a in ARMS}
    bad = [v for v in runs.values() if isinstance(v, str)]
    if bad:
        return {"unit": u, "technical": True, "reason": "; ".join(bad[:4])}
    cks = {v["init_checksum"] for v in runs.values()}
    if len(cks) != 1 or not all(cks):
        return {"unit": u, "technical": True, "reason": "init checksums differ within the unit"}
    t = {a: v["event"] for a, v in runs.items()}
    Lo = {h: contrast(t, h) for h in CONTRASTS}
    return {"unit": u, "technical": False, "times": {a: list(v) for a, v in t.items()},
            "L": {h: float(v[0]) for h, v in Lo.items()}, "order": {h: v[1] for h, v in Lo.items()},
            "first_crossing": {a: v["first_crossing"] for a, v in runs.items()},
            "we_share_250": {a: v["we_share_250"] for a, v in runs.items()}, "test_final": {a: v["test_final"] for a, v in runs.items()}}


def analyze(manifest: Path) -> None:
    stale = LAB / "confirm" / "R5_summary.json"
    if stale.exists():
        stale.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    n = check_units(man)
    bad = [m for m in (split_mismatch(u) for u in range(n)) if m]
    if bad:
        raise SystemExit(f"R5 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = [unit_row(man, u) for u in range(n)]
    out = {"manifest_commit": man["commit"], "n_planned": n, "hypotheses": verdict(rows, n, np.random.default_rng(5)), "rows": rows}
    (LAB / "confirm" / "R5_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


# ---------------------------------------------------------------- selftest
def _dense(cross: int | None, mem: int = 120, dip: int | None = None) -> dict:
    ts = list(range(0, CAP + 1, EVAL))
    ta = [1.0 if cross is not None and s >= cross and s != dip else 0.1 for s in ts]
    rs = list(range(0, CAP + 1, 10))
    return {"test_steps": ts, "test_acc": ta, "train_steps": rs, "train_acc": [1.0 if s >= mem else 0.2 for s in rs]}


def _fake_rows(rng: np.random.Generator, n: int, speed: dict[str, float]) -> list[dict]:
    rows = []
    for u in range(n):
        base = rng.normal(0.0, 0.3)
        t = {}
        for a in ARMS:
            s = 2 ** (math.log2(speed[a]) + base + rng.normal(0.0, 0.3))
            s = int(round(s / EVAL)) * EVAL
            t[a] = (s, True) if s < CAP else (CAP, False)
        Lo = {h: contrast(t, h) for h in CONTRASTS}
        rows.append({"unit": u, "technical": False, "times": t, "L": {h: v[0] for h, v in Lo.items()},
                     "order": {h: v[1] for h, v in Lo.items()}, "first_crossing": {a: t[a][0] for a in ARMS},
                     "we_share_250": {a: 0.3 for a in ARMS}})
    return rows


def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    for bad in ({"units": N_UNITS + 1}, {"units": float(N_UNITS)}, {"units": True}):
        try:
            check_units({**man, **bad})
            raise AssertionError(f"bad units accepted: {bad}")
        except SystemExit:
            pass
    for bad in ({"steps": 8000.0}, {"steps": 2000}, {"threads": True}, {"device": "cpu"}):
        try:
            BLOCK.check_registered({**man, **bad})
            raise AssertionError(f"unregistered manifest accepted: {bad}")
        except SystemExit:
            pass
    # design: determinism, sizes, disjoint test, independent targets, exact per-output match of D, dose arms share keys
    b0, b1 = build_unit(0), build_unit(1)
    s = b0["sets"]
    assert all(np.array_equal(s[a], build_unit(0)["sets"][a]) for a in ("test",) + ARMS)
    assert len(s["test"]) == N_TEST and all(len(s[a]) == N_TRAIN == len(np.unique(s[a])) for a in ARMS)
    assert all(np.intersect1d(s[a], s["test"]).size == 0 for a in ARMS)
    assert not np.array_equal(s["test"], b1["sets"]["test"]) and targets(0, 0) != targets(0, 1)
    for j in (0, 1):
        assert np.array_equal(np.bincount(antidiag(s[f"D_{j}"]), minlength=P), np.bincount(antidiag(s[f"E2_{j}"]), minlength=P))
        me, md = match_stats(s[f"E2_{j}"], s["test"]), match_stats(s[f"D_{j}"], s["test"])
        assert all(abs(me[k] - md[k]) <= TOL for k in me)
        assert target_share(s[f"E2_{j}"], targets(0, j)) > 0.15 and target_share(s[f"D_{j}"], targets(0, j)) <= TSHARE_D_MAX
    sh = [target_share(s[a], targets(0, 0)) for a in ("E1_0", "E2_0", "E8_0")]
    assert sh[0] < sh[1] < sh[2] and target_share(s["R"], targets(0, 0)) < 0.13, sh
    assert len({init_seed(u) for u in range(N_UNITS)}) == N_UNITS and init_seed(N_UNITS - 1) <= SEED_MAX
    # jobs and run ids
    tj = trainer_jobs(man)
    assert len(tj) == len(ARMS) * N_UNITS == len(set(tj)) and all("r5_raw" in j and "\\" not in j and "--stop-after-gen 8000" in j for j in tj)
    assert len({expected_run_id(shlex.split(j)) for j in tj}) == len(tj)
    assert expected_run_id(shlex.split(tj[0])) == "EXP-018_baseline_seed2720_thr1_r5_u0_R_devcuda", expected_run_id(shlex.split(tj[0]))
    assert "--test-file lab/confirm/r5_splits/r5_u0_test.npy" in tj[0] and "--spectra-at 250" in tj[0] and "--steps 8000" in tj[0]
    assert all(j.startswith("python lab/tools/confirm_r5.py --run M -- ") for j in BLOCK.jobs(man, "M"))
    BLOCK.check_job(man, shlex.split(tj[0]))
    try:
        BLOCK.check_job(man, shlex.split(tj[0]) + ["--force"])
        raise AssertionError("foreign command accepted")
    except SystemExit:
        pass
    assert run_dir(shlex.split(job(man, 0, "D_1"))) == RAW / "EXP-018_baseline_seed2720_thr1_r5_u0_D_1_devcuda"
    # event rule
    assert event(_dense(500), CAP) == (500, True) and event(_dense(None), CAP) == (CAP, False)
    assert event(_dense(500, dip=525), CAP) == (550, True)                       # a dip resets the run of 3
    assert event(_dense(100, mem=300), CAP) == (300, True)                        # memorisation must come first
    assert event(_dense(7975), CAP) == (CAP, False) and event(_dense(500), 7000) == (CAP, False)
    # contrasts and censoring
    t = {a: (1000, True) for a in ARMS} | {"R": (CAP, False), "E8_0": (500, True), "E1_0": (2000, True)}
    assert contrast(t, "H-ER")[1] == 1 and abs(contrast(t, "H-ER")[0] - math.log2(8)) < 1e-12
    assert contrast(t, "H-ED") == (0.0, None) and contrast(t, "H-dose") == (2.0, 1)
    assert order((CAP, False), (CAP, False)) is None and order((900.0, True), (700.0, True)) == -1
    assert abs(p_sign(9, 9) - 1 / 512) < 1e-12 and p_sign(0, 0) == 1.0
    # verdict on synthetic studies
    rng = np.random.default_rng(0)
    fast = {"R": 6000, "D_0": 3000, "D_1": 3000, "E2_0": 800, "E2_1": 800, "E1_0": 2500, "E8_0": 450}
    v = verdict(_fake_rows(rng, 20, fast), 20, rng)
    assert all(v[h]["verdict"] == "bestätigt" for h in CONTRASTS), v
    null = {a: 1500 for a in ARMS}
    v = verdict(_fake_rows(rng, 20, null), 20, rng)
    assert all(v[h]["verdict"] == "nicht bestätigt" for h in CONTRASTS), v
    only_marg = {**fast, "D_0": 800, "D_1": 800}                                    # D as fast as E: H-ED must fail
    v = verdict(_fake_rows(rng, 20, only_marg), 20, rng)
    assert v["H-ER"]["verdict"] == "bestätigt" and v["H-ED"]["verdict"] == "nicht bestätigt", v
    assert verdict(_fake_rows(rng, 19, fast), 20, rng)["verdict"] == "nicht auswertbar"
    assert verdict(_fake_rows(rng, 19, fast) + [{"unit": 19, "technical": True}], 20, rng)["verdict"] == "nicht auswertbar"
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    loaded = {Path(m.__file__).resolve().relative_to(ROOT.resolve()).as_posix() for m in list(sys.modules.values())
              if getattr(m, "__file__", None) and Path(m.__file__).resolve().is_relative_to((ROOT / "lab").resolve())}
    assert loaded <= set(CODE_FILES), sorted(loaded - set(CODE_FILES))
    print("[confirm_r5] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
