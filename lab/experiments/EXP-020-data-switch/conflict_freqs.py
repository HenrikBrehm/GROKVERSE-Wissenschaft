"""EXP-020 Nachtrag d (session 9): "foreign" frequencies in mixed states. Descriptive, secondary; no training.

Definition (fixed 2026-09-26 14:52 Berlin (commit 7537783), after seeing seeds 30-32, BEFORE any run of seeds 33/34):
  A_s = F u G u {fold(2k) : k in F u G} u K_onlyF u K_onlyG   (K_only* = top-5 of the pure runs at step 2000)
  foreign(t) = top-5 of the switched run at step t + 2000 minus A_s
  early = t in {10, 25, 50}, late = t in {150, 400, 1000}
  init rank = rank (1 = strongest of 56) in the step-0 W_E spectrum (identical in all runs of a seed)
Predictions for the fresh seeds 33, 34 (each seed judged separately, must be valid = all 8 runs present):
  P-d1: at least one foreign frequency in at least one early run, and none in any late run.
  P-d2: pooled over both seeds, the median init rank of the distinct foreign frequencies (per seed) is <= 14.
Seeds 30-32 are exploration and are only reported.
Nachtrag d-1 (~15:00, after Codex review, before any seed-33/34 run finished): runs are accepted only through the
fail-closed loader `load_run` (result.json completed, seed, exact steps, split/test/switch hashes, one init checksum per
seed, finite spectra); definitions and criteria unchanged. `load_run` is shared with EXP-036.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "training"))
from grokverse.data import split_hash  # noqa: E402

P, M, G_BUDGET = 113, 5, 2000
EARLY, LATE = (10, 25, 50), (150, 400, 1000)
FRESH = (33, 34)
SPLITS = HERE / "splits"


def fold(k: int) -> int:
    k %= P
    return min(k, P - k)


def ranks(pw: np.ndarray) -> dict[int, int]:
    order = np.lexsort((np.arange(len(pw)), -pw))
    return {int(k) + 1: r + 1 for r, k in enumerate(order)}


def top(pw: np.ndarray) -> set[int]:
    return {k for k, r in ranks(pw).items() if r <= M}


def run_name(init: int, s: int, arm: str, t: int | None, suffix: str = "") -> str:
    if t is None:
        return f"EXP-018_baseline_seed{init}_thr4_seed{s}_train_{arm}{suffix}"
    return f"EXP-020_baseline_seed{init}_thr4_seed{s}_train_F_to_seed{s}_train_G_at{t}{suffix}"


def load_run(root: Path, init: int, s: int, arm: str, t: int | None, max_steps: int | None,
             steps: tuple[int, ...], suffix: str = "") -> tuple[dict | None, str | None]:
    """Fail-closed loader. arm 'F'/'G' for pure runs (t None), 'FG' for a switch at t. Returns
    {'spec': {step: power}, 'init_checksum': str, 'test_acc': float} or (None, reason)."""
    name = run_name(init, s, arm if t is None else "F", t, suffix)
    d = root / name
    try:
        res = json.loads((d / "result.json").read_text(encoding="utf-8"))
        spec, sst = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()
    except (OSError, ValueError) as e:
        return None, f"{name}: unreadable ({type(e).__name__})"
    if res.get("status") != "completed" or res.get("seed") != init:
        return None, f"{name}: status/seed"
    want = max_steps if max_steps is not None else (t + G_BUDGET if t is not None else None)
    if want is not None and res.get("max_steps") != want:
        return None, f"{name}: max_steps {res.get('max_steps')} != {want}"
    if t is not None and res.get("steps_completed") != want:
        return None, f"{name}: steps_completed {res.get('steps_completed')} != {want}"
    first = "G" if (t is None and arm == "G") else "F"
    if res.get("split_hash") != split_hash(np.load(SPLITS / f"seed{s}_train_{first}.npy")):
        return None, f"{name}: split hash"
    if res.get("test_hash") != split_hash(np.load(SPLITS / f"seed{s}_test.npy")):
        return None, f"{name}: test hash"
    if t is not None:
        sw = res.get("events", {}).get("switch", {})
        if (res.get("switch_step") != t or sw.get("step") != t
                or sw.get("new_train_hash") != split_hash(np.load(SPLITS / f"seed{s}_train_G.npy"))):
            return None, f"{name}: switch not as specified"
    out = {}
    for st in steps:
        if st not in sst or st > res.get("steps_completed", -1):
            return None, f"{name}: no spectrum at step {st}"
        pw = spec[sst.index(st)]
        if not np.all(np.isfinite(pw)):
            return None, f"{name}: non-finite spectrum at {st}"
        out[st] = pw
    return {"spec": out, "init_checksum": res.get("init_checksum_shared"),
            "test_acc": res.get("final_acc", {}).get("test"), "result": res}, None


def foreign_sets(root: Path, init: int, s: int, ts: tuple[int, ...], pure_f_max: int | None
                 ) -> tuple[dict | None, str | None]:
    """Validated foreign sets per t for one (init, split). pure_f_max: max_steps of the pure F run
    (EXP-020: 8000, EXP-036: 2000)."""
    tg = json.loads((SPLITS / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
    fg = set(tg["F"]) | set(tg["G"])
    pf, e1 = load_run(root, init, s, "F", None, pure_f_max, (0, G_BUDGET))
    pg, e2 = load_run(root, init, s, "G", None, G_BUDGET, (0, G_BUDGET))
    if e1 or e2:
        return None, e1 or e2
    allowed = fg | {fold(2 * k) for k in fg} | top(pf["spec"][G_BUDGET]) | top(pg["spec"][G_BUDGET])
    checks = {pf["init_checksum"], pg["init_checksum"]}
    foreign, acc = {}, {}
    for t in ts:
        r, e = load_run(root, init, s, "FG", t, None, (0, t + G_BUDGET))
        if e:
            return None, e
        checks.add(r["init_checksum"])
        foreign[t] = sorted(top(r["spec"][t + G_BUDGET]) - allowed)
        acc[t] = r["test_acc"]
    if len(checks) != 1 or None in checks:
        return None, f"init {init} split {s}: init checksums differ across runs"
    return {"foreign": foreign, "test_acc": acc, "init_spec": pf["spec"][0], "A_size": len(allowed),
            "init_checksum": checks.pop()}, None


def main() -> None:
    rows = []
    for s in range(30, 35):
        r, err = foreign_sets(HERE / "raw", s, s, (*EARLY, *LATE), 8000)
        if err:
            print(f"seed {s}: not complete ({err})")
            continue
        init_r = ranks(r["init_spec"])
        distinct = sorted({k for v in r["foreign"].values() for k in v})
        row = {"seed": s, "A_size": r["A_size"], "foreign": r["foreign"], "test_acc": r["test_acc"],
               "init_ranks": {k: init_r[k] for k in distinct},
               "early_any": any(r["foreign"][t] for t in EARLY), "late_none": not any(r["foreign"][t] for t in LATE)}
        rows.append(row)
        tag = "fresh" if s in FRESH else "exploration"
        print(f"seed {s} ({tag}): foreign={row['foreign']} init_ranks={row['init_ranks']} "
              f"early_any={row['early_any']} late_none={row['late_none']}")
    fresh = [r for r in rows if r["seed"] in FRESH]
    for r in fresh:
        print(f"P-d1 seed {r['seed']}: {'met' if r['early_any'] and r['late_none'] else 'not met'}")
    if len(fresh) == len(FRESH):
        pooled = [v for r in fresh for v in r["init_ranks"].values()]
        med = float(np.median(pooled)) if pooled else float("nan")
        print(f"P-d2: median init rank {med} over {len(pooled)} freqs -> {'met' if pooled and med <= 14 else 'not met'}")
    else:
        print(f"P-d2: not evaluable yet ({len(fresh)}/{len(FRESH)} fresh seeds complete)")
    (HERE / "conflict_freqs.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
