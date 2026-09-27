"""R4 confirmation (paper objection O1, programme A): does an ordinary RANDOM 30 % split shape which frequencies the embedding learns?
Session 30, UNTESTED.

Registration: lab/confirm/R4_REGISTRATION_DRAFT.md. Crossed design: unit u has two inits (seeds 2600 + 2u, 2601 + 2u) and two uniform
random splits (numpy SeedSequence([R4_TAG, u, j]), independent of every init seed); all four combinations are trained (freq_ban --split-file,
test = complement, 2000 steps, spectra at 250/1000/2000). Similarity = Spearman of the 56-frequency W_E power spectra at step 2000.
Per unit: S_split (same split, other init), S_init (same init, other split), S_none (nothing shared), each the mean of two pairs.
Primary family (Holm over 2, one-sided t-test on delta - MDE, 95 % bootstrap CI; "bestätigt" = Holm p < 0.05 and CI lower bound >= 0):
  H1  S_split - S_none - MDE > 0      H2  S_init - S_none - MDE > 0
Descriptive: (S_split - S_none) - (S_init - S_none) with CI; the same at steps 250 and 1000; top-5 overlap; generalized share.
Any missing or broken run -> "nicht auswertbar".

  python lab/tools/confirm_r4.py --hash-code | --splits M | --jobs M | --run M -- <cmd> | --analyze M | --selftest
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
import confirm_p1 as c1  # noqa: E402  (read-only reuse: interp, t-test, bootstrap, holm)
from bound_block import Block, selftest_binding  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

RAW = LAB / "confirm" / "r4_raw"
BIND = LAB / "confirm" / "r4_bindings"
SPL = LAB / "confirm" / "r4_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
P, N_TRAIN, STEPS, AT, PRIMARY_STEP = 113, 3831, 2000, (250, 1000, 2000), 2000
ALPHA, MDE, R4_TAG, TOP = 0.05, 0.05, 20260930, 5
SEED0, MAX_UNITS = 2600, 40
REGISTERED = {"units": 40, "steps": 2000, "device": "cuda", "threads": 1}
CODE_FILES = ("lab/tools/confirm_r4.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/result_loader.py",
              "lab/experiments/EXP-001-freq-ban/freq_ban.py")


# ---------------------------------------------------------------- design
def inits(u: int) -> tuple[int, int]:
    return SEED0 + 2 * u, SEED0 + 2 * u + 1


def split_indices(u: int, j: int) -> np.ndarray:
    """Uniform random 30 % split, own stream per (unit, split); never drawn from an init seed (rule 18a6)."""
    rng = np.random.default_rng(np.random.SeedSequence([R4_TAG, u, j]))
    return np.sort(rng.choice(P * P, size=N_TRAIN, replace=False)).astype(np.int64)


def split_path(u: int, j: int) -> Path:
    return SPL / f"r4_u{u}_s{j}.npy"


def cells(u: int) -> list[tuple[int, int]]:
    """(init index 0/1, split index 0/1), all four combinations."""
    return [(i, j) for i in (0, 1) for j in (0, 1)]


def check_units(man: dict) -> int:
    n = man["units"]
    if not isinstance(n, int) or isinstance(n, bool) or n != MAX_UNITS:
        raise SystemExit(f"R4 units must be {MAX_UNITS} (registration), got {n!r}")
    return n


def write_splits(man: dict) -> None:
    n = check_units(man)
    SPL.mkdir(parents=True, exist_ok=True)
    if any(split_path(u, j).exists() for u in range(n) for j in (0, 1)):
        raise SystemExit("R4 splits exist already: never overwrite")
    for u in range(n):
        for j in (0, 1):
            with open(split_path(u, j), "xb") as f:
                np.save(f, split_indices(u, j))


def split_mismatch(u: int) -> str | None:
    for j in (0, 1):
        f = split_path(u, j)
        if not f.exists():
            return f"unit {u}: split {j} missing"
        if not np.array_equal(np.load(f), split_indices(u, j)):
            return f"unit {u}: split {j} differs from the deterministic rebuild"
    return None


def job(man: dict, u: int, i: int, j: int) -> str:
    return (f"{c1.interp(man)} {FB} --seed {inits(u)[i]} --condition baseline --threads {man['threads']} --device {man['device']} "
            f"--out-root lab/confirm/r4_raw --steps {man['steps']} --split-file lab/confirm/r4_splits/{split_path(u, j).name} "
            f"--spectra-at {','.join(str(t) for t in AT)} --stop-after-gen {man['steps']}")


def trainer_jobs(man: dict) -> list[str]:
    return [job(man, u, i, j) for u in range(check_units(man)) for i, j in cells(u)]


def expected_run_id(cmd: list[str]) -> str:
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    dev = (g("--device") or "cpu").replace(":", "")
    return (f"EXP-016_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}"
            + ("" if dev == "cpu" else f"_dev{dev}"))


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_r4", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_r4.py")


# ---------------------------------------------------------------- analysis
def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = np.argsort(np.argsort(x)).astype(float), np.argsort(np.argsort(y)).astype(float)   # ties: power spectra are continuous
    rx, ry = rx - rx.mean(), ry - ry.mean()
    return float((rx * ry).sum() / np.sqrt((rx ** 2).sum() * (ry ** 2).sum()))


def overlap(x: np.ndarray, y: np.ndarray) -> float:
    return float(len(set(np.argsort(x)[-TOP:]) & set(np.argsort(y)[-TOP:])))


def one_run(man: dict, u: int, i: int, j: int) -> dict | str:
    d, tag = run_dir(shlex.split(job(man, u, i, j))), f"u{u}:i{i}s{j}"
    if not d.exists():
        return f"{tag}: fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt: {why}"
    L = load_run(d, Expect(seed=inits(u)[i], device=man["device"], max_steps=man["steps"], split_file=split_path(u, j),
                           config={"p": P, "task": "add", "arch": "transformer", "lr": 1e-3, "weight_decay": 1.0, "train_frac": 0.3},
                           at=AT))
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt after load: {why}"
    acc = (L.res.get("final_acc") or {}).get("test")
    return {"spec": {t: L.spectrum(t) for t in AT}, "test_acc": acc}


PAIRS = {"split": [((0, 0), (1, 0)), ((0, 1), (1, 1))], "init": [((0, 0), (0, 1)), ((1, 0), (1, 1))],
         "none": [((0, 0), (1, 1)), ((0, 1), (1, 0))]}     # keys (init index, split index)


def similarities(runs: dict) -> dict[str, float]:
    return {f"{kind}_{name}_{t}": float(np.mean([f(runs[a]["spec"][t], runs[b]["spec"][t]) for a, b in pp]))
            for t in AT for kind, f in (("rho", spearman), ("top", overlap)) for name, pp in PAIRS.items()}


def unit_row(man: dict, u: int) -> dict:
    runs = {(i, j): one_run(man, u, i, j) for i, j in cells(u)}
    bad = [v for v in runs.values() if isinstance(v, str)]
    if bad:
        return {"unit": u, "technical": True, "reason": "; ".join(bad[:4])}
    return {"unit": u, "technical": False, "inits": list(inits(u)), **similarities(runs),
            "generalised": sum(1 for v in runs.values() if isinstance(v["test_acc"], (int, float)) and v["test_acc"] >= 0.9)}


def deltas(r: dict, t: int = PRIMARY_STEP, kind: str = "rho") -> dict[str, float]:
    return {"H1": r[f"{kind}_split_{t}"] - r[f"{kind}_none_{t}"], "H2": r[f"{kind}_init_{t}"] - r[f"{kind}_none_{t}"]}


def verdict(rows: list[dict], n_planned: int, rng: np.random.Generator) -> dict:
    n_tech = sum(1 for r in rows if r.get("technical"))
    if n_tech or len(rows) != n_planned or n_planned < 3:
        return {"n": len(rows), "n_technical": n_tech, "verdict": "nicht auswertbar"}
    X = {h: np.array([deltas(r)[h] - MDE for r in rows]) for h in ("H1", "H2")}
    tt = {h: c1.t_test_secondary(v) for h, v in X.items()}
    ph = c1.holm({h: t["p_one_sided"] for h, t in tt.items()})
    out: dict = {"n": len(rows), "n_technical": 0, "mde": MDE}
    for h, v in X.items():
        ci = c1.boot_ci(v, rng)
        out[h] = {"mean_delta": float(v.mean() + MDE), "sd": float(v.std(ddof=1)), "ci95_minus_mde": ci, "t": tt[h]["t"],
                  "p": tt[h]["p_one_sided"], "p_holm": ph[h], "n_positive": int((v > 0).sum()),
                  "verdict": "bestätigt" if ph[h] < ALPHA and ci[0] >= 0.0 else "nicht bestätigt"}
    desc: dict = {}
    for t in AT:
        for kind in ("rho", "top"):
            d = {h: np.array([deltas(r, t, kind)[h] for r in rows]) for h in ("H1", "H2")}
            diff = d["H1"] - d["H2"]
            desc[f"{kind}@{t}"] = {"delta_split": [float(d["H1"].mean()), c1.boot_ci(d["H1"], rng)],
                                   "delta_init": [float(d["H2"].mean()), c1.boot_ci(d["H2"], rng)],
                                   "split_minus_init": [float(diff.mean()), c1.boot_ci(diff, rng)]}
    out["descriptive"] = desc
    out["generalised_runs"] = int(sum(r["generalised"] for r in rows))
    return out


def analyze(manifest: Path) -> None:
    stale = LAB / "confirm" / "R4_summary.json"
    if stale.exists():
        stale.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    n = check_units(man)
    bad = [m for m in (split_mismatch(u) for u in range(n)) if m]
    if bad:
        raise SystemExit(f"R4 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = [unit_row(man, u) for u in range(n)]
    out = {"manifest_commit": man["commit"], "n_planned": n, "hypotheses": verdict(rows, n, np.random.default_rng(4)), "rows": rows}
    (LAB / "confirm" / "R4_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


# ---------------------------------------------------------------- selftest
def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    for bad in ({"units": 30}, {"units": 40.0}, {"units": True}):
        try:
            check_units({**man, **bad})
            raise AssertionError(f"bad units accepted: {bad}")
        except SystemExit:
            pass
    for bad in ({"steps": 2000.0}, {"threads": True}, {"device": "cpu"}, {"units": 30}):
        try:
            BLOCK.check_registered({**man, **bad})
            raise AssertionError(f"unregistered manifest accepted: {bad}")
        except SystemExit:
            pass
    s00, s01, s10 = split_indices(0, 0), split_indices(0, 1), split_indices(1, 0)
    assert len(s00) == N_TRAIN == len(np.unique(s00)) and s00.min() >= 0 and s00.max() < P * P
    assert np.array_equal(s00, split_indices(0, 0)) and not np.array_equal(s00, s01) and not np.array_equal(s00, s10)
    assert abs(np.intersect1d(s00, s01).size / N_TRAIN - 0.3) < 0.03                      # independent uniform splits overlap ~30 %
    assert len({x for u in range(MAX_UNITS) for x in inits(u)}) == 2 * MAX_UNITS and inits(MAX_UNITS - 1)[1] == 2679
    tj = trainer_jobs(man)
    assert len(tj) == 4 * MAX_UNITS == len(set(tj)) and all("r4_raw" in j and "\\" not in j and "--stop-after-gen 2000" in j for j in tj)
    assert len({expected_run_id(shlex.split(j)) for j in tj}) == 4 * MAX_UNITS
    assert expected_run_id(shlex.split(tj[0])) == "EXP-016_baseline_seed2600_thr1_r4_u0_s0_devcuda", expected_run_id(shlex.split(tj[0]))
    assert expected_run_id(shlex.split(tj[3])) == "EXP-016_baseline_seed2601_thr1_r4_u0_s1_devcuda"
    assert "--spectra-at 250,1000,2000" in tj[0] and "--save-model" not in tj[0] and "--test-file" not in tj[0]
    assert all(j.startswith("python lab/tools/confirm_r4.py --run M -- ") for j in BLOCK.jobs(man, "M"))
    BLOCK.check_job(man, shlex.split(tj[0]))
    try:
        BLOCK.check_job(man, shlex.split(tj[0]) + ["--force"])
        raise AssertionError("foreign command accepted")
    except SystemExit:
        pass
    assert run_dir(shlex.split(job(man, 0, 1, 1))) == RAW / "EXP-016_baseline_seed2601_thr1_r4_u0_s1_devcuda"   # one_run's lookup
    # statistics on synthetic spectra: split effect only / init effect only / nothing
    rng = np.random.default_rng(0)

    def fake_rows(w_split: float, w_init: float, n: int = 30) -> list[dict]:
        rows = []
        for u in range(n):
            base = {t: rng.standard_normal(56) for t in AT}
            sp = [{t: rng.standard_normal(56) for t in AT} for _ in (0, 1)]
            ini = [{t: rng.standard_normal(56) for t in AT} for _ in (0, 1)]
            runs = {(i, j): {"spec": {t: np.exp(0.3 * base[t] + w_split * sp[j][t] + w_init * ini[i][t] + rng.standard_normal(56))
                                      for t in AT}, "test_acc": 1.0} for i, j in cells(u)}
            rows.append({"unit": u, "technical": False, "generalised": 4, **similarities(runs)})
        return rows
    v = verdict(fake_rows(1.0, 0.0), 30, rng)                      # verdict itself is n-agnostic; 30 synthetic units suffice
    assert v["H1"]["verdict"] == "bestätigt" and v["H2"]["verdict"] == "nicht bestätigt", v
    v = verdict(fake_rows(0.0, 1.0), 30, rng)
    assert v["H1"]["verdict"] == "nicht bestätigt" and v["H2"]["verdict"] == "bestätigt", v
    v = verdict(fake_rows(0.0, 0.0), 30, rng)
    assert v["H1"]["verdict"] == v["H2"]["verdict"] == "nicht bestätigt" and abs(v["H1"]["mean_delta"]) < 0.05, v
    assert verdict(fake_rows(1.0, 0.0)[:29], 30, rng)["verdict"] == "nicht auswertbar"
    assert verdict(fake_rows(1.0, 0.0)[:29] + [{"unit": 29, "technical": True}], 30, rng)["verdict"] == "nicht auswertbar"
    x = np.arange(56.0)
    assert abs(spearman(x, x) - 1) < 1e-12 and abs(spearman(x, -x) + 1) < 1e-12 and overlap(x, x) == TOP
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    loaded = {Path(m.__file__).resolve().relative_to(ROOT.resolve()).as_posix() for m in list(sys.modules.values())
              if getattr(m, "__file__", None) and Path(m.__file__).resolve().is_relative_to((ROOT / "lab").resolve())}
    assert loaded <= set(CODE_FILES), sorted(loaded - set(CODE_FILES))
    print("[confirm_r4] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
