"""R12 confirmation (paper Result 2 scope, FINDINGS open limitation "R5 holds for addition mod 113 only"): do spectrally engineered
training splits also generalise earlier than uniform ones, and than a per-output-matched control, for addition mod 97 and
multiplication mod 113? Session 57 (2026-09-30), written inside the run window, before any R12 run. Registration:
lab/confirm/R12_REGISTRATION_DRAFT.md. Design = R5 (lab/tools/confirm_r5.py, frozen, unchanged) transferred to the group coordinates of
EXP-043 (lab/experiments/EXP-043-generalize-steering/make_split.py, read-only reuse): add p on Z_p (u = a, v = b), mul p on Z_{p-1}
via the discrete log (pairs with a zero keep the neutral weight 1). The dose arms of R5 are dropped.

Per task t in (add 97, mul 113) and unit u (0..19; init seed SEED0[t] + INIT_PERM[u], reserved add97 4200-4219, mul113 4220-4239):
own streams SeedSequence([R12_TAG, t, u, ...]), none drawn from the init seed. Common held-out test set T*_u (20 % of all p^2 pairs),
pool = rest, one uniform key vector for both engineered arms, two target sets A/B (5 of k = 1..(n-1)//2, n = group order, independent
of the init). Five training sets of round(0.3 p^2) pairs, all evaluated on T*_u:
  R      uniform random from the pool
  E2_0   EXP-043 construction (wave over targets A in group coordinates, eps 2, floor 0.05, Efraimidis-Spirakis keys)   E2_1 targets B
  D_0    per output value c = a (op) b mod p exactly as many pairs as the REALISED E2_0 mask, positions uniform within c; redrawn
         (substream r = 0..19) until the tolerances of R5 hold vs E2_0 (degree CV of a and b, swap share, test swap share within
         0.04; test-neighbour coverage within 0.02; a-b graph connected; target share of M0 <= uniform share M/K + 0.031)  D_1 for E2_1
Every run: freq_ban, GPU, --threads 1, 8000 steps, --stop-after-gen 8000, W_E spectrum at 250 (descriptive, add only: spectra.npy is
the additive DFT, not the group basis of mul).
Event (as R5): first test evaluation s with test acc >= 0.95 at s, s + 25 and s + 50, and train acc >= 0.99 at some step <= s; none
within 8000 -> censored at 8000. Bounded time b = min(event, 8000).
Primary family (Holm over 4 at 0.05; per contrast p = max(p_flip, p_sign); sharp randomisation null as R5), per task:
  H-ER   L = log2 b(R) - log2 b(E2_0) > 0
  H-ED   L = mean_j [log2 b(D_j) - log2 b(E2_j)] > 0
Effect size: 2 ** mean L (geometric mean ratio of bounded times) with a 95 % bootstrap CI. Any missing or broken run, a malformed
dense trace, an identity violation -> the whole block "nicht auswertbar".

  python lab/tools/confirm_r12.py --hash-code | --splits M | --jobs M | --run M -- <cmd> | --analyze M | --selftest
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
sys.path.insert(0, str(LAB / "experiments" / "EXP-043-generalize-steering"))
import confirm_p1 as c1  # noqa: E402  (read-only reuse: interp, bootstrap, holm)
import confirm_r5 as r5  # noqa: E402  (read-only reuse: event rule, dense validation, order, p values)
import confirm_splits as cs  # noqa: E402  (m0 in group coordinates)
from bound_block import Block, selftest_binding  # noqa: E402
from make_split import group_coords, n_freq  # noqa: E402
from result_loader import Expect, load_run, sorted_hash  # noqa: E402

RAW = LAB / "confirm" / "r12_raw"
BIND = LAB / "confirm" / "r12_bindings"
SPL = LAB / "confirm" / "r12_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
TASKS = (("add", 97), ("mul", 113))
M, TRAIN_FRAC, TEST_FRAC = 5, 0.3, 0.2
CAP, EVAL = r5.CAP, r5.EVAL
SPEC_AT = (250,)
ALPHA, R12_TAG, N_FLIP = 0.05, 20260930, r5.N_FLIP
SEED0 = {"add97": 4200, "mul113": 4220}
N_UNITS = 20                         # per task, as R5 (no power analysis for H-ED on these tasks; see the registration)
REGISTERED = {"units": N_UNITS, "steps": CAP, "device": "cuda", "threads": 1}
ARMS = ("R", "E2_0", "D_0", "E2_1", "D_1")
EPS = 2.0
TOL, TOL_COV, TSHARE_MARGIN, D_TRIES = r5.TOL, r5.TOL_COV, 0.031, r5.D_TRIES
HYPS = ("H-ER", "H-ED")
CODE_FILES = ("lab/tools/confirm_r12.py", "lab/tools/confirm_r5.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py",
              "lab/tools/result_loader.py", "lab/tools/confirm_splits.py", "lab/experiments/EXP-043-generalize-steering/make_split.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py",
              "lab/experiments/EXP-001-freq-ban/freq_ban.py")

# Frozen literal (session 57, numpy: default_rng(SeedSequence([R12_TAG, 97])).permutation(20)); a literal, so the code hash covers it
INIT_PERM = [5, 13, 9, 2, 15, 1, 17, 8, 16, 19, 10, 7, 4, 6, 14, 3, 12, 18, 0, 11]


# ---------------------------------------------------------------- design
def tname(task: str, p: int) -> str:
    return f"{task}{p}"


def tidx(task: str, p: int) -> int:
    return TASKS.index((task, p))


def sizes(p: int) -> tuple[int, int]:
    return int(round(TRAIN_FRAC * p * p)), int(round(TEST_FRAC * p * p))


def stream(task: str, p: int, *key: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([R12_TAG, tidx(task, p), *key]))


def init_seed(task: str, p: int, u: int) -> int:
    return SEED0[tname(task, p)] + INIT_PERM[u]


def kmax(task: str, p: int) -> int:
    return n_freq(group_coords(task, p)[3])


def targets(task: str, p: int, u: int, j: int) -> list[int]:
    return sorted(int(k) for k in stream(task, p, u, 1, j).choice(np.arange(1, kmax(task, p) + 1), size=M, replace=False))


def weights(task: str, p: int, freqs: list[int], rng: np.random.Generator) -> np.ndarray:
    """EXP-043 construction over all p*p pairs (flat a*p + b): q = max(0.05, 1 + eps * wave) on valid pairs, 1 on mul pairs with a 0."""
    uu, vv, valid, n = group_coords(task, p)
    phi = rng.uniform(0, 2 * np.pi, size=(len(freqs), n))
    wave = np.mean([np.cos(2 * np.pi * k * uu / n + phi[i, (uu + vv) % n]) for i, k in enumerate(freqs)], axis=0)
    return np.where(valid, np.clip(1.0 + EPS * wave, 0.05, None), 1.0)


def keyed(pool: np.ndarray, w: np.ndarray, key: np.ndarray, n_train: int) -> np.ndarray:
    return np.sort(pool[np.argsort(-(key ** (1.0 / w)))[:n_train]])


def output(x: np.ndarray, task: str, p: int) -> np.ndarray:
    a, b = x // p, x % p
    return (a + b) % p if task == "add" else (a * b) % p


def match_stats(x: np.ndarray, test: np.ndarray, p: int) -> dict[str, float]:
    a, b = x // p, x % p
    ca, cb = np.bincount(a, minlength=p), np.bincount(b, minlength=p)
    off, ta, tb = a != b, test // p, test % p
    toff = ta != tb
    return {"cv_a": float(ca.std() / ca.mean()), "cv_b": float(cb.std() / cb.mean()),
            "swap": float(np.isin(b[off] * p + a[off], x).mean()), "test_swap": float(np.isin(tb[toff] * p + ta[toff], x).mean()),
            "test_cov": float((ca[ta] + cb[tb]).mean() / (2 * len(x) / p))}


def components(x: np.ndarray, p: int) -> int:
    """Connected components of the bipartite graph a -- b of the training pairs (2p nodes)."""
    par = list(range(2 * p))

    def find(i: int) -> int:
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    for a, b in zip((x // p).tolist(), (x % p).tolist()):
        par[find(a)] = find(p + b)
    return len({find(i) for i in range(2 * p)})


def matched(sd: dict, se: dict) -> bool:
    return all(abs(sd[k] - se[k]) <= (TOL_COV if k == "test_cov" else TOL) for k in se)


def target_share(x: np.ndarray, tg: list[int], task: str, p: int) -> float:
    pw = cs.m0(x, task, p)
    return float(pw[[k - 1 for k in tg]].sum() / pw.sum())


def tshare_max(task: str, p: int) -> float:
    return M / kmax(task, p) + TSHARE_MARGIN


def matched_d(e: np.ndarray, pool: np.ndarray, test: np.ndarray, tg: list[int], task: str, p: int, u: int, j: int
              ) -> tuple[np.ndarray, int]:
    """Per output value exactly E's realised count, positions uniform within the pool; first substream within the tolerances."""
    ce, cp = np.bincount(output(e, task, p), minlength=p), output(pool, task, p)
    se = match_stats(e, test, p)
    for r in range(D_TRIES):
        rng = stream(task, p, u, 5, j, r)
        d = np.sort(np.concatenate([rng.choice(pool[cp == c], size=ce[c], replace=False) for c in range(p)]))
        if (matched(match_stats(d, test, p), se) and components(d, p) == 1
                and target_share(d, tg, task, p) <= tshare_max(task, p)):
            return d, r
    raise SystemExit(f"R12 {tname(task, p)} unit {u}: no matched D_{j} within {D_TRIES} draws (design failure, before any run)")


def build_unit(task: str, p: int, u: int) -> dict:
    n_train, n_test = sizes(p)
    perm = stream(task, p, u, 0).permutation(p * p)
    test, pool = np.sort(perm[:n_test]), np.sort(perm[n_test:])
    key = stream(task, p, u, 2).random(len(pool))
    sets: dict = {"test": test, "R": np.sort(stream(task, p, u, 3).choice(pool, size=n_train, replace=False))}
    meta: dict = {"task": task, "p": p, "unit": u, "init": init_seed(task, p, u), "targets": {}, "d_substream": {}}
    for j in (0, 1):
        tg = targets(task, p, u, j)
        meta["targets"][j] = tg
        sets[f"E2_{j}"] = keyed(pool, weights(task, p, tg, stream(task, p, u, 4, j))[pool], key, n_train)
        sets[f"D_{j}"], meta["d_substream"][j] = matched_d(sets[f"E2_{j}"], pool, test, tg, task, p, u, j)
    return {"sets": {k: v.astype(np.int64) for k, v in sets.items()}, "meta": meta}


def arm_targets(task: str, p: int, u: int, arm: str) -> list[list[int]]:
    return [targets(task, p, u, 0), targets(task, p, u, 1)] if arm == "R" else [targets(task, p, u, int(arm[-1]))]


def split_path(task: str, p: int, u: int, arm: str) -> Path:
    return SPL / f"r12_{tname(task, p)}_u{u}_{arm}.npy"


def check_units(man: dict) -> int:
    n = man["units"]
    if not isinstance(n, int) or isinstance(n, bool) or n != N_UNITS:
        raise SystemExit(f"R12 units must be {N_UNITS} (registration), got {n!r}")
    return n


def write_splits(man: dict) -> None:
    n = check_units(man)
    SPL.mkdir(parents=True, exist_ok=True)
    names = ("test",) + ARMS
    if any(split_path(t, p, u, a).exists() for t, p in TASKS for u in range(n) for a in names):
        raise SystemExit("R12 splits exist already: never overwrite")
    for task, p in TASKS:
        for u in range(n):
            b = build_unit(task, p, u)
            for a in names:
                with open(split_path(task, p, u, a), "xb") as f:
                    np.save(f, b["sets"][a])
            s = b["sets"]
            with open(SPL / f"r12_{tname(task, p)}_u{u}.json", "x", encoding="utf-8") as f:
                json.dump({**b["meta"], "match": {a: {**match_stats(s[a], s["test"], p), "components": components(s[a], p)} for a in ARMS},
                           "target_share_m0": {a: [target_share(s[a], tg, task, p) for tg in arm_targets(task, p, u, a)] for a in ARMS}},
                          f, indent=1)


def split_mismatch(task: str, p: int, u: int) -> str | None:
    b = build_unit(task, p, u)["sets"]
    for a in ("test",) + ARMS:
        f = split_path(task, p, u, a)
        if not f.exists():
            return f"{tname(task, p)} unit {u}: {a} missing"
        if not np.array_equal(np.load(f), b[a]):
            return f"{tname(task, p)} unit {u}: {a} differs from the deterministic rebuild"
    return None


def job(man: dict, task: str, p: int, u: int, arm: str) -> str:
    return (f"{c1.interp(man)} {FB} --seed {init_seed(task, p, u)} --condition baseline --threads {man['threads']} "
            f"--device {man['device']} --p {p} --task {task} --out-root lab/confirm/r12_raw --steps {man['steps']} "
            f"--split-file lab/confirm/r12_splits/{split_path(task, p, u, arm).name} "
            f"--test-file lab/confirm/r12_splits/{split_path(task, p, u, 'test').name} "
            f"--spectra-at {','.join(str(t) for t in SPEC_AT)} --stop-after-gen {man['steps']}")


def trainer_jobs(man: dict) -> list[str]:
    """All runs of both tasks in one seeded random order (execution order only; the committed job file is the record)."""
    jobs = [job(man, t, p, u, a) for t, p in TASKS for u in range(check_units(man)) for a in ARMS]
    order_ = np.random.default_rng(np.random.SeedSequence([R12_TAG, 96, len(jobs)])).permutation(len(jobs))
    return [jobs[i] for i in order_]


def expected_run_id(cmd: list[str]) -> str:
    """freq_ban ids for p/task != 113/add with a split file (as confirm_r11): EXP-043 prefix, '_{task}{p}', then _dev."""
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    rid = f"EXP-043_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}_{g('--task')}{g('--p')}"
    dev = g("--device") or "cpu"
    return rid + ("" if dev == "cpu" else f"_dev{dev.replace(':', '')}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_r12", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_r12.py")


# ---------------------------------------------------------------- statistics
def contrast(t: dict[str, tuple[int, bool]], h: str) -> tuple[float, int | None]:
    if h == "H-ER":
        return r5.lb(t["R"]) - r5.lb(t["E2_0"]), r5.order(r5.agg([t["E2_0"]]), r5.agg([t["R"]]))
    L = float(np.mean([r5.lb(t[f"D_{j}"]) - r5.lb(t[f"E2_{j}"]) for j in (0, 1)]))
    return L, r5.order(r5.agg([t["E2_0"], t["E2_1"]]), r5.agg([t["D_0"], t["D_1"]]))


def task_stats(rows: list[dict], rng: np.random.Generator) -> dict:
    out: dict = {}
    for h in HYPS:
        L = np.array([r["L"][h] for r in rows])
        det = [r["order"][h] for r in rows if r["order"][h] is not None]
        pf, pg = r5.p_flip(L, rng), r5.p_sign(sum(1 for o in det if o > 0), len(det))
        ci = c1.boot_ci(L, rng)
        out[h] = {"mean_L": float(L.mean()), "ratio_geo": float(2 ** L.mean()), "ratio_ci95": [float(2 ** ci[0]), float(2 ** ci[1])],
                  "p_flip": pf, "p_sign": pg, "n_determined": len(det), "n_positive_order": sum(1 for o in det if o > 0),
                  "p": max(pf, pg)}
    desc: dict = {}
    for a in ARMS:
        ev = [r["times"][a] for r in rows]
        sh = [r["we_share_250"][a] for r in rows if r["we_share_250"][a] is not None]
        desc[a] = {"observed": sum(1 for t in ev if t[1]), "by_2000": sum(1 for t in ev if t[1] and t[0] <= 2000),
                   "median_bounded": float(np.median([min(t[0], CAP) for t in ev])),
                   "we_target_share_250_mean": float(np.mean(sh)) if sh else None,
                   "first_crossing_median": float(np.median([CAP if r["first_crossing"][a] is None else r["first_crossing"][a]
                                                             for r in rows])),
                   "test_final_mean": float(np.mean([r["test_final"][a] for r in rows]))}
    out["descriptive"] = desc
    return out


def verdict(rows_by_task: dict[str, list[dict]], n_planned: int, rng: np.random.Generator) -> dict:
    n_tech = sum(1 for rows in rows_by_task.values() for r in rows if r.get("technical"))
    if (n_tech or set(rows_by_task) != {tname(t, p) for t, p in TASKS} or n_planned < 3
            or any(len(rows) != n_planned for rows in rows_by_task.values())):
        return {"n_technical": n_tech, "verdict": "nicht auswertbar"}
    out: dict = {tn: task_stats(rows, rng) for tn, rows in rows_by_task.items()}
    ph = c1.holm({f"{tn}:{h}": out[tn][h]["p"] for tn in out for h in HYPS})
    for tn in rows_by_task:
        for h in HYPS:
            out[tn][h]["p_holm"] = ph[f"{tn}:{h}"]
            out[tn][h]["verdict"] = "bestätigt" if ph[f"{tn}:{h}"] < ALPHA else "nicht bestätigt"
    out["n_technical"] = 0
    return out


# ---------------------------------------------------------------- analysis
def measure(d: Path, seed: int, task: str, p: int, device: str, steps: int, split_file: Path, test_file: Path,
            tgts: list[list[int]]) -> dict | str:
    """Common loader (seed, device, budget, split and TEST hash, config, finite spectrum at 250) + dense validation + event."""
    L = load_run(d, Expect(seed=seed, device=device, max_steps=steps, split_file=split_file, test_file=test_file,
                           config={"p": p, "task": task, "arch": "transformer", "lr": 1e-3, "weight_decay": 1.0, "train_frac": TRAIN_FRAC},
                           at=SPEC_AT))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    res = L.res
    if (why := r5.dense_violation(res.get("dense"))):
        return f"defekt: {why}"
    test_final = (res.get("final_acc") or {}).get("test")
    if type(test_final) not in (int, float) or not math.isfinite(test_final):
        return "defekt: final test accuracy missing or not finite"
    share = None
    if task == "add":                                    # spectra.npy is the additive DFT: meaningful for add only
        pw = L.spectrum(250)
        share = float(np.mean([pw[[k - 1 for k in tg]].sum() / pw.sum() for tg in tgts]))
    return {"event": r5.event(res["dense"], int(res["steps_completed"])), "init_checksum": res.get("init_checksum_shared"),
            "first_crossing": (res.get("events") or {}).get("generalization_step"), "we_share_250": share,
            "test_final": test_final}


def one_run(man: dict, task: str, p: int, u: int, arm: str) -> dict | str:
    d, tag = run_dir(shlex.split(job(man, task, p, u, arm))), f"{tname(task, p)}:u{u}:{arm}"
    if not d.exists():
        return f"{tag}: fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt: {why}"
    m = measure(d, init_seed(task, p, u), task, p, man["device"], man["steps"], split_path(task, p, u, arm),
                split_path(task, p, u, "test"), arm_targets(task, p, u, arm))
    if isinstance(m, str):
        return f"{tag}: {m}"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt after load: {why}"
    return m


def unit_row(man: dict, task: str, p: int, u: int) -> dict:
    runs = {a: one_run(man, task, p, u, a) for a in ARMS}
    bad = [v for v in runs.values() if isinstance(v, str)]
    if bad:
        return {"unit": u, "technical": True, "reason": "; ".join(bad[:4])}
    cks = {v["init_checksum"] for v in runs.values()}
    if len(cks) != 1 or not all(cks):
        return {"unit": u, "technical": True, "reason": "init checksums differ within the unit"}
    t = {a: v["event"] for a, v in runs.items()}
    Lo = {h: contrast(t, h) for h in HYPS}
    return {"unit": u, "technical": False, "times": {a: list(v) for a, v in t.items()},
            "L": {h: float(v[0]) for h, v in Lo.items()}, "order": {h: v[1] for h, v in Lo.items()},
            "first_crossing": {a: v["first_crossing"] for a, v in runs.items()},
            "we_share_250": {a: v["we_share_250"] for a, v in runs.items()}, "test_final": {a: v["test_final"] for a, v in runs.items()}}


def analyze(manifest: Path) -> None:
    stale = LAB / "confirm" / "R12_summary.json"
    if stale.exists():
        stale.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    n = check_units(man)
    bad = [m for m in (split_mismatch(t, p, u) for t, p in TASKS for u in range(n)) if m]
    if bad:
        raise SystemExit(f"R12 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = {tname(t, p): [unit_row(man, t, p, u) for u in range(n)] for t, p in TASKS}
    meta = {tname(t, p): [json.loads((SPL / f"r12_{tname(t, p)}_u{u}.json").read_text(encoding="utf-8")) for u in range(n)]
            for t, p in TASKS}
    out = {"manifest_commit": man["commit"], "n_planned_per_task": n, "hypotheses": verdict(rows, n, np.random.default_rng(12)),
           "d_matching": {tn: {a: {k: float(np.mean([m["match"][a][k] for m in ms])) for k in ms[0]["match"][a]} for a in ARMS}
                          for tn, ms in meta.items()},
           "d_substreams": {tn: [m["d_substream"] for m in ms] for tn, ms in meta.items()}, "rows": rows}
    (LAB / "confirm" / "R12_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


# ---------------------------------------------------------------- selftest
def _fake_rows(rng: np.random.Generator, n: int, speed: dict[str, float], d_copies_e: bool = False) -> list[dict]:
    rows = []
    for u in range(n):
        base = rng.normal(0.0, 0.3)
        t = {}
        for a in ARMS:
            s = int(round(2 ** (math.log2(speed[a]) + base + rng.normal(0.0, 0.3)) / EVAL)) * EVAL
            t[a] = (s, True) if s < CAP else (CAP, False)
        if d_copies_e:
            t["D_0"], t["D_1"] = t["E2_0"], t["E2_1"]
        Lo = {h: contrast(t, h) for h in HYPS}
        rows.append({"unit": u, "technical": False, "times": t, "L": {h: v[0] for h, v in Lo.items()},
                     "order": {h: v[1] for h, v in Lo.items()}, "first_crossing": {a: t[a][0] for a in ARMS},
                     "we_share_250": {a: None for a in ARMS}, "test_final": {a: 1.0 for a in ARMS}})
    return rows


def _selftest_measure() -> None:
    """Loader integration with --test-file on synthetic run directories (temporary files only), both tasks."""
    import tempfile
    with tempfile.TemporaryDirectory(dir=LAB / "confirm") as tmp:
        root = Path(tmp)
        for task, p in TASKS:
            n_train, n_test = sizes(p)
            sp, te, other = root / f"s{p}.npy", root / f"t{p}.npy", root / f"o{p}.npy"
            np.save(sp, np.arange(0, 3 * n_train, 3, dtype=np.int64))
            np.save(te, np.arange(1, 3 * n_test, 3, dtype=np.int64))
            np.save(other, np.arange(2, 3 * n_test, 3, dtype=np.int64))
            tg = [[1, 2, 3, 4, 5]]

            def make(name: str, **patch: object) -> Path:
                d = root / f"{task}{p}_{name}"
                d.mkdir()
                res = {"status": "completed", "seed": 4200, "device": "cuda", "max_steps": CAP, "steps_completed": CAP,
                       "split_hash": sorted_hash(np.load(sp)), "test_hash": sorted_hash(np.load(te)), "init_checksum_shared": "c",
                       "config": {"p": p, "task": task, "arch": "transformer", "lr": 1e-3, "weight_decay": 1.0, "train_frac": 0.3},
                       "events": {"generalization_step": 500}, "final_acc": {"test": 1.0}, "dense": r5._dense(500), **patch}
                (d / "result.json").write_text(json.dumps(res), encoding="utf-8")
                pw = np.ones((1, kmax(task, p)))
                pw[0, :5] = 10.0
                np.save(d / "spectra.npy", pw)
                np.save(d / "spectra_steps.npy", np.array([250]))
                return d
            ok = measure(make("ok"), 4200, task, p, "cuda", CAP, sp, te, tg)
            assert isinstance(ok, dict) and ok["event"] == (500, True), ok
            if task == "add":
                assert abs(ok["we_share_250"] - 50 / (50 + kmax(task, p) - 5)) < 1e-12, ok
            else:
                assert ok["we_share_250"] is None, ok
            assert "test_hash" in measure(make("wrongtest", test_hash=sorted_hash(np.load(other))), 4200, task, p, "cuda", CAP, sp, te, tg)
            assert "dense" in measure(make("baddense", dense={**r5._dense(500), "test_steps": list(range(0, CAP, EVAL))}),
                                      4200, task, p, "cuda", CAP, sp, te, tg)
            assert "steps_completed" in measure(make("short", steps_completed=7000), 4200, task, p, "cuda", CAP, sp, te, tg)
            assert "seed" in measure(make("seed", seed=4201), 4200, task, p, "cuda", CAP, sp, te, tg)
            wrong_task = measure(make("task", config={"p": p, "task": "mul" if task == "add" else "add", "arch": "transformer",
                                                      "lr": 1e-3, "weight_decay": 1.0, "train_frac": 0.3}), 4200, task, p, "cuda", CAP, sp, te, tg)
            assert isinstance(wrong_task, str), wrong_task
            assert isinstance(measure(make("frac", config={"p": p, "task": task, "arch": "transformer", "lr": 1e-3, "weight_decay": 1.0,
                                                           "train_frac": 0.5}), 4200, task, p, "cuda", CAP, sp, te, tg), str)
            assert "final test" in measure(make("nofinal", final_acc={}), 4200, task, p, "cuda", CAP, sp, te, tg)


def _selftest_design() -> None:
    assert sorted(INIT_PERM) == list(range(N_UNITS)) and INIT_PERM != sorted(INIT_PERM)
    assert INIT_PERM == np.random.default_rng(np.random.SeedSequence([R12_TAG, 97])).permutation(N_UNITS).tolist()
    seeds = [init_seed(t, p, u) for t, p in TASKS for u in range(N_UNITS)]
    assert sorted(seeds) == list(range(4200, 4240))
    assert kmax("add", 97) == 48 and kmax("mul", 113) == 55 and sizes(97) == (2823, 1882) and sizes(113) == (3831, 2554)
    for task, p in TASKS:
        n_train, n_test = sizes(p)
        s = build_unit(task, p, 0)["sets"]
        assert all(np.array_equal(s[a], build_unit(task, p, 0)["sets"][a]) for a in ("test",) + ARMS)
        assert not np.array_equal(s["test"], build_unit(task, p, 1)["sets"]["test"]) and targets(task, p, 0, 0) != targets(task, p, 0, 1)
        for u in range(N_UNITS):
            s = build_unit(task, p, u)["sets"]
            assert len(s["test"]) == n_test and all(len(s[a]) == n_train == len(np.unique(s[a])) for a in ARMS), (task, u)
            assert all(np.intersect1d(s[a], s["test"]).size == 0 for a in ARMS), (task, u)
            for j in (0, 1):
                e, d, tg = s[f"E2_{j}"], s[f"D_{j}"], targets(task, p, u, j)
                assert np.array_equal(np.bincount(output(d, task, p), minlength=p), np.bincount(output(e, task, p), minlength=p)), (task, u, j)
                assert matched(match_stats(d, s["test"], p), match_stats(e, s["test"], p)) and components(d, p) == 1, (task, u, j)
                assert target_share(d, tg, task, p) <= tshare_max(task, p) < target_share(e, tg, task, p), (task, u, j)
                assert target_share(s["R"], tg, task, p) < target_share(e, tg, task, p), (task, u, j)
    # output(): add is the anti-diagonal of R5; mul pairs with a zero map to 0
    x = np.arange(113 * 113)
    assert np.array_equal(output(x, "add", 113), r5.antidiag(x))
    assert set(output(np.array([0 * 113 + 5, 7 * 113 + 0]), "mul", 113).tolist()) == {0}
    assert components(np.array([a * 97 + b for a in range(97) for b in range(97) if (a < 40) == (b < 40)]), 97) == 2


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
    _selftest_design()
    tj = trainer_jobs(man)
    allj = [job(man, t, p, u, a) for t, p in TASKS for u in range(N_UNITS) for a in ARMS]
    assert len(tj) == len(ARMS) * N_UNITS * len(TASKS) == len(set(tj)) and sorted(tj) == sorted(allj) and tj != allj
    assert all("r12_raw" in j and "\\" not in j and "--stop-after-gen 8000" in j for j in tj) and tj == trainer_jobs(man)
    assert len({expected_run_id(shlex.split(j)) for j in tj}) == len(tj)
    j0 = job(man, "mul", 113, 0, "R")
    assert (expected_run_id(shlex.split(j0))
            == f"EXP-043_baseline_seed{init_seed('mul', 113, 0)}_thr1_r12_mul113_u0_R_mul113_devcuda"), expected_run_id(shlex.split(j0))
    assert "--p 113 --task mul" in j0 and "--test-file lab/confirm/r12_splits/r12_mul113_u0_test.npy" in j0 and "--steps 8000" in j0
    assert all(j.startswith("python lab/tools/confirm_r12.py --run M -- ") for j in BLOCK.jobs(man, "M"))
    BLOCK.check_job(man, shlex.split(tj[0]))
    try:
        BLOCK.check_job(man, shlex.split(tj[0]) + ["--force"])
        raise AssertionError("foreign command accepted")
    except SystemExit:
        pass
    # contrasts and verdict
    t = {a: (1000, True) for a in ARMS} | {"R": (CAP, False)}
    assert contrast(t, "H-ER")[1] == 1 and abs(contrast(t, "H-ER")[0] - math.log2(8)) < 1e-12 and contrast(t, "H-ED") == (0.0, None)
    assert contrast(t | {"E2_1": (CAP, False), "R": (1000, True)}, "H-ER") == (0.0, None)          # E2_1 never enters H-ER
    rng = np.random.default_rng(0)
    fast = {"R": 6000, "D_0": 3000, "D_1": 3000, "E2_0": 800, "E2_1": 800}
    names = [tname(t_, p_) for t_, p_ in TASKS]
    v = verdict({tn: _fake_rows(rng, N_UNITS, fast) for tn in names}, N_UNITS, rng)
    assert all(v[tn][h]["verdict"] == "bestätigt" for tn in names for h in HYPS), v
    v = verdict({names[0]: _fake_rows(rng, N_UNITS, fast), names[1]: _fake_rows(rng, N_UNITS, fast, d_copies_e=True)}, N_UNITS, rng)
    assert v[names[0]]["H-ED"]["verdict"] == "bestätigt" and v[names[1]]["H-ED"]["verdict"] == "nicht bestätigt"
    assert v[names[1]]["H-ED"]["p"] == 1.0 and v[names[1]]["H-ER"]["verdict"] == "bestätigt", v
    assert verdict({names[0]: _fake_rows(rng, N_UNITS, fast)}, N_UNITS, rng)["verdict"] == "nicht auswertbar"
    assert verdict({names[0]: _fake_rows(rng, N_UNITS, fast), names[1]: _fake_rows(rng, N_UNITS - 1, fast)}, N_UNITS, rng)["verdict"] \
        == "nicht auswertbar"
    tech = _fake_rows(rng, N_UNITS - 1, fast) + [{"unit": 19, "technical": True}]
    assert verdict({names[0]: _fake_rows(rng, N_UNITS, fast), names[1]: tech}, N_UNITS, rng)["verdict"] == "nicht auswertbar"
    _selftest_measure()
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    loaded = {Path(m.__file__).resolve().relative_to(ROOT.resolve()).as_posix() for m in list(sys.modules.values())
              if getattr(m, "__file__", None) and Path(m.__file__).resolve().is_relative_to((ROOT / "lab").resolve())}
    assert loaded <= set(CODE_FILES), sorted(loaded - set(CODE_FILES))
    print("[confirm_r12] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
