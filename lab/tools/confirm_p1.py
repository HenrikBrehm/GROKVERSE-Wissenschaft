"""P1 confirmation (FINDINGS "Programm"): job list and frozen analysis for the reserved block. Session 14, UNTESTED.

P1: engineered splits raise the target power in W_E, Delta_pow > 0 on fresh seeds and splits, minimum effect Delta_pow >= 1.
Primary per task in the manifest: mean Delta_pow over seeds, one-sided sign-flip test of mean > 0 (exact for n <= 20, else
Monte Carlo), 95 % bootstrap CI of the mean; the p-values enter the P1-P3 Holm family (FAMILY = 3, p of missing members = 1).
"confirmed" for a task needs Holm-p < 0.05 AND the lower CI bound > 0; the minimum effect is reported (CI lower bound >= 1?).
Runs: transformer of the study (freq_ban.py, add/mul) or group_train.py (D_n), 2000 steps, device from the manifest.

  python lab/tools/confirm_p1.py --jobs lab/confirm/P1_manifest.json > lab/confirm/P1_jobs.txt     # for parallel_queue.py
  python lab/tools/confirm_p1.py --analyze lab/confirm/P1_manifest.json                             # under guarded_run.py
  python lab/tools/confirm_p1.py --selftest
Extra manifest fields: "device": "cuda"|"cpu", "python": ".venv-gpu/Scripts/python.exe", "threads": 1.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools"))
from confirm_splits import OUT as SPLITS, check_manifest  # noqa: E402
from result_loader import Expect, find_run, load_run  # noqa: E402

STEP, ALPHA, FAMILY, MIN_EFFECT, N_BOOT, N_MC = 2000, 0.05, 3, 1.0, 10_000, 200_000
RAW = LAB / "confirm" / "raw"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
GT = "lab/experiments/EXP-046-dihedral-steering/group_train.py"


def stem(man: dict, t: dict, s: int, arm: str) -> str:
    return f"confirm_exp{int(man['experiment'])}_eps{float(man['eps'])}_{t['task']}{t['p']}_seed{s}_{arm}"


def jobs(man: dict) -> list[str]:
    out = []
    for t in man["tasks"]:
        for s in man["seeds"]:
            for arm in "FG":
                sp = f"lab/confirm/splits/{stem(man, t, s, arm)}.npy"
                if t["task"] == "D":
                    out.append(f"{man['python']} {GT} --seed {s} --n {t['p']} --steps {STEP} --device {man['device']} --split-file {sp} "
                               f"--out-root lab/confirm/raw")
                else:
                    out.append(f"{man['python']} {FB} --seed {s} --condition baseline --steps {STEP} --threads {man['threads']} "
                               f"--device {man['device']} --p {t['p']} --task {t['task']} --split-file {sp} "
                               f"--spectra-at 250,500,1000,{STEP} --out-root lab/confirm/raw")
    return out


def power_at(man: dict, t: dict, s: int, arm: str) -> np.ndarray | str:
    st = stem(man, t, s, arm)
    split = SPLITS / f"{st}.npy"
    dev = man["device"]
    if t["task"] == "D":
        L = load_run(find_run(RAW, f"EXP-046_seed{s}_{st}_dev{dev}"),
                     Expect(seed=s, device=dev, max_steps=STEP, split_file=split, config={"p": 2 * t["p"], "group": f"D{t['p']}"},
                            at=(STEP,)))
        return L.spectrum(STEP) if L.status == "ok" else f"{L.status}: {L.reason}"
    suffix = "" if (t["task"], t["p"]) == ("add", 113) else f"_{t['task']}{t['p']}"
    devsuf = "" if dev == "cpu" else f"_dev{dev}"            # freq_ban: CPU run-ids carry no device suffix
    L = load_run(find_run(RAW, f"EXP-0*_baseline_seed{s}_thr*_{st}{suffix}{devsuf}"),
                 Expect(seed=s, device=dev, max_steps=STEP, split_file=split, config={"p": t["p"], "task": t["task"]},
                        snapshots_at=(STEP,)))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
    from analyze import group_power                       # EXP-043 group-basis power (add 113 = plain DFT, k = 1..56)
    return group_power(L.snapshot(STEP), t["task"], t["p"])[0]


def delta_pow(pF: np.ndarray, pG: np.ndarray, F: list[int], G: list[int]) -> float:
    s = lambda pw, S: float(pw[[k - 1 for k in S]].sum())   # noqa: E731
    return float(np.log(s(pF, F) / s(pF, G)) + np.log(s(pG, G) / s(pG, F)))


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
            rows.append({"seed": s, "valid": False, "reason": "; ".join(bad)} if bad else
                        {"seed": s, "valid": True, "Delta_pow": delta_pow(pw["F"], pw["G"], T["F"], T["G"])})
        d = np.array([r["Delta_pow"] for r in rows if r["valid"]])
        res: dict = {"rows": rows, "n_valid": int(len(d)), "n_planned": len(man["seeds"])}
        if len(d) >= max(8, int(0.8 * len(man["seeds"]))):
            res.update({"mean": float(d.mean()), "sd": float(d.std(ddof=1)), "n_positive": int((d > 0).sum()),
                        "ci95": boot_ci(d, rng), "p": sign_flip_p(d, rng)})
        out["tasks"][f"{t['task']}{t['p']}"] = res
    ps = {k: v.get("p", 1.0) for k, v in out["tasks"].items()}
    ps.update({f"_other{i}": 1.0 for i in range(FAMILY - 1)})   # P2, P3 enter with p = 1 until their results exist
    adj = holm(ps)
    for k, v in out["tasks"].items():
        v["p_holm_worstcase"] = adj[k]
        v["verdict"] = ("nicht auswertbar" if "p" not in v else
                        "bestätigt" if v["p_holm_worstcase"] < ALPHA and v["ci95"][0] > 0 else "nicht bestätigt")
        if "ci95" in v:
            v["min_effect_met"] = v["ci95"][0] >= MIN_EFFECT
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
