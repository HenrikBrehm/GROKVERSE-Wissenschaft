"""Shared, versioned result loader for lab analyses (Astra review point 16, session 13). Read-only, no training.

One place that decides whether a stored run may enter a verdict. It separates three outcomes:
  "fehlt"   no run directory / no result.json (not run yet, or refused by the guard)
  "defekt"  technically unusable: not completed, wrong seed/device/budget/data/task, missing or non-finite arrays
  "ok"      usable; the scientific result (positive or negative) is then up to the analysis
Works for freq_ban.py, group_train.py (EXP-046), intadd_train.py (EXP-048) and width_train.py (EXP-049) records.

    from result_loader import Expect, find_run, load_run
    r = load_run(find_run(root, pattern), Expect(seed=150, device="cuda", max_steps=2000, split_file=path, at=(2000,)))
    if r.status != "ok": ... r.reason ...
    pw = r.spectrum(2000)
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

LOADER_VERSION = 1


def sorted_hash(idx: np.ndarray) -> str:
    """Same as grokverse.data.split_hash (sha256 of the sorted int64 little-endian indices), without importing torch."""
    return hashlib.sha256(np.sort(np.asarray(idx, dtype=np.int64)).astype("<i8").tobytes()).hexdigest()


@dataclass(frozen=True)
class Expect:
    seed: int
    device: str
    max_steps: int                          # the requested step budget (result.json "max_steps")
    min_steps_completed: int | None = None  # default: max_steps (runs that may stop early set a lower bound)
    split_file: str | Path | None = None    # train split .npy -> result "split_hash"
    test_file: str | Path | None = None     # -> "test_hash"
    switch_file: str | Path | None = None   # -> "switch_hash"
    config: dict = field(default_factory=dict)   # e.g. {"p": 113, "task": "add", "arch": "transformer", "d_model": 512}
    at: tuple[int, ...] = ()                # spectra.npy must hold these steps (finite)
    snapshots_at: tuple[int, ...] = ()      # we_snapshots.npy must hold these steps (finite)
    files: tuple[str, ...] = ()             # further files that must exist and be finite (.npy)


@dataclass
class Loaded:
    status: str
    reason: str = ""
    path: Path | None = None
    res: dict = field(default_factory=dict)
    _spec: dict = field(default_factory=dict)
    _snap: dict = field(default_factory=dict)

    def spectrum(self, step: int) -> np.ndarray:
        return self._spec[step]

    def snapshot(self, step: int) -> np.ndarray:
        return self._snap[step]


def find_run(root: Path, pattern: str) -> Path | None:
    """Exactly one directory matching the glob, else None (ambiguous counts as missing and is reported as such)."""
    hits = sorted(p for p in Path(root).glob(pattern) if p.is_dir())
    return hits[0] if len(hits) == 1 else None


def _steps_array(d: Path, spec_name: str, steps_name: str, want: tuple[int, ...]) -> tuple[dict, str]:
    if not want:
        return {}, ""
    if not (d / spec_name).exists() or not (d / steps_name).exists():
        return {}, f"{spec_name} missing"
    arr, steps = np.load(d / spec_name), np.load(d / steps_name).tolist()
    if len(arr) != len(steps):
        return {}, f"{spec_name}: {len(arr)} rows for {len(steps)} steps"
    out = {}
    for t in want:
        if t not in steps:
            return {}, f"{spec_name}: no entry at step {t}"
        v = np.asarray(arr[steps.index(t)], dtype=np.float64)
        if not np.isfinite(v).all():
            return {}, f"{spec_name}: non-finite at step {t}"
        out[t] = v
    return out, ""


def load_run(d: Path | None, e: Expect) -> Loaded:
    if d is None or not (Path(d) / "result.json").exists():
        return Loaded("fehlt", "no (unique) run directory / result.json", d)
    d = Path(d)
    try:
        res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as ex:
        return Loaded("defekt", f"result.json unreadable: {type(ex).__name__}", d)
    bad = lambda why: Loaded("defekt", why, d, res)   # noqa: E731
    if res.get("status") != "completed":
        return bad(f"status {res.get('status')!r}")
    if res.get("seed") != e.seed:
        return bad(f"seed {res.get('seed')} != {e.seed}")
    device = res.get("device", "cpu")                  # records from before rule 16 (no field) ran on the CPU
    if device != e.device:
        return bad(f"device {device!r} != {e.device!r}")
    if res.get("max_steps") != e.max_steps:
        return bad(f"max_steps {res.get('max_steps')} != {e.max_steps}")
    need = e.max_steps if e.min_steps_completed is None else e.min_steps_completed
    if not isinstance(res.get("steps_completed"), int) or res["steps_completed"] < need:
        return bad(f"steps_completed {res.get('steps_completed')} < {need}")
    for key, path in (("split_hash", e.split_file), ("test_hash", e.test_file), ("switch_hash", e.switch_file)):
        if path is not None and res.get(key) != sorted_hash(np.load(path)):
            return bad(f"{key} does not match {Path(path).name}")
    cfg = res.get("config", {})
    for key, want in e.config.items():
        got = cfg.get(key, res.get(key))
        if got != want:
            return bad(f"config {key} {got!r} != {want!r}")
    spec, why = _steps_array(d, "spectra.npy", "spectra_steps.npy", e.at)
    if why:
        return bad(why)
    snap, why = _steps_array(d, "we_snapshots.npy", "we_snapshot_steps.npy", e.snapshots_at)
    if why:
        return bad(why)
    for f in e.files:
        if not (d / f).exists():
            return bad(f"{f} missing")
        if f.endswith(".npy") and not np.isfinite(np.load(d / f)).all():
            return bad(f"{f} non-finite")
    return Loaded("ok", "", d, res, spec, snap)


def selftest() -> None:
    """Fail closed on synthetic run directories (writes only into a temporary directory)."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        split = root / "split.npy"
        np.save(split, np.array([5, 1, 3], dtype=np.int64))
        d = root / "EXP-X_seed1_run"
        d.mkdir()
        base = {"status": "completed", "seed": 1, "device": "cuda", "max_steps": 10, "steps_completed": 10,
                "split_hash": sorted_hash(np.array([1, 3, 5])), "config": {"p": 113, "task": "add"}}
        (d / "result.json").write_text(json.dumps(base))
        np.save(d / "spectra.npy", np.ones((2, 4)))
        np.save(d / "spectra_steps.npy", np.array([0, 10]))
        e = Expect(seed=1, device="cuda", max_steps=10, split_file=split, config={"p": 113}, at=(10,))
        assert load_run(find_run(root, "EXP-X_seed1_*"), e).status == "ok"
        assert load_run(find_run(root, "nothing_*"), e).status == "fehlt"
        for patch, word in (({"seed": 2}, "seed"), ({"device": "cpu"}, "device"), ({"max_steps": 50}, "max_steps"),
                            ({"steps_completed": 5}, "steps_completed"), ({"status": "running"}, "status"),
                            ({"split_hash": "x"}, "split_hash"), ({"config": {"p": 97}}, "config")):
            (d / "result.json").write_text(json.dumps({**base, **patch}))
            r = load_run(d, e)
            assert r.status == "defekt" and word in r.reason, (patch, r.reason)
        (d / "result.json").write_text(json.dumps(base))
        np.save(d / "spectra.npy", np.array([[1.0] * 4, [np.nan] * 4]))
        assert "non-finite" in load_run(d, e).reason
        np.save(d / "spectra.npy", np.ones((2, 4)))
        assert "no entry" in load_run(d, Expect(seed=1, device="cuda", max_steps=10, at=(5,))).reason
    print("[result_loader] selftest ok", flush=True)


if __name__ == "__main__":
    selftest()
