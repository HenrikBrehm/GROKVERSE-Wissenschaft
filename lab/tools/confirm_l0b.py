"""L0b confirmation (rule 20b, LeDoux 2026 conflict): set composition against a fixed data order in the LONG-EPOCH regime.
Registration lab/confirm/L0b_REGISTRATION.md (session 63, 2026-09-30). Pilot: EXP-106 (seeds 3700-3707, SEEN; sample size from its
spread: lab/confirm/L0b_power_s63.py -> 64). Trainer freq_ban.py unchanged (options --batch-size/--order/--weight-decay exist).

Protocol: add 113; per seed the EXP-100 construction with its OWN streams SeedSequence([100300, seed, purpose]): engineered pair
F/G as EXP-053/P1 (omega = 0, calibrated eps) with target sets drawn WITHOUT the stride-order frequencies O (purpose 0), and a
uniform random split R of the same size from the same pool (purpose 1), common test set. Arms, all AdamW lr 1e-3, weight decay
0.1, batch 16 (240 steps per epoch), 30 000 steps (--stop-after-gen = budget), GPU:
  iid16w     i.i.d. order     on F, G and R
  stride16w  stride order     on F, G and R          -> 6 runs per seed
Per run (final W_E group power, EXP-043 basis): o = share of the power on O; t_gen = first step with test accuracy >= 0.95
(trainer transitions, primary), censored at the budget if never reached.
Family (Holm over H1-H4, alpha 0.05; confirmed = Holm-p < 0.05 AND the bootstrap-CI rule; bootstrap over seeds, 10 000, rng 21):
  H1 order acts where the set gives little:  x = o(R, stride16w) - o(R, iid16w);             one-sided t, mean > 0;   CI lower > 0
  H2 the set wins on engineered splits:     x = mean_FG [o(stride16w) - o(iid16w)];         TOST |mean| < DELTA = 0.02
                                            (p = max of the two one-sided t p-values);      95 % CI inside (-DELTA, DELTA)
  H3 steering not reduced by the order:     x = Delta_pow(stride16w) - Delta_pow(iid16w);   non-inferiority, mean > -H3_MARGIN
                                            (H3_MARGIN = 2, about 20 % of the pilot's 9.2); CI lower > -H3_MARGIN
  H4 the order costs time on engineered:    x = mean_FG log2 t_gen(stride16w) / t_gen(iid16w); one-sided t, mean > 0; CI lower > 0
Descriptive: Delta_pow per arm, o per arm and split at the end and at step 10 000, runs that never generalise per arm and
split (and pairs where only one side is censored, by side), peak-in-O fractions, Spearman of o(R, iid16w) against x_H1.
Streams: SALT 100300 drives the target draw and R only; test set, phases and keys come from overlap_split (salt 53001, keyed by
seed), as in L0 and EXP-100 - fresh because the seeds are fresh.
Validity: any technical failure -> the whole block 'nicht auswertbar' (as L0); a run that never generalises is NOT technical.
Pure infrastructure failures may be re-run with the identical job line before --analyze (registration).

  python lab/tools/confirm_l0b.py --hash-code | --splits M | --jobs M | --run M -- <cmd> | --analyze M | --selftest
"""
from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "experiments/EXP-053-p3-overlap-design"))
import confirm_p1 as c1  # noqa: E402
from bound_block import Block, selftest_binding, sha  # noqa: E402
import overlap_split as ov  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

RAW, BIND, SPL = LAB / "confirm/l0b_raw", LAB / "confirm/l0b_bindings", LAB / "confirm/l0b_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
CAL = LAB / "experiments/EXP-053-p3-overlap-design/calibration.json"
SALT, ALPHA, DELTA, H3_MARGIN = 100_300, 0.05, 0.02, 2.0
O = (11, 12, 22, 23, 34, 45)                   # stride-order frequencies for p = 113 (EXP-100)
N_SEEDS = 70                                    # L0b_power_s63.py: H1 needs 63; review s63: all free seeds 3730-3799
BUDGET, WD, BS = 30_000, 0.1, 16
ARMS = {"iid16w": "iid", "stride16w": "stride"}
SPLITS = ("F", "G", "R")
REGISTERED = {"seeds": list(range(3730, 3730 + N_SEEDS)), "budget": BUDGET, "device": "cuda", "threads": 1, "batch_size": BS,
              "weight_decay": WD, "arms": dict(ARMS), "order_freqs": list(O), "delta_equiv": DELTA, "h3_margin": H3_MARGIN, "o_mid_step": 10_000}
CODE_FILES = ("lab/tools/confirm_l0b.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_splits.py",
              "lab/tools/result_loader.py", "lab/tools/trainer_guard.py", "lab/tools/paket_a_device.py",
              "lab/experiments/EXP-001-freq-ban/freq_ban.py", "lab/experiments/EXP-053-p3-overlap-design/overlap_split.py",
              "lab/experiments/EXP-053-p3-overlap-design/calibration.json",
              "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-043-generalize-steering/analyze.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py")


def rng(seed: int, purpose: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([SALT, seed, purpose]))


def targets(seed: int) -> tuple[list[int], list[int]]:
    ks = rng(seed, 0).permutation([k for k in range(1, (ov.P - 1) // 2 + 1) if k not in O])
    return sorted(int(k) for k in ks[:ov.M]), sorted(int(k) for k in ks[ov.M:2 * ov.M])


def build(seed: int) -> dict:
    eps = json.loads(CAL.read_text(encoding="utf-8"))["levels"]["0.0"]["eps"]
    keep = ov.targets
    try:
        ov.targets = targets                    # same construction as P1/EXP-053/EXP-100, only the target draw excludes O
        d = ov.build(seed, 0.0, eps)
    finally:
        ov.targets = keep
    pool = np.setdiff1d(np.arange(ov.P * ov.P), d["test"])
    d["R"] = np.sort(rng(seed, 1).choice(pool, ov.N_TRAIN, replace=False))
    return d


KEYS = {"F": "A", "G": "B", "R": "R", "test": "test"}


def stem(s: int, a: str) -> str:
    return f"l0b_seed{s}_{a}"


def write_splits(man: dict) -> None:
    SPL.mkdir(parents=True, exist_ok=True)
    if any((SPL / f"{stem(s, a)}.npy").exists() for s in man["seeds"] for a in KEYS):
        raise SystemExit("L0b splits exist already: never overwrite")
    for s in man["seeds"]:
        d, (F, G) = build(s), targets(s)
        assert not set(F) & set(G) and not (set(F) | set(G)) & set(O)
        for a, key in KEYS.items():
            if a != "test":
                assert len(d[key]) == ov.N_TRAIN and not np.intersect1d(d[key], d["test"]).size
            with open(SPL / f"{stem(s, a)}.npy", "xb") as f:
                np.save(f, d[key].astype(np.int64))
        with open(SPL / f"l0b_seed{s}.json", "x", encoding="utf-8") as f:
            json.dump({"seed": s, "targets": {"F": F, "G": G}, "order_freqs": list(O), "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(s: int) -> str | None:
    d, (F, G) = build(s), targets(s)
    for a, key in KEYS.items():
        f = SPL / f"{stem(s, a)}.npy"
        if not f.exists() or not np.array_equal(np.load(f), d[key].astype(np.int64)):
            return f"seed {s}: split {a} missing or differs from the rebuild"
    meta = json.loads((SPL / f"l0b_seed{s}.json").read_text(encoding="utf-8"))
    return None if meta.get("targets") == {"F": F, "G": G} else f"seed {s}: targets differ"


def spec_steps(bud: int) -> str:
    return ",".join(str(x) for x in sorted({50, 250, 2000, bud} | set(range(2500, bud + 1, 2500))))


def trainer_jobs(man: dict) -> list[str]:
    out, bud = [], man["budget"]
    for s in man["seeds"]:
        for arm, order in man["arms"].items():
            for a in SPLITS:
                out.append(f"{c1.interp(man)} {FB} --seed {s} --condition baseline --threads {man['threads']} --device {man['device']} "
                           f"--test-file lab/confirm/l0b_splits/{stem(s, 'test')}.npy --out-root lab/confirm/l0b_raw "
                           f"--split-file lab/confirm/l0b_splits/{stem(s, a)}.npy --steps {bud} --stop-after-gen {bud} "
                           f"--spectra-at {spec_steps(bud)} --weight-decay {man['weight_decay']} --batch-size {man['batch_size']}"
                           + (f" --order {order}" if order != "iid" else ""))
    return out


def expected_run_id(cmd: list[str]) -> str:
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    rid = f"EXP-018_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}"
    if g("--batch-size") and int(g("--batch-size")):
        rid += f"_bs{int(g('--batch-size'))}"
    if g("--order") and g("--order") != "iid":
        rid += f"_ord{g('--order')}"
    if g("--weight-decay") is not None:
        rid += f"_wd{float(g('--weight-decay'))!r}"
    dev = g("--device") or "cpu"
    return rid + ("" if dev == "cpu" else f"_dev{dev.replace(':', '')}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


_a43 = None


def a43():
    global _a43
    if _a43 is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("exp043_analyze", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
        _a43 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_a43)
    return _a43


BLOCK = Block(name="confirm_l0b", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_l0b.py")


def one_run(man: dict, s: int, a: str, order: str) -> dict | str:
    sp, te = SPL / f"{stem(s, a)}.npy", SPL / f"{stem(s, 'test')}.npy"
    cmd = ["x", FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", man["device"], "--split-file", str(sp),
           "--batch-size", str(man["batch_size"]), "--weight-decay", str(man["weight_decay"])] + (["--order", order] if order != "iid" else [])
    d, tag = run_dir(cmd), f"seed {s} {a} {order}"
    if not d.exists():
        return f"{tag}: fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt: {why}"
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=man["budget"], split_file=sp, test_file=te,
                           config={"p": 113, "task": "add", "lr": 1e-3, "weight_decay": man["weight_decay"], "train_frac": 0.3,
                                   "beta1": 0.9, "beta2": 0.98},
                           snapshots_at=(man["o_mid_step"], man["budget"])))
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    r = L.res
    if r.get("batch_size") != man["batch_size"] or r.get("order", "iid") != order or r.get("optimizer", "adamw") != "adamw":
        return f"{tag}: defekt: recorded batch/order/optimizer differ"
    if r.get("events", {}).get("minibatch", {}).get("batch_size") != man["batch_size"]:
        return f"{tag}: defekt: minibatch event missing"
    if (why := BLOCK.unbound(man, d)) or r.get("fingerprint_fields", {}).get("split_file_sha256") != sha(sp):
        return f"{tag}: defekt after load: {why or 'split bytes differ'}"
    try:
        pw = a43().group_power(L.snapshot(man["budget"]), "add", 113)[0]
        pw_mid = a43().group_power(L.snapshot(man["o_mid_step"]), "add", 113)[0]
    except Exception as ex:   # any load/transform failure is technical, never an abort (as confirm_l0)
        return f"{tag}: defekt: {type(ex).__name__}: {ex}"
    if not np.isfinite(pw).all() or pw.sum() <= 0 or not np.isfinite(pw_mid).all() or pw_mid.sum() <= 0:
        return f"{tag}: defekt: non-finite power"
    gen = (r.get("transitions") or {}).get("primary", {}).get("generalization", {}).get("first_crossing_step")
    return {"pw": pw, "pw_mid": pw_mid, "t_gen": gen}


def o_share(pw: np.ndarray) -> float:
    return float(pw[[k - 1 for k in O]].sum() / pw.sum())


def peak_in_o(pw: np.ndarray) -> bool:
    return int(np.argmax(pw)) + 1 in O


def seed_row(man: dict, s: int, F: list[int], G: list[int], loader=None) -> dict:
    loader = loader or (lambda s_, a_, o_: one_run(man, s_, a_, o_))
    row: dict = {"seed": s, "technical": False}
    runs = {}
    for arm, order in man["arms"].items():
        for a in SPLITS:
            v = loader(s, a, order)
            if isinstance(v, str):
                row["technical"], row["reason"] = True, v
                return row
            runs[(arm, a)] = v
    bud = man["budget"]
    for arm in man["arms"]:
        d = c1.delta_pow_checked(runs[(arm, "F")]["pw"], runs[(arm, "G")]["pw"], F, G)
        if d is None:
            row["technical"], row["reason"] = True, f"{arm}: dpow not finite or a target power sum <= 0"
            return row
        row[f"dpow_{arm}"] = d
        row[f"o_FG_{arm}"] = (o_share(runs[(arm, "F")]["pw"]) + o_share(runs[(arm, "G")]["pw"])) / 2
        row[f"o_R_{arm}"] = o_share(runs[(arm, "R")]["pw"])
        row[f"o_mid_{arm}"] = {a: o_share(runs[(arm, a)]["pw_mid"]) for a in SPLITS}
        row[f"peakO_{arm}"] = {a: peak_in_o(runs[(arm, a)]["pw"]) for a in SPLITS}
        row[f"tgen_{arm}"] = {a: runs[(arm, a)]["t_gen"] for a in SPLITS}
    cens = lambda t: float(t) if t else float(bud)   # noqa: E731  (never generalised -> censored at the budget, not technical)
    row["x_H1"] = row["o_R_stride16w"] - row["o_R_iid16w"]
    row["x_H2"] = row["o_FG_stride16w"] - row["o_FG_iid16w"]
    row["x_H3"] = row["dpow_stride16w"] - row["dpow_iid16w"]
    row["x_H4"] = float(np.mean([np.log2(cens(row["tgen_stride16w"][a]) / cens(row["tgen_iid16w"][a])) for a in "FG"]))
    return row


def spearman(u: np.ndarray, v: np.ndarray) -> float:
    rk = lambda w: np.argsort(np.argsort(w)).astype(float)   # noqa: E731  (ties are measure-zero for continuous shares)
    return float(np.corrcoef(rk(u), rk(v))[0, 1])


def p_value(h: str, x: np.ndarray) -> float:
    t = lambda y: c1.t_test_secondary(y)["p_one_sided"]   # noqa: E731
    if h == "H2":
        return max(t(x + DELTA), t(DELTA - x))            # TOST: mean > -DELTA and mean < DELTA
    return t(x + H3_MARGIN) if h == "H3" else t(x)


def ci_ok(h: str, ci: list[float]) -> bool:
    return {"H1": ci[0] > 0, "H2": -DELTA < ci[0] and ci[1] < DELTA, "H3": ci[0] > -H3_MARGIN, "H4": ci[0] > 0}[h]


def verdict(rows: list[dict], n_planned: int, rng_: np.random.Generator) -> dict:
    n_tech = sum(1 for r in rows if r.get("technical"))
    if n_tech or len(rows) != n_planned:
        return {"n_technical": n_tech, "verdict": "nicht auswertbar"}
    X = {h: np.array([r[f"x_{h}"] for r in rows], dtype=float) for h in ("H1", "H2", "H3", "H4")}
    p = {h: p_value(h, x) for h, x in X.items()}
    ph = c1.holm(p)
    out: dict = {"n": len(rows)}
    for h, x in X.items():
        ci = c1.boot_ci(x, rng_)
        out[h] = {"mean": float(x.mean()), "ci95": ci, "n_positive": int((x > 0).sum()), "p": p[h], "p_holm": ph[h],
                  "verdict": "bestätigt" if ph[h] < ALPHA and ci_ok(h, ci) else "nicht bestätigt"}
    out["descriptive"] = {
        "dpow_iid16w": {"mean": float(np.mean([r["dpow_iid16w"] for r in rows])), "ci95": c1.boot_ci(np.array([r["dpow_iid16w"] for r in rows]), rng_)},
        "o_mean": {f"{k}_{arm}": float(np.mean([r[f"o_{k}_{arm}"] for r in rows])) for k in ("FG", "R") for arm in ARMS},
        "peak_in_O_fraction": {f"{a}_{arm}": float(np.mean([r[f"peakO_{arm}"][a] for r in rows])) for a in SPLITS for arm in ARMS},
        "never_generalised": {f"{a}_{arm}": int(sum(r[f"tgen_{arm}"][a] is None for r in rows)) for a in SPLITS for arm in ARMS},
        "censored_only": {side: int(sum((r[f"tgen_{side}"][a] is None) and (r[f"tgen_{other}"][a] is not None) for r in rows for a in "FG"))
                          for side, other in (("stride16w", "iid16w"), ("iid16w", "stride16w"))},
        "dpow_stride16w": {"mean": float(np.mean([r["dpow_stride16w"] for r in rows]))},
        "o_mid_mean": {f"{a}_{arm}": float(np.mean([r[f"o_mid_{arm}"][a] for r in rows])) for a in SPLITS for arm in ARMS},
        "spearman_oR_iid_vs_xH1": spearman(np.array([r["o_R_iid16w"] for r in rows]), np.array([r["x_H1"] for r in rows]))}
    return out


def analyze(manifest: Path) -> None:
    stale = LAB / "confirm" / "L0b_summary.json"
    if stale.exists():
        stale.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for m in (split_mismatch(s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"L0b splits differ from the registered construction: {bad[:3]}")
    rows = []
    for s in man["seeds"]:
        meta = json.loads((SPL / f"l0b_seed{s}.json").read_text(encoding="utf-8"))
        rows.append(seed_row(man, s, meta["targets"]["F"], meta["targets"]["G"]))
    out = {"manifest_commit": man["commit"], "hypotheses": verdict(rows, len(man["seeds"]), np.random.default_rng(21)),
           "rows": [{k: v for k, v in r.items()} for r in rows]}
    (LAB / "confirm/L0b_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    tj = trainer_jobs(man)
    assert len(tj) == N_SEEDS * 6 and len(set(tj)) == len(tj)
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert len(set(ids)) == len(ids), "run ids collide"
    assert ids[0] == "EXP-018_baseline_seed3730_thr1_l0b_seed3730_F_bs16_wd0.1_devcuda", ids[0]
    assert ids[3] == "EXP-018_baseline_seed3730_thr1_l0b_seed3730_F_bs16_ordstride_wd0.1_devcuda", ids[3]
    BLOCK.check_job(man, shlex.split(tj[0]))
    for s in REGISTERED["seeds"][:3]:
        F, G = targets(s)
        assert not set(F) & set(G) and not (set(F) | set(G)) & set(O)
        d = build(s)
        assert len(d["R"]) == len(d["A"]) == ov.N_TRAIN and not np.intersect1d(d["R"], d["test"]).size
    assert targets(3730) != targets(3731)
    # the same seed under the EXP-100 salt must give other splits (fresh streams)
    keep = SALT
    try:
        globals()["SALT"] = 100_100
        old = targets(3730)
    finally:
        globals()["SALT"] = keep
    assert old != targets(3730)
    # synthetic verdicts through seed_row (fake loader) and verdict
    rng_ = np.random.default_rng(0)

    def fake(order_on_R: float, order_on_FG: float, delay: float):
        def loader(s, a, order):
            F, G = targets(s)
            pw = np.ones(56) + rng_.random(56) * 0.05
            if a in "FG":
                pw[[k - 1 for k in (F if a == "F" else G)]] += 10
            if order == "stride":
                pw[[k - 1 for k in O]] += order_on_R if a == "R" else order_on_FG
            t = int(4000 * (2 ** (delay + rng_.normal(0, 0.2)) if order == "stride" else 1))
            return {"pw": pw, "pw_mid": pw, "t_gen": t}
        return loader
    rows = [seed_row(man, s, *targets(s), loader=fake(2.0 + rng_.normal(0, 0.5), 0.0, 0.7)) for s in REGISTERED["seeds"]]
    v = verdict(rows, N_SEEDS, rng_)
    assert all(v[h]["verdict"] == "bestätigt" for h in ("H1", "H2", "H3", "H4")), v
    rows = [seed_row(man, s, *targets(s), loader=fake(rng_.normal(0, 0.5), 3.0, 0.0)) for s in REGISTERED["seeds"]]
    v = verdict(rows, N_SEEDS, rng_)
    assert v["H1"]["verdict"] == v["H2"]["verdict"] == v["H4"]["verdict"] == "nicht bestätigt", v
    assert v["descriptive"]["censored_only"] == {"stride16w": 0, "iid16w": 0}
    # H3 non-inferiority: stride steering 3 units weaker than iid fails, equal passes
    base = [{"x_H1": 0.1, "x_H2": 0.0, "x_H3": -3.0 + rng_.normal(0, 0.3), "x_H4": 0.5} for _ in range(N_SEEDS)]
    assert p_value("H3", np.array([b_["x_H3"] for b_ in base])) > 0.5
    assert p_value("H3", np.array([b_["x_H3"] + 3.0 for b_ in base])) < 1e-6
    # a never-generalising stride run is censored, not technical
    r = seed_row(man, 3730, *targets(3730), loader=lambda s, a, o: {"pw": np.ones(56) + np.arange(56) * 0.01, "pw_mid": np.ones(56), "t_gen": None if o == "stride" else 5000})
    assert not r["technical"] and abs(r["x_H4"] - np.log2(BUDGET / 5000)) < 1e-12, r
    # one missing run -> technical -> whole block not evaluable
    r = seed_row(man, 3730, *targets(3730), loader=lambda s, a, o: "x: fehlt" if a == "R" else {"pw": np.ones(56), "pw_mid": np.ones(56), "t_gen": 1})
    assert r["technical"]
    assert verdict([r] + rows[1:], N_SEEDS, rng_)["verdict"] == "nicht auswertbar"
    assert verdict(rows[:-1], N_SEEDS, rng_)["verdict"] == "nicht auswertbar"
    # TOST: exact zero effect with spread is equivalent, a shift of 2 DELTA is not
    z = np.random.default_rng(1).normal(0, 0.01, 64)
    assert p_value("H2", z) < 1e-6 and p_value("H2", z + 2 * DELTA) > 0.5
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    print("[confirm_l0b] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
