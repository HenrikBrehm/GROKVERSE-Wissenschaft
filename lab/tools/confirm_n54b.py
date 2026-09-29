"""N54b confirmation (session 47): does the lock-in half-point t_half under i.i.d. minibatch AdamW scale as (N/B)^alpha with alpha in
the square-root band [0.3, 0.7], at lr 1e-3 (H1, replication of EXP-108 on fresh seeds) and at lr 2e-3 (H2, second learning rate)?
Registration lab/confirm/N54B_REGISTRATION_DRAFT.md. Pilots: EXP-107/108 (lr 1e-3, seeds 3700-3707), EXP-109 (lr 2e-3, 3700-3701).

Protocol: add 113, the L0/EXP-100 split construction (EXP-053/P1 pair F/G, omega = 0, calibrated eps, targets drawn without the
stride-order frequencies O) with its own stream SeedSequence([100300, seed, 0]); per seed, lr and batch B in {1024, 256, 64} (no full-batch arm, s47: cost, and a
saturation towards full batch is expected under the sign-drift model):
pure runs F and G and switches F->G and G->F at every t of GRID[B]; every run 5000 steps (--stop-after-gen 5000), W_E snapshot at 5000.
pi(t) = mean over both directions of the normalised position of log(P_F/P_G) at step 5000 between the pure runs (EXP-107/108).
t_half = first upward crossing of 0.5 by linear interpolation of pi over (0, 0) and the grid; no crossing -> t_half = t_max,
censored. alpha per seed and lr = least-squares slope of log t_half against log(N/B) over the three batch sizes.
Validity: any technical failure -> the whole block 'nicht auswertbar' (infrastructure failures may be re-run with the identical job
line before --analyze). A seed is invalid for an lr if any pure pair at that lr has L_F - L_G < 0.5 (not technical, reported).
Family (Holm over H1, H2; alpha 0.05): per lr, TOST p = max(p(mean alpha > 0.3), p(mean alpha < 0.7)), one-sided t-tests;
confirmed = Holm-p < 0.05 and bootstrap 95 % CI within [0.3, 0.7] and <= 2 censored seeds per batch size. A hypothesis with fewer
than 8 valid seeds is 'nicht auswertbar' and enters Holm with p = 1 (conservative).
Secondary (no verdict): t_half per B and lr; ratio t_half(2e-3)/t_half(1e-3) per B; the EXP-108 point predictions for lr 1e-3
(1024 62, 256 127, 64 290).

  python lab/tools/confirm_n54b.py --hash-code | --splits M | --jobs M | --run M -- <cmd> | --analyze M | --selftest
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

RAW, BIND, SPL = LAB / "confirm/n54b_raw", LAB / "confirm/n54b_bindings", LAB / "confirm/n54b_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
CAL = LAB / "experiments/EXP-053-p3-overlap-design/calibration.json"
SALT, ALPHA, BAND, MIN_VALID, MAX_CENS, MIN_SEP = 100_300, 0.05, (0.3, 0.7), 8, 2, 0.5
O = (11, 12, 22, 23, 34, 45)
N_SEEDS = 10
TOTAL = 5000
LRS = (0.001, 0.002)
BATCHES = (1024, 256, 64)
GRID: dict[int, tuple[int, ...]] = {1024: (15, 30, 50, 75, 100, 150), 256: (30, 60, 100, 150, 200, 300),
                                    64: (75, 150, 225, 300, 450, 700)}   # set after EXP-109 (registration lists the pilot)
HYP = {"H1": 0.001, "H2": 0.002}
PRED_LR1 = {1024: 62.0, 256: 127.0, 64: 290.0}   # EXP-108 means (lr 1e-3), secondary comparison only
REGISTERED = {"seeds": list(range(3900, 3900 + N_SEEDS)), "budget": TOTAL, "device": "cuda", "threads": 1, "lrs": list(LRS),
              "batches": list(BATCHES), "grid": {str(b): list(t) for b, t in GRID.items()}, "order_freqs": list(O)}
CODE_FILES = ("lab/tools/confirm_n54b.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_splits.py",
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
        ov.targets = targets
        return ov.build(seed, 0.0, eps)
    finally:
        ov.targets = keep


def stem(s: int, a: str) -> str:
    return f"n54b_seed{s}_{a}"


def write_splits(man: dict) -> None:
    SPL.mkdir(parents=True, exist_ok=True)
    if any((SPL / f"{stem(s, a)}.npy").exists() for s in man["seeds"] for a in ("F", "G", "test")):
        raise SystemExit("N54b splits exist already: never overwrite")
    for s in man["seeds"]:
        d, (F, G) = build(s), targets(s)
        for a, key in (("F", "A"), ("G", "B"), ("test", "test")):
            with open(SPL / f"{stem(s, a)}.npy", "xb") as f:
                np.save(f, d[key].astype(np.int64))
        with open(SPL / f"n54b_seed{s}.json", "x", encoding="utf-8") as f:
            json.dump({"seed": s, "targets": {"F": F, "G": G}, "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(s: int) -> str | None:
    d, (F, G) = build(s), targets(s)
    for a, key in {"F": "A", "G": "B", "test": "test"}.items():
        f = SPL / f"{stem(s, a)}.npy"
        if not f.exists() or not np.array_equal(np.load(f), d[key].astype(np.int64)):
            return f"seed {s}: split {a} missing or differs from the rebuild"
    meta = json.loads((SPL / f"n54b_seed{s}.json").read_text(encoding="utf-8"))
    return None if meta.get("targets") == {"F": F, "G": G} else f"seed {s}: targets differ"


def job(man: dict, s: int, lr: float, bs: int, first: str, second: str | None = None, t: int | None = None) -> str:
    bud = man["budget"]
    spec = ",".join(str(x) for x in sorted({50, 250, 2000, 2500, bud} | ({t} if t else set())))
    out = (f"{c1.interp(man)} {FB} --seed {s} --condition baseline --threads {man['threads']} --device {man['device']} "
           f"--test-file lab/confirm/n54b_splits/{stem(s, 'test')}.npy --out-root lab/confirm/n54b_raw "
           f"--split-file lab/confirm/n54b_splits/{stem(s, first)}.npy --steps {bud} --stop-after-gen {bud} --spectra-at {spec}")
    if lr != 0.001:
        out += f" --lr {lr!r}"
    if bs:
        out += f" --batch-size {bs}"
    if second:
        out += f" --switch-split-file lab/confirm/n54b_splits/{stem(s, second)}.npy --switch-step {t}"
    return out


def trainer_jobs(man: dict) -> list[str]:
    out = []
    for s in man["seeds"]:
        for lr in man["lrs"]:
            for bs in man["batches"]:
                out += [job(man, s, lr, bs, x) for x in "FG"]
                for t in man["grid"][str(bs)]:
                    out += [job(man, s, lr, bs, a, b, t) for a, b in (("F", "G"), ("G", "F"))]
    return out


def expected_run_id(cmd: list[str]) -> str:
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    sw = g("--switch-split-file")
    rid = (f"EXP-020_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}_to_{Path(sw).stem}_at{g('--switch-step')}"
           if sw else f"EXP-018_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}")
    if g("--batch-size") and int(g("--batch-size")):
        rid += f"_bs{int(g('--batch-size'))}"
    if g("--lr"):
        rid += f"_lr{float(g('--lr'))!r}"
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


BLOCK = Block(name="confirm_n54b", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_n54b.py")


def one_run(man: dict, s: int, lr: float, bs: int, first: str, second: str | None = None, t: int | None = None) -> np.ndarray | str:
    cmd = shlex.split(job(man, s, lr, bs, first, second, t))
    d, tag = run_dir(cmd), f"seed {s} lr {lr} bs {bs} {first}{'->' + second + '@' + str(t) if second else ''}"
    sp, te = SPL / f"{stem(s, first)}.npy", SPL / f"{stem(s, 'test')}.npy"
    sw = SPL / f"{stem(s, second)}.npy" if second else None
    if not d.exists():
        return f"{tag}: fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt: {why}"
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=man["budget"], split_file=sp, test_file=te, switch_file=sw,
                           config={"p": 113, "task": "add", "lr": lr, "weight_decay": 1.0, "train_frac": 0.3, "beta1": 0.9, "beta2": 0.98},
                           snapshots_at=(man["budget"],)))
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    r = L.res
    if r.get("batch_size", 0) != bs or r.get("order", "iid") != "iid" or r.get("optimizer", "adamw") != "adamw":
        return f"{tag}: defekt: recorded batch/order/optimizer differ"
    if (why := BLOCK.unbound(man, d)) or r.get("fingerprint_fields", {}).get("split_file_sha256") != sha(sp):
        return f"{tag}: defekt after load: {why or 'split bytes differ'}"
    try:
        pw = a43().group_power(L.snapshot(man["budget"]), "add", 113)[0]
    except Exception as ex:   # any load/transform failure is technical, never an abort (as confirm_l0)
        return f"{tag}: defekt: {type(ex).__name__}: {ex}"
    return pw if np.isfinite(pw).all() and (pw > 0).all() else f"{tag}: defekt: non-finite or non-positive power"


def logratio(pw: np.ndarray, F: list[int], G: list[int]) -> float:
    return float(np.log(pw[[k - 1 for k in F]].sum() / pw[[k - 1 for k in G]].sum()))


def t_half(pi: dict[int, float]) -> tuple[float, bool]:
    ts = [0] + sorted(pi)
    ms = [0.0] + [pi[t] for t in sorted(pi)]
    for i in range(1, len(ts)):
        if ms[i - 1] < 0.5 <= ms[i]:
            return ts[i - 1] + (0.5 - ms[i - 1]) * (ts[i] - ts[i - 1]) / (ms[i] - ms[i - 1]), False
    return float(ts[-1]), True


def slope(nb: list[float], th: list[float]) -> float:
    return float(np.polyfit(np.log(nb), np.log(th), 1)[0])


def seed_lr(man: dict, s: int, lr: float, F: list[int], G: list[int], n_train: int) -> dict:
    """One seed at one lr: {'technical': reason} | {'invalid': reason} | pi, t_half, censoring and alpha per batch size."""
    out: dict = {"pi": {}, "th": {}, "cens": {}}
    for bs in man["batches"]:
        pure = {x: one_run(man, s, lr, bs, x) for x in "FG"}
        sw = {(a, t): one_run(man, s, lr, bs, a, b, t) for t in man["grid"][str(bs)] for a, b in (("F", "G"), ("G", "F"))}
        bad = [v for v in list(pure.values()) + list(sw.values()) if isinstance(v, str)]
        if bad:
            return {"technical": bad[0]}
        LF, LG = logratio(pure["F"], F, G), logratio(pure["G"], F, G)
        if LF - LG < MIN_SEP:
            out.setdefault("invalid", f"bs {bs}: pure runs not separated (L_F - L_G = {LF - LG:.3f})")
            continue
        pi = {t: ((logratio(sw[("F", t)], F, G) - LG) / (LF - LG) + (logratio(sw[("G", t)], F, G) - LF) / (LG - LF)) / 2
              for t in man["grid"][str(bs)]}
        out["pi"][bs], (out["th"][bs], out["cens"][bs]) = pi, t_half(pi)
    if "invalid" in out:
        return {"invalid": out["invalid"]}
    out["alpha"] = slope([n_train / bs for bs in man["batches"]], [out["th"][bs] for bs in man["batches"]])
    return out


def tost_p(a: np.ndarray) -> float:
    return max(c1.t_test_secondary(a - BAND[0])["p_one_sided"], c1.t_test_secondary(BAND[1] - a)["p_one_sided"])


def verdict(per_lr: dict[float, list[dict]], batches: list[int], rng_: np.random.Generator) -> dict:
    """per_lr[lr] = rows of seed_lr (one per seed). Technical failures anywhere -> 'nicht auswertbar'."""
    if any("technical" in r for rows in per_lr.values() for r in rows):
        return {"verdict": "nicht auswertbar", "n_technical": sum("technical" in r for rows in per_lr.values() for r in rows)}
    out: dict = {}
    p: dict[str, float] = {}
    for h, lr in HYP.items():
        ok = [r for r in per_lr[lr] if "invalid" not in r]
        a = np.array([r["alpha"] for r in ok])
        cens = {bs: int(sum(r["cens"][bs] for r in ok)) for bs in batches}
        d: dict = {"lr": lr, "n_valid": len(ok), "n_invalid": len(per_lr[lr]) - len(ok), "n_censored": cens}
        if len(ok) >= MIN_VALID:
            p[h] = tost_p(a)
            d.update({"alpha_mean": float(a.mean()), "alpha_sd": float(a.std(ddof=1)), "ci95": c1.boot_ci(a, rng_), "p_tost": p[h]})
        out[h] = d
    ph = c1.holm({h: p.get(h, 1.0) for h in HYP})    # review s47: an unevaluable hypothesis keeps its place in Holm with p = 1
    for h, d in out.items():
        d["p_holm"] = ph[h]
        if h not in p:
            d["verdict"] = "nicht auswertbar (zu wenige gültige Seeds)"
            continue
        inside = BAND[0] <= d["ci95"][0] and d["ci95"][1] <= BAND[1]
        d["verdict"] = ("bestätigt" if ph[h] < ALPHA and inside and max(d["n_censored"].values()) <= MAX_CENS else "nicht bestätigt")
    return out


def secondary(per_lr: dict[float, list[dict]], batches: list[int], rng_: np.random.Generator) -> dict:
    out: dict = {}
    for lr, rows in per_lr.items():
        ok = [r for r in rows if "invalid" not in r and "technical" not in r]
        if not ok:
            continue
        out[f"lr{lr!r}"] = {"t_half_mean": {str(bs): float(np.mean([r["th"][bs] for r in ok])) for bs in batches},
                            "pi_mean": {str(bs): {str(t): float(np.mean([r["pi"][bs][t] for r in ok])) for t in ok[0]["pi"][bs]} for bs in batches}}
    both = [(x, y) for x, y in zip(per_lr[LRS[0]], per_lr[LRS[1]]) if all("invalid" not in r and "technical" not in r for r in (x, y))]
    if both:
        out["ratio_lr2_over_lr1"] = {}
        for bs in batches:
            q = np.log([y["th"][bs] / x["th"][bs] for x, y in both])
            ci = c1.boot_ci(q, rng_)
            out["ratio_lr2_over_lr1"][str(bs)] = {"geo_mean": float(np.exp(q.mean())), "ci95": [float(np.exp(ci[0])), float(np.exp(ci[1]))], "n": len(both)}
    out["pred_lr1_exp108"] = {str(b): v for b, v in PRED_LR1.items()}
    return out


def analyze(manifest: Path) -> None:
    stale = LAB / "confirm" / "N54B_summary.json"
    if stale.exists():
        stale.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for m in (split_mismatch(s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"N54b splits differ from the registered construction: {bad[:3]}")
    per_lr: dict[float, list[dict]] = {lr: [] for lr in man["lrs"]}
    for s in man["seeds"]:
        meta = json.loads((SPL / f"n54b_seed{s}.json").read_text(encoding="utf-8"))
        n_train = int(len(np.load(SPL / f"{stem(s, 'F')}.npy")))
        for lr in man["lrs"]:
            r = seed_lr(man, s, lr, meta["targets"]["F"], meta["targets"]["G"], n_train)
            per_lr[lr].append({"seed": s, "n_train": n_train, **r})
    rng_ = np.random.default_rng(47)
    out = {"manifest_commit": man["commit"], "hypotheses": verdict(per_lr, man["batches"], rng_),
           "secondary": secondary(per_lr, man["batches"], rng_), "rows": {repr(lr): rows for lr, rows in per_lr.items()}}
    (LAB / "confirm/N54B_summary.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False, default=float))


def _fake_row(alpha: float, rng_: np.random.Generator, n_train: int = 3831, cens: bool = False) -> dict:
    th = {bs: 30.0 * (n_train / bs) ** alpha * float(np.exp(rng_.normal(0, 0.05))) for bs in BATCHES}
    return {"th": th, "cens": {bs: cens for bs in BATCHES}, "pi": {bs: {t: 0.5 for t in GRID[bs]} for bs in BATCHES},
            "alpha": slope([n_train / bs for bs in BATCHES], [th[bs] for bs in BATCHES])}


def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    tj = trainer_jobs(man)
    n_per = sum(2 + 2 * len(GRID[b]) for b in BATCHES)
    assert len(tj) == N_SEEDS * len(LRS) * n_per and len(set(tj)) == len(tj), len(tj)
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert len(set(ids)) == len(ids), "run ids collide"
    assert ids[0] == "EXP-018_baseline_seed3900_thr1_n54b_seed3900_F_bs1024_devcuda", ids[0]
    sw2 = [i for i in ids if "_to_" in i and "_lr0.002" in i and "_bs64" in i][0]
    assert sw2.startswith("EXP-020_baseline_seed3900_thr1_n54b_seed3900_F_to_n54b_seed3900_G_at75_bs64_lr0.002"), sw2
    BLOCK.check_job(man, shlex.split(tj[0]))
    for s in REGISTERED["seeds"][:2]:
        F, G = targets(s)
        assert not set(F) & set(G) and not (set(F) | set(G)) & set(O)
    assert t_half({10: 0.2, 20: 0.8}) == (15.0, False) and t_half({10: 0.1, 20: 0.3}) == (20.0, True)
    assert t_half({10: 0.6}) == (10 * 0.5 / 0.6, False)
    rng_ = np.random.default_rng(0)
    yes = {lr: [_fake_row(0.52, rng_) for _ in range(N_SEEDS)] for lr in LRS}
    v = verdict(yes, list(BATCHES), rng_)
    assert v["H1"]["verdict"] == v["H2"]["verdict"] == "bestätigt", v
    epoch = {LRS[0]: [_fake_row(0.95, rng_) for _ in range(N_SEEDS)], LRS[1]: [_fake_row(0.5, rng_) for _ in range(N_SEEDS)]}
    v = verdict(epoch, list(BATCHES), rng_)
    assert v["H1"]["verdict"] == "nicht bestätigt" and v["H2"]["verdict"] == "bestätigt", v
    few = {LRS[0]: yes[LRS[0]], LRS[1]: [{"invalid": "x"}] * 3 + yes[LRS[1]][:7]}
    v = verdict(few, list(BATCHES), rng_)
    assert v["H2"]["verdict"].startswith("nicht auswertbar") and v["H2"]["p_holm"] == 1.0, v
    assert v["H1"]["verdict"] == "bestätigt" and v["H1"]["p_holm"] == min(1.0, 2 * v["H1"]["p_tost"]), v   # Holm keeps k = 2
    cens = {lr: [_fake_row(0.52, rng_, cens=i < 3) for i in range(N_SEEDS)] for lr in LRS}
    assert verdict(cens, list(BATCHES), rng_)["H1"]["verdict"] == "nicht bestätigt"
    tech = {LRS[0]: [{"technical": "x"}] + yes[LRS[0]][1:], LRS[1]: yes[LRS[1]]}
    assert verdict(tech, list(BATCHES), rng_)["verdict"] == "nicht auswertbar"
    sec = secondary(yes, list(BATCHES), rng_)
    assert 0.9 < sec["ratio_lr2_over_lr1"]["64"]["geo_mean"] < 1.1, sec["ratio_lr2_over_lr1"]
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    print("[confirm_n54b] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
