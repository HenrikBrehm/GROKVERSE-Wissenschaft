"""P1 confirmation (FINDINGS "Programm"): job list and frozen analysis for the reserved block. Session 14, UNTESTED.

P1: engineered splits raise the target power in W_E, Delta_pow > 0 on fresh seeds and splits, minimum effect Delta_pow >= 1.
Primary per task in the manifest: mean Delta_pow over seeds, one-sided sign-flip test of mean > 0 (exact for n <= 20, else
Monte Carlo), 95 % bootstrap CI of the mean; with manifest 'primary_task' only that task enters the P1-P3 Holm family (FAMILY = 3,
missing members p = 1) and the other tasks form a secondary Holm family (session 20, Codex B2; see family_adjust).
"confirmed" for a task needs ALL planned pairs valid, Holm-p < 0.05 AND the lower CI bound >= MIN_EFFECT (session 20, Codex B4/H3).
Runs: transformer of the study (freq_ban.py, add/mul) or group_train.py (D_n), 2000 steps, device from the manifest.

  python lab/tools/confirm_p1.py --jobs lab/confirm/P1_manifest.json > lab/confirm/P1_jobs.txt     # for parallel_queue.py
  python lab/tools/confirm_p1.py --analyze lab/confirm/P1_manifest.json                             # under guarded_run.py
  python lab/tools/confirm_p1.py --selftest
Extra manifest fields: "device": "cuda"|"cpu", "python": ".venv-gpu/Scripts/python.exe", "threads": 1.

Optional "cross": {"task": "add", "p": 113, "seeds": [...], "inits_per_seed": 2} (Astra point 5, session 16, UNTESTED): the SAME
F/G split files of these seeds are trained again with extra inits cross_init(s, r) = s + 200 + 100 r (reserved 1200-1399).
Secondary and descriptive only, not in the Holm family; the primary P1 test keeps one Delta per seed (repeated inits of the same
split are no independent split replications). Reading, fixed before any run: see cross_block().
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools"))
from confirm_splits import OUT as SPLITS, build, check_manifest  # noqa: E402
from result_loader import Expect, find_run, load_run  # noqa: E402

STEP, ALPHA, FAMILY, MIN_EFFECT, N_BOOT, N_MC = 2000, 0.05, 3, 1.0, 10_000, 200_000
RAW = LAB / "confirm" / "raw"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
GT = "lab/experiments/EXP-046-dihedral-steering/group_train.py"


def stem(man: dict, t: dict, s: int, arm: str) -> str:
    return f"confirm_exp{int(man['experiment'])}_eps{float(man['eps'])}_{t['task']}{t['p']}_seed{s}_{arm}"


def cross_init(s: int, r: int) -> int:
    return s + 200 + 100 * r


def cross_spec(man: dict) -> dict | None:
    c = man.get("cross")
    if c is None:
        return None
    t = {"task": c["task"], "p": int(c["p"])}
    if t not in [{"task": x["task"], "p": int(x["p"])} for x in man["tasks"]] or t["task"] == "D":
        raise SystemExit("cross: task must be a non-D task of the manifest")
    if not set(c["seeds"]) <= set(man["seeds"]) or not all(1000 <= s <= 1099 for s in c["seeds"]):
        raise SystemExit("cross: seeds must be manifest seeds in 1000-1099")
    if not 1 <= int(c["inits_per_seed"]) <= 2:            # keeps cross_init inside the reserved 1200-1399
        raise SystemExit("cross: inits_per_seed must be 1 or 2")
    return {"t": t, "seeds": list(c["seeds"]), "R": int(c["inits_per_seed"])}


def interp(man: dict) -> str:
    """Session 20: Windows CreateProcess cannot find a RELATIVE path with forward slashes (.venv-gpu/Scripts/python.exe);
    an absolute forward-slash path works and survives parallel_queue's no-backslash rule for job lines."""
    py = str(man["python"])
    if ("/" in py or "\\" in py) and not Path(py).is_absolute():
        return (LAB.parent / py).as_posix()
    return py


def fb_job(man: dict, t: dict, init: int, sp: str) -> str:
    return (f"{interp(man)} {FB} --seed {init} --condition baseline --steps {STEP} --threads {man['threads']} "
            f"--device {man['device']} --p {t['p']} --task {t['task']} --split-file {sp} "
            f"--spectra-at 250,500,1000,{STEP} --out-root lab/confirm/raw")


def jobs(man: dict) -> list[str]:
    out = []
    for t in man["tasks"]:
        for s in man["seeds"]:
            for arm in "FG":
                sp = f"lab/confirm/splits/{stem(man, t, s, arm)}.npy"
                if t["task"] == "D":
                    out.append(f"{interp(man)} {GT} --seed {s} --n {t['p']} --steps {STEP} --device {man['device']} --split-file {sp} "
                               f"--out-root lab/confirm/raw")
                else:
                    out.append(fb_job(man, t, s, sp))
    c = cross_spec(man)
    if c is not None:
        for s in c["seeds"]:
            for r in range(c["R"]):
                for arm in "FG":
                    out.append(fb_job(man, c["t"], cross_init(s, r), f"lab/confirm/splits/{stem(man, c['t'], s, arm)}.npy"))
    return out


def power_at(man: dict, t: dict, s: int, arm: str, init: int | None = None) -> np.ndarray | str:
    """W_E group power at STEP of the run on the split of (seed s, arm); init defaults to s (primary runs)."""
    st = stem(man, t, s, arm)
    init = s if init is None else init
    split = SPLITS / f"{st}.npy"
    dev = man["device"]
    if t["task"] == "D":
        L = load_run(find_run(RAW, f"EXP-046_seed{s}_{st}_dev{dev}"),
                     Expect(seed=s, device=dev, max_steps=STEP, split_file=split, config={"p": 2 * t["p"], "group": f"D{t['p']}"},
                            at=(STEP,)))
        return L.spectrum(STEP) if L.status == "ok" else f"{L.status}: {L.reason}"
    suffix = "" if (t["task"], t["p"]) == ("add", 113) else f"_{t['task']}{t['p']}"
    devsuf = "" if dev == "cpu" else f"_dev{dev}"            # freq_ban: CPU run-ids carry no device suffix
    L = load_run(find_run(RAW, f"EXP-0*_baseline_seed{init}_thr*_{st}{suffix}{devsuf}"),
                 Expect(seed=init, device=dev, max_steps=STEP, split_file=split, config={"p": t["p"], "task": t["task"]},
                        snapshots_at=(STEP,)))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
    from analyze import group_power                       # EXP-043 group-basis power (add 113 = plain DFT, k = 1..56)
    return group_power(L.snapshot(STEP), t["task"], t["p"])[0]


def delta_pow(pF: np.ndarray, pG: np.ndarray, F: list[int], G: list[int]) -> float:
    s = lambda pw, S: float(pw[[k - 1 for k in S]].sum())   # noqa: E731
    return float(np.log(s(pF, F) / s(pF, G)) + np.log(s(pG, G) / s(pG, F)))


def delta_pow_checked(pF: np.ndarray, pG: np.ndarray, F: list[int], G: list[int]) -> float | None:
    """Session 20 (Codex B4): None if a target sum is not positive or the result is not finite (row then invalid)."""
    sums = [float(pw[[k - 1 for k in S]].sum()) for pw in (pF, pG) for S in (F, G)]
    if not all(np.isfinite(x) and x > 0 for x in sums):
        return None
    d = delta_pow(pF, pG, F, G)
    return d if np.isfinite(d) else None


def split_mismatch(man: dict, t: dict, s: int, arm: str) -> str | None:
    """Session 20 (Codex H6): rebuild the split deterministically and require exact equality of indices and targets."""
    st = stem(man, t, s, arm)
    idx, T = build(int(man["experiment"]), t["task"], t["p"], s, arm, float(man["eps"]))
    meta = json.loads((SPLITS / f"{st}.json").read_text(encoding="utf-8"))
    if not np.array_equal(np.load(SPLITS / f"{st}.npy"), idx):
        return f"{arm}: split indices differ from build()"
    if list(meta["targets"]) != list(T) or meta.get("arm") != arm or int(meta.get("seed", -1)) != s:
        return f"{arm}: split metadata differs from build()"
    return None


def family_adjust(ps: dict[str, float], primary: str | None) -> dict[str, float]:
    """Session 20 (Codex B2). With 'primary_task' (e.g. "add113"): that task is P1 and enters the P1-P3 Holm family
    (FAMILY = 3, P2/P3 as p = 1 placeholders until they exist); all other tasks form a separate SECONDARY Holm family (P1b).
    Without it (old behaviour): every task plus FAMILY - 1 placeholders in one family."""
    if primary is None:
        return holm({**ps, **{f"_other{i}": 1.0 for i in range(FAMILY - 1)}})
    if primary not in ps:
        raise SystemExit(f"primary_task {primary} is not a manifest task")
    main_ = holm({primary: ps[primary], **{f"_other{i}": 1.0 for i in range(FAMILY - 1)}})
    sec = {k: v for k, v in ps.items() if k != primary}
    return {primary: main_[primary], **(holm(sec) if sec else {})}


def task_verdict(v: dict) -> str:
    """Session 20 (Codex B4/H3): all planned pairs valid, Holm-p < ALPHA AND the CI lower bound >= MIN_EFFECT."""
    if "p" not in v:
        return "nicht auswertbar"
    return "bestätigt" if v["p_holm_worstcase"] < ALPHA and v["ci95"][0] >= MIN_EFFECT else "nicht bestätigt"


def sign_flip_p(d: np.ndarray, rng: np.random.Generator) -> float:
    if len(d) <= 20:
        flips = np.array(list(itertools.product((1.0, -1.0), repeat=len(d))))
        return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())
    flips = rng.choice((1.0, -1.0), size=(N_MC, len(d)))
    return float((np.sum((flips * d).mean(axis=1) >= d.mean() - 1e-12) + 1) / (N_MC + 1))


def boot_ci(d: np.ndarray, rng: np.random.Generator) -> list[float]:
    m = np.array([rng.choice(d, len(d)).mean() for _ in range(N_BOOT)])
    return [float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))]


def holm(ps: dict[str, float]) -> dict[str, float]:
    order = sorted(ps, key=ps.get)
    adj, run = {}, 0.0
    for i, k in enumerate(order):
        run = max(run, min(1.0, (len(order) - i) * ps[k]))
        adj[k] = run
    return adj


def var_components(D: np.ndarray) -> dict:
    """One-way random effects on D [units x inits]: sigma2_between (split pair + targets of the unit) and sigma2_within
    (init, incl. init x split interaction, not separable here); ICC = share of the unit."""
    n, k = D.shape
    msw = float(D.var(axis=1, ddof=1).mean())
    msb = float(k * D.mean(axis=1).var(ddof=1))
    sb = max(0.0, (msb - msw) / k)
    tot = sb + msw
    return {"sigma2_between_unit": sb, "sigma2_within_init": msw, "icc_unit": sb / tot if tot > 0 else float("nan")}


def cross_reading(D: np.ndarray) -> str:
    """Fixed session 16 (before any run): stable if >= 90 % of all (unit, init) Delta > 0 and the init SD < mean/2;
    init-dependent if < 75 % positive or init SD >= mean; else mixed. Descriptive, no test."""
    frac, m = float((D > 0).mean()), float(D.mean())
    sw = var_components(D)["sigma2_within_init"] ** 0.5
    if frac >= 0.9 and m > 0 and sw < m / 2:
        return "stabil über Inits"
    if frac < 0.75 or m <= 0 or sw >= m:
        return "init-abhängig"
    return "gemischt"


def cross_block(man: dict) -> dict | None:
    c = cross_spec(man)
    if c is None:
        return None
    t, rows = c["t"], []
    for s in c["seeds"]:
        T = {a: json.loads((SPLITS / f"{stem(man, t, s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
        inits = [s] + [cross_init(s, r) for r in range(c["R"])]
        pw = {(i, a): power_at(man, t, s, a, i) for i in inits for a in "FG"}
        bad = [f"init {i} {a}: {v}" for (i, a), v in pw.items() if isinstance(v, str)]
        rows.append({"seed": s, "inits": inits, "valid": not bad, "reason": "; ".join(bad)} if bad else
                    {"seed": s, "inits": inits, "valid": True,
                     "Delta_pow": [delta_pow(pw[(i, "F")], pw[(i, "G")], T["F"], T["G"]) for i in inits]})
    ok = [r for r in rows if r["valid"]]
    res: dict = {"task": f"{t['task']}{t['p']}", "rows": rows, "n_valid_units": len(ok)}
    if len(ok) < 4:
        res["reading"] = "nicht auswertbar"
        return res
    D = np.array([r["Delta_pow"] for r in ok])
    res.update(var_components(D))
    res.update({"mean": float(D.mean()), "frac_positive": float((D > 0).mean()),
                "min_per_unit": D.min(axis=1).tolist(), "reading": cross_reading(D)})
    return res


def analyze(manifest: Path) -> None:
    man = json.loads(manifest.read_text(encoding="utf-8"))
    check_manifest(manifest, man)
    rng = np.random.default_rng(1)
    out: dict = {"manifest_commit": man["commit"], "tasks": {}}
    for t in man["tasks"]:
        rows = []
        for s in man["seeds"]:
            T = {a: json.loads((SPLITS / f"{stem(man, t, s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
            pw = {a: power_at(man, t, s, a) for a in "FG"}
            bad = [f"{a}: {v}" for a, v in pw.items() if isinstance(v, str)]
            bad += [m for m in (split_mismatch(man, t, s, a) for a in "FG") if m]
            dp = None if bad else delta_pow_checked(pw["F"], pw["G"], T["F"], T["G"])
            if not bad and dp is None:
                bad = ["Delta_pow not finite or target power <= 0"]
            rows.append({"seed": s, "valid": False, "reason": "; ".join(bad)} if bad else
                        {"seed": s, "valid": True, "Delta_pow": dp})
        d = np.array([r["Delta_pow"] for r in rows if r["valid"]])
        res: dict = {"rows": rows, "n_valid": int(len(d)), "n_planned": len(man["seeds"])}
        if len(d) == len(man["seeds"]):   # session 20 (Codex B4): every planned pair, no complete-case deletion
            res.update({"mean": float(d.mean()), "sd": float(d.std(ddof=1)), "n_positive": int((d > 0).sum()),
                        "ci95": boot_ci(d, rng), "p": sign_flip_p(d, rng)})
        out["tasks"][f"{t['task']}{t['p']}"] = res
    adj = family_adjust({k: v.get("p", 1.0) for k, v in out["tasks"].items()}, man.get("primary_task"))
    out["primary_task"] = man.get("primary_task")
    for k, v in out["tasks"].items():
        v["p_holm_worstcase"] = adj[k]
        v["verdict"] = task_verdict(v)
        if "ci95" in v:
            v["min_effect_met"] = v["ci95"][0] >= MIN_EFFECT
    cb = cross_block(man)
    if cb is not None:
        out["cross_secondary"] = cb
        print(json.dumps({k: v for k, v in cb.items() if k != "rows"}, indent=1))
    (LAB / "confirm" / "P1_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: {x: y for x, y in v.items() if x != "rows"} for k, v in out["tasks"].items()}, indent=1))


def selftest() -> None:
    rng = np.random.default_rng(0)
    assert abs(delta_pow(np.array([4.0, 1.0]), np.array([1.0, 4.0]), [1], [2]) - 2 * np.log(4)) < 1e-12
    assert sign_flip_p(np.ones(10), rng) == 1 / 1024
    assert sign_flip_p(np.array([1.0, -1.0] * 5), rng) > 0.5
    lo, hi = boot_ci(np.full(10, 2.0), rng)
    assert lo == hi == 2.0
    man = {"experiment": 1, "eps": 2.0, "seeds": [1000], "device": "cuda", "python": "PY", "threads": 1,
           "tasks": [{"task": "add", "p": 113}, {"task": "D", "p": 59}]}
    j = jobs(man)
    assert len(j) == 4 and "--task add" in j[0] and "group_train.py" in j[2] and all("\\" not in x for x in j), j
    assert "confirm_exp1_eps2.0_add113_seed1000_F.npy" in j[0] and "--n 59" in j[2]
    h = holm({"a": 0.01, "b": 0.04, "c": 1.0})
    assert abs(h["a"] - 0.03) < 1e-12 and abs(h["b"] - 0.08) < 1e-12 and h["c"] == 1.0
    # cross block (session 16): extra inits reuse the unit's split files, D tasks rejected
    mc = {**man, "seeds": [1000, 1001], "cross": {"task": "add", "p": 113, "seeds": [1001], "inits_per_seed": 2}}
    jc = jobs(mc)
    assert len(jc) == 8 + 4 and "--seed 1201 " in jc[8] and "--seed 1301 " in jc[10], jc[8:]
    assert "confirm_exp1_eps2.0_add113_seed1001_F.npy" in jc[8] and "confirm_exp1_eps2.0_add113_seed1001_G.npy" in jc[9]
    for bad in ({"task": "D", "p": 59, "seeds": [1000], "inits_per_seed": 1},
                {"task": "add", "p": 113, "seeds": [999], "inits_per_seed": 1},
                {"task": "add", "p": 113, "seeds": [1000], "inits_per_seed": 3}):
        try:
            jobs({**mc, "cross": bad})
            raise AssertionError(bad)
        except SystemExit:
            pass
    vc = var_components(np.array([[1.0, 1.0, 1.0], [3.0, 3.0, 3.0]]))
    assert vc["sigma2_within_init"] == 0 and abs(vc["sigma2_between_unit"] - 2.0) < 1e-12 and vc["icc_unit"] == 1.0
    vc = var_components(np.array([[1.0, 3.0], [1.0, 3.0]]))
    assert vc["sigma2_between_unit"] == 0 and abs(vc["sigma2_within_init"] - 2.0) < 1e-12 and vc["icc_unit"] == 0.0
    assert cross_reading(np.full((5, 3), 8.0) + np.linspace(-1, 1, 15).reshape(5, 3)) == "stabil über Inits"
    assert cross_reading(np.array([[8.0, -1.0, 8.0]] * 5)) == "init-abhängig"
    # session 20 (Codex B4/H3)
    assert delta_pow_checked(np.array([4.0, 0.0]), np.array([1.0, 4.0]), [1], [2]) is None
    assert delta_pow_checked(np.array([4.0, np.nan]), np.array([1.0, 4.0]), [1], [2]) is None
    assert abs(delta_pow_checked(np.array([4.0, 1.0]), np.array([1.0, 4.0]), [1], [2]) - 2 * np.log(4)) < 1e-12
    import tempfile                                      # session 20 (Codex H6): split re-validation
    global SPLITS
    keep = SPLITS
    try:
        with tempfile.TemporaryDirectory() as tmp:
            SPLITS = Path(tmp)
            m1, t1 = {"experiment": 1, "eps": 2.0}, {"task": "add", "p": 113}
            idx, T = build(1, "add", 113, 1000, "F", 2.0)
            st = stem(m1, t1, 1000, "F")
            np.save(SPLITS / f"{st}.npy", idx)
            (SPLITS / f"{st}.json").write_text(json.dumps({"targets": T, "arm": "F", "seed": 1000}), encoding="utf-8")
            assert split_mismatch(m1, t1, 1000, "F") is None
            (SPLITS / f"{st}.json").write_text(json.dumps({"targets": T[::-1] if T != T[::-1] else [0], "arm": "F", "seed": 1000}), encoding="utf-8")
            assert "metadata" in split_mismatch(m1, t1, 1000, "F")
            np.save(SPLITS / f"{st}.npy", idx[1:])
            assert "indices" in split_mismatch(m1, t1, 1000, "F")
    finally:
        SPLITS = keep
    fa = family_adjust({"add113": 0.001, "mul113": 0.01, "add97": 0.02, "D59": 0.03}, "add113")
    assert abs(fa["add113"] - 0.003) < 1e-12 and abs(fa["mul113"] - 0.03) < 1e-12 and abs(fa["add97"] - 0.04) < 1e-12 and abs(fa["D59"] - 0.04) < 1e-12, fa   # Holm is monotone
    assert abs(family_adjust({"a": 0.01, "b": 0.02}, None)["a"] - 0.04) < 1e-12
    assert task_verdict({"n_valid": 49}) == "nicht auswertbar"
    assert task_verdict({"p": 0.001, "p_holm_worstcase": 0.003, "ci95": [0.5, 2.0]}) == "nicht bestätigt"
    assert task_verdict({"p": 0.001, "p_holm_worstcase": 0.003, "ci95": [1.2, 2.0]}) == "bestätigt"
    assert task_verdict({"p": 0.001, "p_holm_worstcase": 0.06, "ci95": [1.2, 2.0]}) == "nicht bestätigt"
    print("[confirm_p1] selftest ok", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        selftest()
    elif len(a) == 2 and a[0] == "--jobs":
        m = json.loads(Path(a[1]).read_text(encoding="utf-8"))
        check_manifest(Path(a[1]), m)
        print("\n".join(jobs(m)))
    elif len(a) == 2 and a[0] == "--analyze":
        analyze(Path(a[1]))
    else:
        raise SystemExit(__doc__)
