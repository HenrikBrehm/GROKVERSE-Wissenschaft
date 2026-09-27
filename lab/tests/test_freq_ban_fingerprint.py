"""Tests for the Astra-3 changes in freq_ban.py (session 13): fingerprint, legacy skip check, run lock, atomic arrays,
'completed' only after the artifact check. Plain script (no pytest needed); tiny CPU runs (20 steps) in a temp dir.

Run ONLY through the guard, inside the run window:
    python lab/tools/guarded_run.py --min-minutes 5 -- python lab/tests/test_freq_ban_fingerprint.py
Exit 0 = all tests passed.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FB = ROOT / "lab/experiments/EXP-001-freq-ban/freq_ban.py"
SPLIT = ROOT / "lab/experiments/EXP-016-engineered-split/splits/split_seed10_eps2.0.npy"
SPLIT_OTHER = ROOT / "lab/experiments/EXP-016-engineered-split/splits/split_seed11_eps2.0.npy"
sys.path.insert(0, str(FB.parent))
import freq_ban as fb  # noqa: E402

RUN_DIR = "EXP-016_baseline_seed10_thr1_split_seed10_eps2.0"


def ns(**kw) -> argparse.Namespace:
    base = dict(seed=10, condition="baseline", t0=2000, m=5, steps=20, stop_after_gen=2000, threads=1, split_seed=None,
                switch_step=None, split_value=None, warmup=0, alternate_every=0, reset_at_switch=None, lr_scale=1.0,
                we_init_scale=1.0, spectra_at="", p=113, task="add", arch="transformer", device="cpu", save_model=False,
                split_file=str(SPLIT), test_file=None, switch_split_file=None)
    base.update(kw)
    return argparse.Namespace(**base)


def train(out: Path, *extra: str) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(FB), "--seed", "10", "--condition", "baseline", "--threads", "1",
           "--split-file", str(SPLIT), "--out-root", str(out), *extra]
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=600)


def test_fingerprint_unit() -> None:
    f1, fields = fb.run_fingerprint(ns())
    assert f1 == fb.run_fingerprint(ns())[0], "fingerprint must be deterministic"
    for change in (dict(steps=30), dict(stop_after_gen=100), dict(device="cuda"), dict(spectra_at="10"),
                   dict(save_model=True), dict(split_file=str(SPLIT_OTHER)), dict(threads=2), dict(m=3)):
        assert fb.run_fingerprint(ns(**change))[0] != f1, f"fingerprint ignores {change}"
    assert fields["split_file_sha256"] == fb.file_sha256(str(SPLIT)) and fields["test_file_sha256"] is None
    assert fb.run_fingerprint(ns(spectra_at="10,5"))[0] == fb.run_fingerprint(ns(spectra_at="5,10"))[0]
    # session 18: a late argument enters the fingerprint only when it differs from its default, so existing runs keep
    # their fingerprints (a namespace without the attribute = a record from before the argument existed)
    assert "lr_scale_after_switch" not in fields
    assert fb.run_fingerprint(ns(lr_scale_after_switch=1.0))[0] == f1, "default late argument changed the fingerprint"
    # anchor to the pre-session-18 algorithm (Codex s18): FINGERPRINT_ARGS + sorted spectra + file hashes + version only
    import hashlib
    a0 = ns()
    old_fields = {k: getattr(a0, k) for k in fb.FINGERPRINT_ARGS}
    old_fields["spectra_at"] = []
    old_fields.update({f"{k}_sha256": fb.file_sha256(getattr(a0, k)) for k in fb.FINGERPRINT_FILES})
    old_fields["fingerprint_version"] = 1
    blob = json.dumps(old_fields, sort_keys=True, separators=(",", ":"), default=str)
    assert f1 == hashlib.sha256(blob.encode()).hexdigest(), "default fingerprint differs from the pre-session-18 algorithm"
    S, c = 150, 3.0                                                     # ELR window: exactly steps S+1 .. S+500
    assert [fb.lr_mult_after_switch(t, S, c) for t in (S, S + 1, S + 500, S + 501)] == [1.0, c, c, 1.0]
    assert sum(fb.lr_mult_after_switch(t, S, c) == c for t in range(1, 2000)) == fb.LR_AFTER_SWITCH_STEPS
    assert fb.run_fingerprint(ns(lr_scale_after_switch=3.0))[0] != f1, "fingerprint ignores --lr-scale-after-switch"


def test_pid_and_atomic_unit(tmp: Path) -> None:
    import time
    assert fb._pid_alive_since(os.getpid(), time.time()), "own process must count as alive"
    assert not fb._pid_alive_since(4_000_000, time.time()), "a non-existent pid must count as dead"
    assert not fb._pid_alive_since(os.getpid(), 0.0), "a process created after the lock time is PID reuse"
    import numpy as np
    target = tmp / "x_eps2.0.npy"
    fb.save_npy_atomic(target, np.arange(5))
    assert (np.load(target) == np.arange(5)).all() and not list(tmp.glob("*.tmp")), "atomic save left a tmp file"


def test_integration(tmp: Path) -> None:
    out = tmp / "raw"
    r = train(out, "--steps", "20")
    assert r.returncode == 0, r.stdout + r.stderr
    d = out / RUN_DIR
    res = json.loads((d / "result.json").read_text())
    assert res["status"] == "completed" and res["steps_completed"] == 20 and "fingerprint" in res, res.get("status")
    assert res["config"]["device"] == "cpu", "config.device must record the real device"
    assert not (d / fb.LOCK_NAME).exists(), "lock not released after a completed run"
    assert not list(d.glob("*.tmp")), "temporary files left behind"

    r = train(out, "--steps", "20")                                   # identical request -> skip, exit 0
    assert r.returncode == 0 and "already completed" in r.stdout, r.stdout + r.stderr

    r = train(out, "--steps", "20", "--lr-scale-after-switch", "3")   # session 18: ELR arm needs a data switch
    assert r.returncode != 0 and "--lr-scale-after-switch needs" in (r.stdout + r.stderr), r.stdout + r.stderr

    r = train(out, "--steps", "30")                                   # Astra's failure case: other budget, same run id
    assert r.returncode != 0 and "another configuration" in (r.stdout + r.stderr), r.stdout + r.stderr

    legacy = dict(res)                                                # a pre-fingerprint record with another budget
    legacy.pop("fingerprint")
    legacy["max_steps"] = 50
    (d / "result.json").write_text(json.dumps(legacy))
    r = train(out, "--steps", "20")
    assert r.returncode != 0 and "pre-fingerprint" in (r.stdout + r.stderr) and "max_steps" in (r.stdout + r.stderr), \
        r.stdout + r.stderr
    legacy["max_steps"] = 20                                          # matching legacy record -> skip
    (d / "result.json").write_text(json.dumps(legacy))
    r = train(out, "--steps", "20")
    assert r.returncode == 0 and "already completed" in r.stdout, r.stdout + r.stderr

    import time
    (d / fb.LOCK_NAME).write_text(json.dumps({"pid": os.getpid(), "created_unix": time.time()}))   # live holder
    r = train(out, "--steps", "20", "--force")
    assert r.returncode != 0 and "locked" in (r.stdout + r.stderr), r.stdout + r.stderr
    (d / fb.LOCK_NAME).write_text(json.dumps({"pid": 4_000_000, "created_unix": time.time()}))     # stale lock
    r = train(out, "--steps", "20", "--force")
    assert r.returncode == 0, r.stdout + r.stderr
    assert not (d / fb.LOCK_NAME).exists()


def test_verify_artifacts(tmp: Path) -> None:
    import numpy as np
    d = tmp / "art"
    d.mkdir()
    np.save(d / "spectra.npy", np.ones((2, 56)))
    np.save(d / "spectra_steps.npy", np.array([0, 20]))
    fb.verify_artifacts(d, 20, set(), False)
    for bad in (lambda: np.save(d / "spectra_steps.npy", np.array([0, 10])),
                lambda: np.save(d / "spectra.npy", np.array([[1.0] * 56, [np.nan] * 56]))):
        np.save(d / "spectra.npy", np.ones((2, 56)))
        np.save(d / "spectra_steps.npy", np.array([0, 20]))
        bad()
        try:
            fb.verify_artifacts(d, 20, set(), False)
        except SystemExit:
            continue
        raise AssertionError("verify_artifacts accepted a broken record")


def test_rewind(tmp: Path) -> None:
    """EXP-073 (session 24): rewinding ALL parameters (weights + AdamW state) to step R at the switch step t must reproduce
    the run that switches at R (constant lr, no step-dependent schedule); a partial rewind must differ; the fingerprint of
    runs without the option stays unchanged; invalid combinations are refused."""
    import numpy as np
    f1 = fb.run_fingerprint(ns())[0]
    assert fb.run_fingerprint(ns(rewind_at_switch=None, rewind_from=None))[0] == f1, "default rewind arguments changed the fingerprint"
    assert fb.run_fingerprint(ns(rewind_at_switch="vo", rewind_from=5))[0] != f1, "fingerprint ignores --rewind-at-switch"
    out = tmp / "rw"
    spl = ROOT / "lab/experiments/EXP-056-overlap-persistence/splits"     # Codex s24: switch runs need a common test set
    base = [sys.executable, str(FB), "--seed", "400", "--condition", "baseline", "--threads", "1", "--out-root", str(out),
            "--split-file", str(spl / "seed400_w0_A.npy"), "--switch-split-file", str(spl / "seed400_w0_B.npy"),
            "--test-file", str(spl / "seed400_test.npy"), "--save-model"]
    run = lambda *x: subprocess.run(base + list(x), cwd=ROOT, capture_output=True, text=True, timeout=600)   # noqa: E731
    r_ref = run("--steps", "25", "--switch-step", "10")
    r_all = run("--steps", "30", "--switch-step", "15", "--rewind-at-switch", "all", "--rewind-from", "10")
    r_vo = run("--steps", "30", "--switch-step", "15", "--rewind-at-switch", "vo", "--rewind-from", "10")
    for r in (r_ref, r_all, r_vo):
        assert r.returncode == 0, r.stdout + r.stderr
    import torch
    d = {}
    for k in ("at10", "rwall10", "rwvo10"):
        hits = list(out.glob(f"*{k}"))
        assert len(hits) == 1, (k, hits)
        d[k] = hits[0]
    m = {k: torch.load(v / "model_final.pt", map_location="cpu") for k, v in d.items()}
    assert all(torch.equal(m["at10"][n], m["rwall10"][n]) for n in m["at10"]), "rewind all != switch at R"
    assert not torch.equal(m["at10"]["W_E"], m["rwvo10"]["W_E"]), "partial rewind indistinguishable from switch at R"
    ev = json.loads((d["rwvo10"] / "result.json").read_text(encoding="utf-8"))["events"]["rewind_at_switch"]
    assert ev["check"] is True and ev["names"] == ["W_V", "W_O"] and ev["from_step"] == 10, ev
    sp = {k: np.load(v / "spectra.npy")[-1] for k, v in d.items()}
    assert np.array_equal(sp["at10"], sp["rwall10"])
    assert set(ev["diag_before"]) == {"new", "old"} and len(ev["diag_after"]["new"]) == 2, ev
    for bad in (("--rewind-at-switch", "vo"), ("--rewind-at-switch", "vo", "--rewind-from", "15"),
                ("--rewind-at-switch", "vo", "--rewind-from", "5", "--reset-at-switch", "qk")):
        r = run("--steps", "30", "--switch-step", "15", *bad)
        assert r.returncode != 0, bad
    rb = subprocess.run([x if x != "baseline" else "ban_random" for x in base] + ["--steps", "30", "--switch-step", "15",
                        "--rewind-at-switch", "vo", "--rewind-from", "5"], cwd=ROOT, capture_output=True, text=True, timeout=600)
    assert rb.returncode != 0 and "--condition baseline" in (rb.stdout + rb.stderr), rb.stdout + rb.stderr


def main() -> int:
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        for name, fn in (("fingerprint_unit", lambda: test_fingerprint_unit()),
                         ("pid_and_atomic_unit", lambda: test_pid_and_atomic_unit(tmp)),
                         ("verify_artifacts", lambda: test_verify_artifacts(tmp)),
                         ("integration", lambda: test_integration(tmp)),
                         ("rewind", lambda: test_rewind(tmp))):
            fn()
            print(f"[test_freq_ban_fingerprint] {name} ok", flush=True)
    print("[test_freq_ban_fingerprint] all ok", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
