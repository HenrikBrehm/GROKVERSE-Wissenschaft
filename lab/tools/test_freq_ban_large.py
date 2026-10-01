"""Equivalence test for lab/tools/freq_ban_large.py (session 70). CPU, p = 113, small; run via guarded_run.py.

Each case trains once with plain freq_ban.py and once through the wrapper (same split/test files, same seed) and checks:
  - final weights (model_final.pt) bit-identical  -> training untouched by lazy data and chunked evaluation,
  - accuracy series equal to 1e-6 (original: float32 mean), loss series to 1e-6 (chunked sums vs one mean),
  - W_E spectra identical, generalisation event identical,
  - wrapper bookkeeping: WRAPPER.json, wrapper.json, argv with the wrapper flags; a plain out-root is refused.
Cases: full batch (chunk 500 < n_train 3831 and n_test 2000), minibatch 64 with stride order.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
TRAINER = ROOT / "lab" / "experiments" / "EXP-001-freq-ban" / "freq_ban.py"
WRAPPER = ROOT / "lab" / "tools" / "freq_ban_large.py"
P = 113


def make_files(tmp: Path) -> tuple[Path, Path]:
    rng = np.random.default_rng(np.random.SeedSequence([70, 113]))
    perm = rng.permutation(P * P)
    tr, te = np.sort(perm[:3831]), np.sort(perm[3831:3831 + 2000])
    np.save(tmp / "split_add113_s70.npy", tr.astype(np.int64))
    np.save(tmp / "test_add113_s70.npy", te.astype(np.int64))
    return tmp / "split_add113_s70.npy", tmp / "test_add113_s70.npy"


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-4000:], sep="\n")
    return r


def only_run_dir(root: Path) -> Path:
    dirs = [d for d in root.iterdir() if d.is_dir()]
    assert len(dirs) == 1, dirs
    return dirs[0]


def compare(case: str, flags: list[str], tmp: Path) -> None:
    plain_root, wrap_root = tmp / f"plain_{case}", tmp / f"wrap_{case}"
    base = [*flags, "--threads", "1", "--save-model", "--condition", "baseline"]
    assert run([sys.executable, str(TRAINER), *base, "--out-root", str(plain_root)]).returncode == 0
    assert run([sys.executable, str(WRAPPER), "--eval-chunk", "500", "--", *base,
                "--out-root", str(wrap_root)]).returncode == 0
    dp, dw = only_run_dir(plain_root), only_run_dir(wrap_root)
    assert dp.name == dw.name, (dp.name, dw.name)
    rp, rw = (json.loads((d / "result.json").read_text()) for d in (dp, dw))
    assert rp["status"] == rw["status"] == "completed"
    sp, sw = (torch.load(d / "model_final.pt") for d in (dp, dw))
    assert sp.keys() == sw.keys() and all(torch.equal(sp[k], sw[k]) for k in sp), f"{case}: weights differ"
    for k in ("train_steps", "test_steps"):
        assert rp["dense"][k] == rw["dense"][k], f"{case}: {k} differs"
    for k in ("train_acc", "test_acc"):   # original: float32 mean of a bool tensor; wrapper: exact count / n
        d = float(np.max(np.abs(np.subtract(rp["dense"][k], rw["dense"][k]))))
        assert d <= 1e-6, f"{case}: {k} differs by {d}"
    for k in ("train_loss", "test_loss"):
        assert np.allclose(rp["dense"][k], rw["dense"][k], rtol=1e-6, atol=1e-7), f"{case}: {k} differs"
    assert np.array_equal(np.load(dp / "spectra.npy"), np.load(dw / "spectra.npy")), f"{case}: spectra differ"
    assert rp["events"].get("generalization_step") == rw["events"].get("generalization_step")
    assert rp["fingerprint"] == rw["fingerprint"]
    assert all(abs(rp["final_acc"][k] - rw["final_acc"][k]) <= 1e-6 for k in ("train", "test"))
    assert "freq_ban_large.py" in rw["argv"][0] and "--eval-chunk" in rw["argv"]
    assert json.loads((dw / "wrapper.json").read_text())["eval_chunk"] == 500
    assert (wrap_root / "WRAPPER.json").exists()
    max_dloss = max(float(np.max(np.abs(np.subtract(rp["dense"][k], rw["dense"][k])))) for k in ("train_loss", "test_loss"))
    print(f"[ok] {case}: {rp['steps_completed']} steps, gen {rp['events'].get('generalization_step')}, "
          f"weights identical, max |d loss| {max_dloss:.2e}", flush=True)


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        split, test = make_files(tmp)
        common = ["--p", "113", "--task", "add", "--split-file", str(split), "--test-file", str(test),
                  "--train-frac", repr(3831 / P ** 2), "--seed", "7001", "--stop-after-gen", "200"]
        compare("fullbatch", [*common, "--steps", "600"], tmp)
        compare("mb_stride", [*common, "--steps", "300", "--batch-size", "64", "--order", "stride"], tmp)
        # refuse a non-empty out-root that the wrapper did not create
        r = run([sys.executable, str(WRAPPER), "--", *common, "--steps", "10", "--threads", "1",
                 "--condition", "baseline", "--out-root", str(tmp / "plain_fullbatch")])
        assert r.returncode != 0 and "WRAPPER.json" in (r.stdout + r.stderr), "plain out-root was not refused"
        # refuse other wrapper settings in the same out-root
        r = run([sys.executable, str(WRAPPER), "--eval-chunk", "999", "--", *common, "--steps", "10", "--threads", "1",
                 "--condition", "baseline", "--out-root", str(tmp / "wrap_fullbatch")])
        assert r.returncode != 0 and "other settings" in (r.stdout + r.stderr), "changed settings were not refused"
        print("[ok] out-root guards", flush=True)
    print("ALL OK")


if __name__ == "__main__":
    main()
