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


def test_hp_overrides(tmp: Path) -> None:
    """Rule 19a (session 24): --lr / --weight-decay / --train-frac reach the config, change fingerprint and run id only when given,
    and invalid values are refused."""
    f1 = fb.run_fingerprint(ns())[0]
    assert fb.run_fingerprint(ns(lr=None, weight_decay=None, train_frac=None))[0] == f1, "default overrides changed the fingerprint"
    assert fb.run_fingerprint(ns(lr=2e-3))[0] != f1 and fb.run_fingerprint(ns(weight_decay=0.3))[0] != f1
    assert fb.hp_overrides(ns()) == {} and fb.hp_overrides(ns(lr=2e-3, weight_decay=0.0)) == {"lr": 2e-3, "weight_decay": 0.0}
    out = tmp / "hp"
    r = train(out, "--steps", "20", "--lr", "0.002", "--weight-decay", "0.5")
    assert r.returncode == 0, r.stdout + r.stderr
    hits = list(out.glob("*_lr0.002_wd0.5"))
    assert len(hits) == 1, list(out.iterdir())
    cfg = json.loads((hits[0] / "result.json").read_text(encoding="utf-8"))["config"]
    assert cfg["lr"] == 0.002 and cfg["weight_decay"] == 0.5 and cfg["train_frac"] == 0.3, cfg
    r = train(out, "--steps", "20", "--beta1", "0.8", "--beta2", "0.995")      # session 39 (EXP-081): betas reach the config
    assert r.returncode == 0, r.stdout + r.stderr
    hits = list(out.glob("*_b10.8_b20.995"))
    assert len(hits) == 1, list(out.iterdir())
    cfg = json.loads((hits[0] / "result.json").read_text(encoding="utf-8"))["config"]
    assert cfg["beta1"] == 0.8 and cfg["beta2"] == 0.995 and cfg["lr"] == 0.001, cfg
    assert fb.run_fingerprint(ns(beta1=None, beta2=None))[0] == f1 and fb.run_fingerprint(ns(beta2=0.95))[0] != f1
    for bad in (("--train-frac", "1.5"), ("--lr", "0"), ("--weight-decay", "-1"), ("--train-frac", "0.2"), ("--beta1", "1"), ("--beta2", "0")):   # 0.2: split file has 0.3
        r = train(out, "--steps", "20", *bad)
        assert r.returncode != 0, bad


def test_pre_switch_betas(tmp: Path) -> None:
    """EXP-090 (session 40): --pre-switch-betas. Preset values reproduce the plain switch run bitwise; other values act exactly in
    steps 1..t (W_E at t equals a --beta1/--beta2 run); the beta switch keeps the bias-corrected moments continuous (event check);
    fingerprint/run id change only when given; invalid combinations are refused."""
    import numpy as np
    import torch
    f1 = fb.run_fingerprint(ns())[0]
    assert fb.run_fingerprint(ns(pre_switch_betas=None))[0] == f1, "default --pre-switch-betas changed the fingerprint"
    assert fb.run_fingerprint(ns(pre_switch_betas="0.975,0.995"))[0] != f1, "fingerprint ignores --pre-switch-betas"
    out = tmp / "psb"
    spl = ROOT / "lab/experiments/EXP-056-overlap-persistence/splits"
    base = [sys.executable, str(FB), "--seed", "400", "--condition", "baseline", "--threads", "1", "--out-root", str(out),
            "--split-file", str(spl / "seed400_w0_A.npy"), "--switch-split-file", str(spl / "seed400_w0_B.npy"),
            "--test-file", str(spl / "seed400_test.npy"), "--save-model", "--steps", "25", "--switch-step", "10", "--spectra-at", "10,25"]
    run = lambda *x: subprocess.run(base + list(x), cwd=ROOT, capture_output=True, text=True, timeout=600)   # noqa: E731
    for extra in ((), ("--pre-switch-betas", "0.9,0.98"), ("--pre-switch-betas", "0.8,0.95"), ("--beta1", "0.8", "--beta2", "0.95")):
        r = run(*extra)
        assert r.returncode == 0, (extra, r.stdout + r.stderr)
    d = {}
    for k in ("at10", "at10_psb0.9_0.98", "at10_psb0.8_0.95", "at10_b10.8_b20.95"):
        hits = [h for h in out.glob(f"*{k}") if h.is_dir()]
        assert len(hits) == 1, (k, list(out.iterdir()))
        d[k] = hits[0]
    m = {k: torch.load(v / "model_final.pt", map_location="cpu") for k, v in d.items()}
    assert all(torch.equal(m["at10"][n], m["at10_psb0.9_0.98"][n]) for n in m["at10"]), "preset pre-switch betas != plain run"
    snap = lambda k: np.load(d[k] / "we_snapshots.npy")[list(np.load(d[k] / "we_snapshot_steps.npy")).index(10)]   # noqa: E731
    assert np.array_equal(snap("at10_psb0.8_0.95"), snap("at10_b10.8_b20.95")), "pre-switch betas not used in steps 1..t"
    assert not np.array_equal(snap("at10_psb0.8_0.95"), snap("at10")), "pre-switch betas had no effect"
    assert not torch.equal(m["at10_psb0.8_0.95"]["W_E"], m["at10_b10.8_b20.95"]["W_E"]), "preset betas not restored after the switch"
    res = json.loads((d["at10_psb0.8_0.95"] / "result.json").read_text(encoding="utf-8"))
    ev = res["events"]["pre_switch_betas"]
    assert ev["check"] is True and ev["pre"] == [0.8, 0.95] and ev["post"] == [0.9, 0.98] and ev["step"] == 10.0, ev
    assert abs(ev["factor_m"] - (1 - 0.9 ** 10) / (1 - 0.8 ** 10)) < 1e-12, ev
    assert res["pre_switch_betas"] == [0.8, 0.95] and res["config"]["beta1"] == 0.9, res.get("pre_switch_betas")   # top level, like lr_scale
    for bad in (("--pre-switch-betas", "0.9"), ("--pre-switch-betas", "1,0.98"), ("--pre-switch-betas", "0.9,0.98", "--beta1", "0.8"),
                ("--pre-switch-betas", "0.9,0.98", "--reset-optim-part", "m")):
        r = run(*bad)
        assert r.returncode != 0, bad
    rn = subprocess.run([x for x in base if x not in ("--switch-split-file", str(spl / "seed400_w0_B.npy"), "--switch-step", "10")]
                        + ["--pre-switch-betas", "0.8,0.95"], cwd=ROOT, capture_output=True, text=True, timeout=600)
    assert rn.returncode != 0, "--pre-switch-betas without a switch accepted"


def test_pre_switch_grad_every(tmp: Path) -> None:
    """EXP-095 (session 42): --pre-switch-grad-every k. Before the switch the gradient is computed only at steps 1, 1+k, ...
    and reused in between (same Adam steps, lr, betas); after the switch every step evaluates. Two Adam steps on one reused
    gradient move W_E almost exactly like one step at 2x lr (m_hat = g, v_hat = g^2), unlike two plain steps.
    Fingerprint/run id change only when given; invalid combinations are refused."""
    import numpy as np
    f1 = fb.run_fingerprint(ns())[0]
    assert fb.run_fingerprint(ns(pre_switch_grad_every=1))[0] == f1, "default --pre-switch-grad-every changed the fingerprint"
    assert fb.run_fingerprint(ns(pre_switch_grad_every=2))[0] != f1, "fingerprint ignores --pre-switch-grad-every"
    out = tmp / "ge"
    spl = ROOT / "lab/experiments/EXP-056-overlap-persistence/splits"
    base = [sys.executable, str(FB), "--seed", "400", "--condition", "baseline", "--threads", "1", "--out-root", str(out),
            "--split-file", str(spl / "seed400_w0_A.npy"), "--test-file", str(spl / "seed400_test.npy")]
    sw = ["--switch-split-file", str(spl / "seed400_w0_B.npy")]
    run = lambda *x: subprocess.run(base + list(x), cwd=ROOT, capture_output=True, text=True, timeout=600)   # noqa: E731
    for extra in (sw + ["--steps", "14", "--switch-step", "10", "--spectra-at", "2,10", "--pre-switch-grad-every", "2"],
                  sw + ["--steps", "14", "--switch-step", "10", "--spectra-at", "2,10"],
                  ["--steps", "2", "--spectra-at", "1,2", "--lr-scale", "2"]):
        r = run(*extra)
        assert r.returncode == 0, (extra, r.stdout + r.stderr)
    d = {}
    for k in ("at10_ge2", "at10", "lrs2"):
        hits = [h for h in out.glob(f"*{k}") if h.is_dir()]
        assert len(hits) == 1, (k, list(out.iterdir()))
        d[k] = hits[0]
    snap = lambda k, s: np.load(d[k] / "we_snapshots.npy")[list(np.load(d[k] / "we_snapshot_steps.npy")).index(s)]   # noqa: E731
    ref = snap("lrs2", 1)
    near, plain = np.linalg.norm(snap("at10_ge2", 2) - ref), np.linalg.norm(snap("at10", 2) - ref)
    assert near < 0.1 * plain, ("reused gradient does not act like one 2x step", near, plain)
    assert not np.array_equal(snap("at10_ge2", 10), snap("at10", 10)), "--pre-switch-grad-every had no effect"
    res = json.loads((d["at10_ge2"] / "result.json").read_text(encoding="utf-8"))
    ev = res["events"]["pre_switch_grad_every"]
    assert ev["k"] == 2 and ev["eval_steps_pre_switch"] == [1, 3, 5, 7, 9] and ev["evals_total"] == 5 + 4, ev
    assert res["pre_switch_grad_every"] == 2, res.get("pre_switch_grad_every")
    for bad in (sw + ["--steps", "14", "--switch-step", "10", "--pre-switch-grad-every", "3"],      # t not a multiple of k
                sw + ["--steps", "14", "--switch-step", "10", "--pre-switch-grad-every", "0"],
                sw + ["--steps", "14", "--switch-step", "10", "--pre-switch-grad-every", "2", "--lr-scale", "2"],
                ["--steps", "14", "--pre-switch-grad-every", "2"]):                                    # no switch
        r = run(*bad)
        assert r.returncode != 0, bad


def test_minibatch_order(tmp: Path) -> None:
    """L0 (session 43): --batch-size / --order / --optimizer sgdm. Defaults leave the fingerprint unchanged; stride sorts the
    train pairs by (a mod 10, a) and repeats that order every epoch; iid reshuffles every epoch and is reproducible for a seed;
    fixed repeats one permutation; the switch rebuilds the order for the new set; sgdm step 1 is linear (not a sign step);
    invalid combinations are refused."""
    import numpy as np
    f1 = fb.run_fingerprint(ns())[0]
    for k, v in (("batch_size", 0), ("order", "iid"), ("optimizer", "adamw"), ("sgd_lr", None), ("sgd_momentum", 0.9)):
        assert fb.run_fingerprint(ns(**{k: v}))[0] == f1, f"default --{k} changed the fingerprint"
    assert fb.run_fingerprint(ns(batch_size=256))[0] != f1 and fb.run_fingerprint(ns(batch_size=256, order="stride"))[0] != fb.run_fingerprint(ns(batch_size=256))[0]
    out = tmp / "mb"
    spl = ROOT / "lab/experiments/EXP-056-overlap-persistence/splits"
    base = [sys.executable, str(FB), "--seed", "400", "--condition", "baseline", "--threads", "1", "--out-root", str(out),
            "--split-file", str(spl / "seed400_w0_A.npy"), "--test-file", str(spl / "seed400_test.npy")]
    run = lambda *x: subprocess.run(base + list(x), cwd=ROOT, capture_output=True, text=True, timeout=600)   # noqa: E731
    n = len(np.load(spl / "seed400_w0_A.npy"))
    spe = -(-n // 1024)
    steps = str(3 * spe + 1)
    for extra in (["--steps", steps, "--batch-size", "1024", "--order", "stride", "--spectra-at", "1"],
                  ["--steps", steps, "--batch-size", "1024", "--spectra-at", "1"],
                  ["--steps", steps, "--batch-size", "1024", "--order", "fixed", "--spectra-at", "1"],
                  ["--steps", "2", "--optimizer", "sgdm", "--sgd-lr", "0.1", "--sgd-momentum", "0.0", "--spectra-at", "1"],
                  ["--steps", "2", "--optimizer", "sgdm", "--sgd-lr", "1e-09", "--sgd-momentum", "0.0", "--spectra-at", "1"],
                  ["--steps", "9", "--batch-size", "1024", "--order", "stride", "--spectra-at", "1",
                   "--switch-split-file", str(spl / "seed400_w0_B.npy"), "--switch-step", "5"],
                  ["--steps", "2", "--spectra-at", "1"]):
        r = run(*extra)
        assert r.returncode == 0, (extra, r.stdout + r.stderr)
    d = {}
    for k in ("w0_A_bs1024_ordstride", "w0_A_bs1024", "w0_A_bs1024_ordfixed", "sgdm0.1_0.0", "sgdm1e-09_0.0", "w0_A", "at5_bs1024_ordstride"):
        hits = [h for h in out.glob(f"*{k}") if h.is_dir()]
        assert len(hits) == 1, (k, list(out.iterdir()))
        d[k] = hits[0]
    ev = lambda k: json.loads((d[k] / "result.json").read_text(encoding="utf-8"))["events"]["minibatch"]   # noqa: E731
    idx = np.load(spl / "seed400_w0_A.npy")
    av, bv = idx // 113, idx % 113
    want = idx[np.lexsort((np.arange(n), av, av % 10))][:12].tolist()
    es, ei, ef = ev("w0_A_bs1024_ordstride"), ev("w0_A_bs1024"), ev("w0_A_bs1024_ordfixed")
    assert es["first_epochs"][0]["head_flat"] == want, (es["first_epochs"][0]["head_flat"], want)
    assert len(es["first_epochs"]) == 4 and len({e["sha"] for e in es["first_epochs"]}) == 1, es
    assert len({e["sha"] for e in ef["first_epochs"]}) == 1 and ef["first_epochs"][0]["sha"] != es["first_epochs"][0]["sha"], ef
    assert len({e["sha"] for e in ei["first_epochs"]}) == 4, ei
    assert ei["steps_per_epoch"] == spe and ei["epochs_started"] == 4, ei
    r = run("--steps", steps, "--batch-size", "1024", "--spectra-at", "1", "--force")
    assert r.returncode == 0 and ev("w0_A_bs1024")["first_epochs"] == ei["first_epochs"], "iid order not reproducible"
    snap = lambda k, s: np.load(d[k] / "we_snapshots.npy")[list(np.load(d[k] / "we_snapshot_steps.npy")).index(s)].astype(np.float64)   # noqa: E731
    lam = 1e-3 * 1.0
    D_sgd, D_def = snap("sgdm0.1_0.0", 1) - (1 - lam) * snap("sgdm0.1_0.0", 0), snap("w0_A", 1) - (1 - lam) * snap("w0_A", 0)
    band = lambda X: float(np.mean(np.abs(np.abs(X) - 1e-3) <= 1e-4))   # noqa: E731
    assert band(D_def) > 0.9 and band(D_sgd) < 0.3, (band(D_def), band(D_sgd))
    D_dec = snap("sgdm1e-09_0.0", 1) - (1 - lam) * snap("sgdm1e-09_0.0", 0)      # tiny lr: only the decoupled decay acts
    assert float(np.abs(D_dec).max()) < 1e-6, ("sgdm weight decay is not (1 - lr_adamw * wd)", float(np.abs(D_dec).max()))
    esw = ev("at5_bs1024_ordstride")["first_epochs"]                           # order rebuilt for the new set after the switch
    idxB = np.load(spl / "seed400_w0_B.npy")
    aB = idxB // 113
    wantB = idxB[np.lexsort((np.arange(len(idxB)), aB, aB % 10))][:12].tolist()
    assert [e["step"] for e in esw][:3] == [1, 5, 6] and esw[2]["head_flat"] == wantB, esw
    res = json.loads((d["sgdm0.1_0.0"] / "result.json").read_text(encoding="utf-8"))
    assert res["optimizer"] == "sgdm" and res["sgd_lr"] == 0.1, res.get("optimizer")
    for bad in (["--steps", "4", "--order", "stride"],                                   # order without minibatch
                ["--steps", "4", "--optimizer", "sgdm"],                                 # sgdm without --sgd-lr
                ["--steps", "4", "--batch-size", "64", "--lr-scale", "2"],
                ["--steps", "4", "--batch-size", "-1"],
                ["--steps", "4", "--sgd-lr", "0.1"],                                    # SGD flag without sgdm
                ["--steps", "4", "--optimizer", "sgdm", "--sgd-lr", "inf"],
                ["--steps", "4", "--optimizer", "sgdm", "--sgd-lr", "0.1", "--beta1", "0.8"]):
        r = run(*bad)
        assert r.returncode != 0, bad


def main() -> int:
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        for name, fn in (("fingerprint_unit", lambda: test_fingerprint_unit()),
                         ("pid_and_atomic_unit", lambda: test_pid_and_atomic_unit(tmp)),
                         ("verify_artifacts", lambda: test_verify_artifacts(tmp)),
                         ("integration", lambda: test_integration(tmp)),
                         ("rewind", lambda: test_rewind(tmp)),
                         ("hp_overrides", lambda: test_hp_overrides(tmp)),
                         ("pre_switch_betas", lambda: test_pre_switch_betas(tmp)),
                         ("pre_switch_grad_every", lambda: test_pre_switch_grad_every(tmp)),
                         ("minibatch_order", lambda: test_minibatch_order(tmp))):
            fn()
            print(f"[test_freq_ban_fingerprint] {name} ok", flush=True)
    print("[test_freq_ban_fingerprint] all ok", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
