"""L0 confirmation (rule 20b): does set composition (K2) steer the learned frequencies under minibatch training? Session 43,
SCAFFOLD: H1/H2 fixed before the pilot EXP-100; N_SEEDS, BUDGET and H3 are set AFTER the pilot (registration
lab/confirm/L0_REGISTRATION_DRAFT.md lists the pilot as seen data). UNTESTED. Needs the trainer options of
lab/experiments/EXP-100-set-vs-order/trainer_l0.patch (applied and committed before freezing).

Protocol: add 113, the EXP-100 construction (EXP-053/P1 splits with omega = 0 and calibrated eps, target sets drawn WITHOUT the
stride-order frequencies O); the target draw uses its own stream SeedSequence([100200, seed, 0]), test set, phases and keys come
from EXP-053's streams (salt 53001) as in P1; per seed arms F and G; minibatch AdamW with
i.i.d. order at batch 256 (H1) and 64 (H2); fixed budget (--stop-after-gen = budget).
Primary family (Holm, alpha 0.05): H1 Delta_pow(end) > 0 at batch 256; H2 the same at batch 64 (one-sided t-test; confirmed =
Holm-p < 0.05 and bootstrap CI lower bound > 0). H3 (conflict with the stride order) only if the pilot showed an order effect.
Validity: any technical failure -> 'nicht auswertbar'; a non-finite Delta_pow or a load/transform exception is technical.
Smoke: check_job accepts only full-budget lines, so the smoke job through the frozen loader costs one full run (plan the time).

  python lab/tools/confirm_l0.py --hash-code | --splits M | --jobs M | --run M -- <cmd> | --analyze M | --selftest
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

RAW, BIND, SPL = LAB / "confirm/l0_raw", LAB / "confirm/l0_bindings", LAB / "confirm/l0_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
CAL = LAB / "experiments/EXP-053-p3-overlap-design/calibration.json"
SALT, ALPHA = 100_200, 0.05
O = (11, 12, 22, 23, 34, 45)                   # stride-order frequencies for p = 113 (EXP-100)
N_SEEDS: int | None = 10                        # s46: power rule after the EXP-100 pilot (L0_power_s46.py -> 10)
BUDGET: int | None = 30_000                     # s46: pilot runtime ~4-5 min per run on the GPU
ARMS = {"iid256": 256, "iid64": 64}             # H1, H2
HYP = {"H1": "iid256", "H2": "iid64"}
REGISTERED = {"seeds": list(range(3720, 3720 + (N_SEEDS or 0))), "budget": BUDGET, "device": "cuda", "threads": 1,
              "arms": dict(ARMS), "order_freqs": list(O)}
CODE_FILES = ("lab/tools/confirm_l0.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_splits.py",
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


def stem(s: int, arm: str) -> str:
    return f"l0_seed{s}_{arm}"


def write_splits(man: dict) -> None:
    require_set()
    SPL.mkdir(parents=True, exist_ok=True)
    if any((SPL / f"{stem(s, a)}.npy").exists() for s in man["seeds"] for a in ("F", "G", "test")):
        raise SystemExit("L0 splits exist already: never overwrite")
    for s in man["seeds"]:
        d, (F, G) = build(s), targets(s)
        for a, key in (("F", "A"), ("G", "B"), ("test", "test")):
            with open(SPL / f"{stem(s, a)}.npy", "xb") as f:
                np.save(f, d[key].astype(np.int64))
        with open(SPL / f"l0_seed{s}.json", "x", encoding="utf-8") as f:
            json.dump({"seed": s, "targets": {"F": F, "G": G}, "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(s: int) -> str | None:
    d, (F, G) = build(s), targets(s)
    files = {"F": "A", "G": "B", "test": "test"}
    for a, key in files.items():
        f = SPL / f"{stem(s, a)}.npy"
        if not f.exists() or not np.array_equal(np.load(f), d[key].astype(np.int64)):
            return f"seed {s}: split {a} missing or differs from the rebuild"
    meta = json.loads((SPL / f"l0_seed{s}.json").read_text(encoding="utf-8"))
    return None if meta.get("targets") == {"F": F, "G": G} else f"seed {s}: targets differ"


def trainer_jobs(man: dict) -> list[str]:
    if man.get("budget") is None or not man.get("seeds"):
        raise SystemExit("scaffold: manifest without seeds/budget (set N_SEEDS and BUDGET from the pilot first)")
    out, bud = [], man["budget"]
    spec = ",".join(str(x) for x in sorted({50, 250, 2000, bud} | set(range(2500, bud + 1, 2500))))
    for s in man["seeds"]:
        for arm, bs in man["arms"].items():
            for a in "FG":
                out.append(f"{c1.interp(man)} {FB} --seed {s} --condition baseline --threads {man['threads']} --device {man['device']} "
                           f"--test-file lab/confirm/l0_splits/{stem(s, 'test')}.npy --out-root lab/confirm/l0_raw "
                           f"--split-file lab/confirm/l0_splits/{stem(s, a)}.npy --steps {bud} --stop-after-gen {bud} "
                           f"--spectra-at {spec} --batch-size {bs}")
    return out


def expected_run_id(cmd: list[str]) -> str:
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    rid = f"EXP-018_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}"
    if g("--batch-size") and int(g("--batch-size")):
        rid += f"_bs{int(g('--batch-size'))}"
    if g("--order") and g("--order") != "iid":
        rid += f"_ord{g('--order')}"
    dev = g("--device") or "cpu"
    return rid + ("" if dev == "cpu" else f"_dev{dev.replace(':', '')}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


def require_set() -> None:
    if N_SEEDS is None or BUDGET is None or not 1 <= N_SEEDS <= 80:
        raise SystemExit("scaffold: set N_SEEDS (1..80, seeds 3720-3799) and BUDGET from the pilot first")


_a43 = None


def a43():
    global _a43
    if _a43 is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("exp043_analyze", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
        _a43 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_a43)
    return _a43


BLOCK = Block(name="confirm_l0", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_l0.py")


def one_run(man: dict, s: int, a: str, bs: int) -> np.ndarray | str:
    sp, te = SPL / f"{stem(s, a)}.npy", SPL / f"{stem(s, 'test')}.npy"
    cmd = ["x", FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", man["device"], "--split-file", str(sp),
           "--batch-size", str(bs)]
    d, tag = run_dir(cmd), f"seed {s} {a} bs{bs}"
    if not d.exists():
        return f"{tag}: fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt: {why}"
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=man["budget"], split_file=sp, test_file=te,
                           config={"p": 113, "task": "add", "lr": 1e-3, "weight_decay": 1.0, "train_frac": 0.3, "beta1": 0.9, "beta2": 0.98},
                           snapshots_at=(man["budget"],)))
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    r = L.res
    if r.get("batch_size") != bs or r.get("order", "iid") != "iid" or r.get("optimizer", "adamw") != "adamw":
        return f"{tag}: defekt: recorded batch/order/optimizer differ"
    if (why := BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(sp):
        return f"{tag}: defekt after load: {why or 'split bytes differ'}"
    try:
        pw = a43().group_power(L.snapshot(man["budget"]), "add", 113)[0]
    except Exception as ex:   # any load/transform failure is technical, never an abort (as confirm_r10/r11)
        return f"{tag}: defekt: {type(ex).__name__}: {ex}"
    return pw if np.isfinite(pw).all() else f"{tag}: defekt: non-finite power"


def verdict(rows: list[dict], n_planned: int, rng_: np.random.Generator) -> dict:
    n_tech = sum(1 for r in rows if r.get("technical"))
    if n_tech or len(rows) != n_planned:
        return {"n_technical": n_tech, "verdict": "nicht auswertbar"}
    X = {h: np.array([r[f"dpow_{arm}"] for r in rows]) for h, arm in HYP.items()}
    p = {h: c1.t_test_secondary(x)["p_one_sided"] for h, x in X.items()}
    ph = c1.holm(p)
    out: dict = {"n": len(rows)}
    for h, x in X.items():
        ci = c1.boot_ci(x, rng_)
        out[h] = {"arm": HYP[h], "mean": float(x.mean()), "ci95": ci, "n_positive": int((x > 0).sum()), "p": p[h], "p_holm": ph[h],
                  "verdict": "bestätigt" if ph[h] < ALPHA and ci[0] > 0 else "nicht bestätigt"}
    return out


def analyze(manifest: Path) -> None:
    require_set()
    stale = LAB / "confirm" / "L0_summary.json"
    if stale.exists():
        stale.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for m in (split_mismatch(s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"L0 splits differ from the registered construction: {bad[:3]}")
    rows = []
    for s in man["seeds"]:
        meta = json.loads((SPL / f"l0_seed{s}.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["F"], meta["targets"]["G"]
        row: dict = {"seed": s, "technical": False}
        for arm, bs in man["arms"].items():
            pF, pG = one_run(man, s, "F", bs), one_run(man, s, "G", bs)
            d = None if isinstance(pF, str) or isinstance(pG, str) else c1.delta_pow_checked(pF, pG, F, G)
            if d is None:
                why = pF if isinstance(pF, str) else pG if isinstance(pG, str) else "dpow not finite or a target power sum <= 0"
                row["technical"], row["reason"] = True, f"{arm}: {why}"
                break
            row[f"dpow_{arm}"] = d
        rows.append(row)
    out = {"manifest_commit": man["commit"], "hypotheses": verdict(rows, len(man["seeds"]), np.random.default_rng(20)), "rows": rows}
    (LAB / "confirm/L0_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    require_set()
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    tj = trainer_jobs(man)
    assert len(tj) == N_SEEDS * 4 and len(set(tj)) == len(tj)
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert len(set(ids)) == len(ids) and ids[0].endswith("_bs256_devcuda"), ids[0]
    BLOCK.check_job(man, shlex.split(tj[0]))
    for s in REGISTERED["seeds"][:2]:
        F, G = targets(s)
        assert not set(F) & set(G) and not (set(F) | set(G)) & set(O)
    rng_ = np.random.default_rng(0)
    yes = [{"technical": False, "dpow_iid256": 5 + rng_.normal(0, 1), "dpow_iid64": 5 + rng_.normal(0, 1)} for _ in range(N_SEEDS)]
    v = verdict(yes, N_SEEDS, rng_)
    assert v["H1"]["verdict"] == v["H2"]["verdict"] == "bestätigt", v
    no = [{"technical": False, "dpow_iid256": rng_.normal(0, 1), "dpow_iid64": rng_.normal(0, 1)} for _ in range(N_SEEDS)]
    assert verdict(no, N_SEEDS, rng_)["H1"]["verdict"] == "nicht bestätigt"
    assert verdict(yes[:-1], N_SEEDS, rng_)["verdict"] == "nicht auswertbar"
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    print("[confirm_l0] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
