"""R4 confirmation (paper objection O1, programme A): does an ordinary RANDOM 30 % split shape which frequencies the embedding learns?
Session 30, UNTESTED. Revised after the Codex review of session 30 (lab/confirm/R4_codex_review_s30.txt).

Registration: lab/confirm/R4_REGISTRATION_DRAFT.md. Crossed design: unit u has two inits (seeds 2600 + 2u, 2601 + 2u) and two uniform
random splits (numpy SeedSequence([R4_TAG, u, j]), independent of every init seed); all four combinations are trained (freq_ban --split-file,
test = complement, 8000 steps, spectra at 250/1000/2000/4000/8000). Per unit and measure: S_split (same split, other init), S_init (same init,
other split), S_none (nothing shared), each the mean of two pairs.
Primary family (Holm over 2, one-sided t-test on delta - MDE, 95 % bootstrap CI; "bestätigt" = Holm p < 0.05 and CI lower bound >= 0):
  H1a  Spearman of the 56-frequency W_E power spectra at step 2000 (early rank signature):  S_split - S_none - 0.05 > 0
  H1b  cosine of the power spectra at step 8000 (energy-weighted, after grokking):          S_split - S_none - 0.04 > 0
"Relevant effect excluded" for an H = upper CI bound of delta below its MDE. Descriptive only: the init contrasts (S_init - S_none),
split minus init, all measures at all steps, top-5 overlap, generalized share at 8000.
Any missing or broken run, a checksum/shape violation -> "nicht auswertbar".

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
P, N_TRAIN, N_FREQ = 113, 3831, 56
AT = (250, 1000, 2000, 4000, 8000)
PRIMARY = {"H1a": ("rho", 2000, 0.05), "H1b": ("cos", 8000, 0.04)}     # measure, step, MDE (i.i.d.-cell surrogate unit SDs 0.145 / 0.085)
ALPHA, R4_TAG, TOP, ACC_GEN = 0.05, 20260930, 5, 0.9
SEED0, N_UNITS = 2600, 60
REGISTERED = {"units": 60, "steps": 8000, "device": "cuda", "threads": 1}
# confirm_p1 imports confirm_splits, which loads the EXP-043/046 split modules (Codex s30 blocker: closure must be hashed)
CODE_FILES = ("lab/tools/confirm_r4.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/result_loader.py",
              "lab/tools/confirm_splits.py", "lab/experiments/EXP-043-generalize-steering/make_split.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py",
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


CELLS = [(i, j) for i in (0, 1) for j in (0, 1)]       # (init index, split index), all four combinations


def check_units(man: dict) -> int:
    n = man["units"]
    if not isinstance(n, int) or isinstance(n, bool) or n != N_UNITS:
        raise SystemExit(f"R4 units must be {N_UNITS} (registration), got {n!r}")
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
    return [job(man, u, i, j) for u in range(check_units(man)) for i, j in CELLS]


def expected_run_id(cmd: list[str]) -> str:
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    dev = (g("--device") or "cpu").replace(":", "")
    return (f"EXP-016_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}"
            + ("" if dev == "cpu" else f"_dev{dev}"))


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_r4", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_r4.py")


# ---------------------------------------------------------------- measures
def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = np.argsort(np.argsort(x)).astype(float), np.argsort(np.argsort(y)).astype(float)   # ties: power spectra are continuous
    rx, ry = rx - rx.mean(), ry - ry.mean()
    return float((rx * ry).sum() / np.sqrt((rx ** 2).sum() * (ry ** 2).sum()))


def cosine(x: np.ndarray, y: np.ndarray) -> float:
    return float(x @ y / (np.linalg.norm(x) * np.linalg.norm(y)))


def overlap(x: np.ndarray, y: np.ndarray) -> float:
    return float(len(set(np.argsort(x)[-TOP:]) & set(np.argsort(y)[-TOP:])))


MEASURES = {"rho": spearman, "cos": cosine, "top": overlap}
PAIRS = {"split": [((0, 0), (1, 0)), ((0, 1), (1, 1))], "init": [((0, 0), (0, 1)), ((1, 0), (1, 1))],
         "none": [((0, 0), (1, 1)), ((0, 1), (1, 0))]}


def similarities(runs: dict) -> dict[str, float]:
    return {f"{kind}_{name}_{t}": float(np.mean([f(runs[a]["spec"][t], runs[b]["spec"][t]) for a, b in pp]))
            for t in AT for kind, f in MEASURES.items() for name, pp in PAIRS.items()}


def identity_violation(runs: dict) -> str | None:
    """Codex s30: same init -> same init checksum, different inits -> different; every spectrum has shape (56,)."""
    cs = {k: v["init_checksum"] for k, v in runs.items()}
    if not (cs[(0, 0)] == cs[(0, 1)] and cs[(1, 0)] == cs[(1, 1)] and cs[(0, 0)] != cs[(1, 0)] and all(cs.values())):
        return "init checksums do not match the crossed design"
    if any(np.shape(s) != (N_FREQ,) for v in runs.values() for s in v["spec"].values()):
        return "spectrum shape is not (56,)"
    return None


# ---------------------------------------------------------------- analysis
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
    return {"spec": {t: L.spectrum(t) for t in AT}, "test_acc": (L.res.get("final_acc") or {}).get("test"),
            "init_checksum": L.res.get("init_checksum_shared")}


def unit_row(man: dict, u: int) -> dict:
    runs = {(i, j): one_run(man, u, i, j) for i, j in CELLS}
    bad = [v for v in runs.values() if isinstance(v, str)]
    if bad:
        return {"unit": u, "technical": True, "reason": "; ".join(bad[:4])}
    if (why := identity_violation(runs)):
        return {"unit": u, "technical": True, "reason": why}
    return {"unit": u, "technical": False, "inits": list(inits(u)), **similarities(runs),
            "generalised": sum(1 for v in runs.values() if isinstance(v["test_acc"], (int, float)) and v["test_acc"] >= ACC_GEN)}


def delta(r: dict, kind: str, t: int, who: str = "split") -> float:
    return r[f"{kind}_{who}_{t}"] - r[f"{kind}_none_{t}"]


def verdict(rows: list[dict], n_planned: int, rng: np.random.Generator) -> dict:
    n_tech = sum(1 for r in rows if r.get("technical"))
    if n_tech or len(rows) != n_planned or n_planned < 3:
        return {"n": len(rows), "n_technical": n_tech, "verdict": "nicht auswertbar"}
    X = {h: np.array([delta(r, kind, t) - mde for r in rows]) for h, (kind, t, mde) in PRIMARY.items()}
    tt = {h: c1.t_test_secondary(v) for h, v in X.items()}
    ph = c1.holm({h: t["p_one_sided"] for h, t in tt.items()})
    out: dict = {"n": len(rows), "n_technical": 0}
    for h, v in X.items():
        ci, mde = c1.boot_ci(v, rng), PRIMARY[h][2]
        out[h] = {"measure": PRIMARY[h][0], "step": PRIMARY[h][1], "mde": mde, "mean_delta": float(v.mean() + mde),
                  "sd": float(v.std(ddof=1)), "ci95_minus_mde": ci, "t": tt[h]["t"], "p": tt[h]["p_one_sided"], "p_holm": ph[h],
                  "n_positive": int((v > 0).sum()),
                  "verdict": "bestätigt" if ph[h] < ALPHA and ci[0] >= 0.0 else "nicht bestätigt",
                  "relevant_effect_excluded": bool(ci[1] < 0.0)}
    desc: dict = {}
    for t in AT:
        for kind in MEASURES:
            s = np.array([delta(r, kind, t, "split") for r in rows])
            i = np.array([delta(r, kind, t, "init") for r in rows])
            none = np.array([r[f"{kind}_none_{t}"] for r in rows])      # transfer check of the study-run null calibration (s30)
            desc[f"{kind}@{t}"] = {"s_none_mean_sd": [float(none.mean()), float(none.std(ddof=1))],
                                   "delta_split": [float(s.mean()), c1.boot_ci(s, rng)],
                                   "delta_init": [float(i.mean()), c1.boot_ci(i, rng)],
                                   "split_minus_init": [float((s - i).mean()), c1.boot_ci(s - i, rng)]}
    out["descriptive"] = desc
    out["generalised_runs"] = int(sum(r["generalised"] for r in rows))
    out["generalised_share"] = out["generalised_runs"] / (4 * len(rows))          # test >= 0.9 at the end (step 8000)
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
def _fake_rows(rng: np.random.Generator, w_split: float, w_init: float, n: int = 30) -> list[dict]:
    rows = []
    for u in range(n):
        base = {t: rng.standard_normal(N_FREQ) for t in AT}
        sp = [{t: rng.standard_normal(N_FREQ) for t in AT} for _ in (0, 1)]
        ini = [{t: rng.standard_normal(N_FREQ) for t in AT} for _ in (0, 1)]
        runs = {(i, j): {"spec": {t: np.exp(0.3 * base[t] + w_split * sp[j][t] + w_init * ini[i][t] + rng.standard_normal(N_FREQ))
                                  for t in AT}, "test_acc": 1.0, "init_checksum": f"c{i}"} for i, j in CELLS}
        assert identity_violation(runs) is None
        rows.append({"unit": u, "technical": False, "generalised": 4, **similarities(runs)})
    return rows


def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    for bad in ({"units": 40}, {"units": 60.0}, {"units": True}):
        try:
            check_units({**man, **bad})
            raise AssertionError(f"bad units accepted: {bad}")
        except SystemExit:
            pass
    for bad in ({"steps": 8000.0}, {"steps": 2000}, {"threads": True}, {"device": "cpu"}, {"units": 40}):
        try:
            BLOCK.check_registered({**man, **bad})
            raise AssertionError(f"unregistered manifest accepted: {bad}")
        except SystemExit:
            pass
    s00, s01, s10 = split_indices(0, 0), split_indices(0, 1), split_indices(1, 0)
    assert len(s00) == N_TRAIN == len(np.unique(s00)) and s00.min() >= 0 and s00.max() < P * P
    assert np.array_equal(s00, split_indices(0, 0)) and not np.array_equal(s00, s01) and not np.array_equal(s00, s10)
    assert abs(np.intersect1d(s00, s01).size / N_TRAIN - 0.3) < 0.03                      # independent uniform splits overlap ~30 %
    assert len({x for u in range(N_UNITS) for x in inits(u)}) == 2 * N_UNITS and inits(N_UNITS - 1)[1] == 2719
    tj = trainer_jobs(man)
    assert len(tj) == 4 * N_UNITS == len(set(tj)) and all("r4_raw" in j and "\\" not in j and "--stop-after-gen 8000" in j for j in tj)
    assert len({expected_run_id(shlex.split(j)) for j in tj}) == 4 * N_UNITS
    assert expected_run_id(shlex.split(tj[0])) == "EXP-016_baseline_seed2600_thr1_r4_u0_s0_devcuda", expected_run_id(shlex.split(tj[0]))
    assert expected_run_id(shlex.split(tj[3])) == "EXP-016_baseline_seed2601_thr1_r4_u0_s1_devcuda"
    assert "--spectra-at 250,1000,2000,4000,8000" in tj[0] and "--steps 8000" in tj[0] and "--test-file" not in tj[0]
    assert all(j.startswith("python lab/tools/confirm_r4.py --run M -- ") for j in BLOCK.jobs(man, "M"))
    BLOCK.check_job(man, shlex.split(tj[0]))
    try:
        BLOCK.check_job(man, shlex.split(tj[0]) + ["--force"])
        raise AssertionError("foreign command accepted")
    except SystemExit:
        pass
    assert run_dir(shlex.split(job(man, 0, 1, 1))) == RAW / "EXP-016_baseline_seed2601_thr1_r4_u0_s1_devcuda"   # one_run's lookup
    good = {(i, j): {"spec": {t: np.ones(N_FREQ) for t in AT}, "init_checksum": f"c{i}"} for i, j in CELLS}
    assert identity_violation(good) is None
    assert identity_violation({**good, (0, 1): {**good[(0, 1)], "init_checksum": "c1"}}) is not None     # same init, other checksum
    assert identity_violation({k: {**v, "init_checksum": "c"} for k, v in good.items()}) is not None      # two inits, one checksum
    assert identity_violation({**good, (1, 1): {**good[(1, 1)], "spec": {t: np.ones(55) for t in AT}}}) is not None
    rng = np.random.default_rng(0)
    v = verdict(_fake_rows(rng, 1.0, 0.0), 30, rng)                 # verdict itself is n-agnostic; 30 synthetic units suffice
    assert all(v[h]["verdict"] == "bestätigt" for h in PRIMARY), v
    v = verdict(_fake_rows(rng, 0.0, 1.0), 30, rng)                 # init effect only: no split verdict, init shows descriptively
    assert all(v[h]["verdict"] == "nicht bestätigt" for h in PRIMARY) and v["descriptive"]["rho@2000"]["delta_init"][0] > 0.1, v
    v = verdict(_fake_rows(rng, 0.0, 0.0), 30, rng)
    assert all(v[h]["verdict"] == "nicht bestätigt" and abs(v[h]["mean_delta"]) < 0.1 for h in PRIMARY), v   # noise SD ~0.04 at n = 30
    assert verdict(_fake_rows(rng, 1.0, 0.0)[:29], 30, rng)["verdict"] == "nicht auswertbar"
    assert verdict(_fake_rows(rng, 1.0, 0.0)[:29] + [{"unit": 29, "technical": True}], 30, rng)["verdict"] == "nicht auswertbar"
    x = np.arange(1.0, 57.0)
    assert abs(spearman(x, x) - 1) < 1e-12 and abs(spearman(x, -x) + 1) < 1e-12 and overlap(x, x) == TOP and abs(cosine(x, 2 * x) - 1) < 1e-12
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    loaded = {Path(m.__file__).resolve().relative_to(ROOT.resolve()).as_posix() for m in list(sys.modules.values())
              if getattr(m, "__file__", None) and Path(m.__file__).resolve().is_relative_to((ROOT / "lab").resolve())}
    assert loaded <= set(CODE_FILES), sorted(loaded - set(CODE_FILES))
    print("[confirm_r4] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
