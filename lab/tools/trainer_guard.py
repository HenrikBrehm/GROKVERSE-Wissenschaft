#!/usr/bin/env python3
"""Resume guard for the small trainers (EXP-046 group_train, EXP-048 intadd_train, EXP-049 width_train).

Session 19: these trainers skipped a run on `status == "completed"` alone, so a finished run with another
configuration under the same run id would be skipped silently (Codex hint, session 18 cycle 4). Same idea as the
fingerprint in freq_ban.py (Astra 3), kept minimal: sha256 over every effective argument (not out_root/force, not
the split PATH) plus the sha256 of the split file CONTENT.

    skip  : completed, same fingerprint, steps_completed == requested steps
    run   : no result.json, unreadable result.json, or an unfinished run with the same fingerprint (retrained
            from scratch; these trainers have no checkpoints)
    abort : any existing result.json with another or a missing fingerprint (fail closed; --force or another
            --out-root overrides)

Self-test (no torch, no training): python lab/tools/trainer_guard.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

NOT_IN_FINGERPRINT = ("out_root", "force", "split_file")
FINGERPRINT_VERSION = 1


def file_sha256(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def config_fingerprint(a: argparse.Namespace) -> tuple[str, dict]:
    fields = {k: v for k, v in sorted(vars(a).items()) if k not in NOT_IN_FINGERPRINT}
    fields["split_file_sha256"] = file_sha256(a.split_file)
    fields["fingerprint_version"] = FINGERPRINT_VERSION
    blob = json.dumps(fields, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode()).hexdigest(), fields


def should_skip(rj: Path, fingerprint: str, steps: int, force: bool, tag: str, run_id: str) -> bool:
    """True = skip (already done with this configuration); False = train; SystemExit(2) = refuse."""
    if force or not rj.exists():
        return False
    try:
        old = json.loads(rj.read_text())
    except (OSError, ValueError):
        print(f"[{tag}] {run_id}: unreadable result.json, retraining", flush=True)
        return False
    if old.get("config_fingerprint") != fingerprint:
        print(f"[{tag}] {run_id}: existing result.json has another configuration "
              f"({str(old.get('config_fingerprint'))[:12]} != {fingerprint[:12]}); "
              f"not overwritten, use --force or another --out-root", file=sys.stderr, flush=True)
        raise SystemExit(2)
    if old.get("status") == "completed" and old.get("steps_completed") == steps:
        print(f"[{tag}] {run_id} already completed; use --force to overwrite", flush=True)
        return True
    return False


def _selftest() -> None:
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        split = d / "s.npy"
        split.write_bytes(b"abc")
        ns = argparse.Namespace(seed=1, steps=50, split_file=str(split), out_root="x", force=False, device="cpu")
        fp, fields = config_fingerprint(ns)
        assert "split_file" not in fields and "out_root" not in fields and fields["split_file_sha256"]
        # same content under another path and another out_root -> same fingerprint
        split2 = d / "t.npy"
        split2.write_bytes(b"abc")
        assert config_fingerprint(argparse.Namespace(**{**vars(ns), "split_file": str(split2), "out_root": "y",
                                                         "force": True}))[0] == fp
        # any effective argument or the split content changes it
        assert config_fingerprint(argparse.Namespace(**{**vars(ns), "steps": 51}))[0] != fp
        split2.write_bytes(b"abd")
        assert config_fingerprint(argparse.Namespace(**{**vars(ns), "split_file": str(split2)}))[0] != fp
        rj = d / "result.json"
        assert should_skip(rj, fp, 50, False, "t", "r") is False                     # nothing there
        rj.write_text("{not json")
        assert should_skip(rj, fp, 50, False, "t", "r") is False                     # broken -> retrain
        rj.write_text(json.dumps({"status": "completed", "steps_completed": 50, "config_fingerprint": fp}))
        assert should_skip(rj, fp, 50, False, "t", "r") is True                      # done -> skip
        assert should_skip(rj, fp, 60, False, "t", "r") is False                     # other budget, same fp
        assert should_skip(rj, fp, 50, True, "t", "r") is False                      # --force
        rj.write_text(json.dumps({"status": "running", "steps_completed": 20, "config_fingerprint": fp}))
        assert should_skip(rj, fp, 50, False, "t", "r") is False                     # unfinished -> retrain
        for bad in ({"status": "completed", "steps_completed": 50, "config_fingerprint": "other"},
                    {"status": "completed", "steps_completed": 50}):                 # other / missing fp
            rj.write_text(json.dumps(bad))
            try:
                should_skip(rj, fp, 50, False, "t", "r")
            except SystemExit as e:
                assert e.code == 2
            else:
                raise AssertionError("mismatch must refuse")
    print("trainer_guard selftest: OK")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        _selftest()
    else:
        raise SystemExit(__doc__)
