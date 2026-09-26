"""Synthetic checks for EXP-018 analyze.py (Codex review 2026-09-26): short runs, early stop, censoring."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1].parent / "training"))
import analyze as an  # noqa: E402
from grokverse.data import split_hash  # noqa: E402


def fake(tmp: Path, s: int, arm: str, gen: int | None, steps_completed: int, **over) -> None:
    d = Path(str(an.RUN).format(s=s, arm=arm).replace(str(an.HERE / "raw"), str(tmp)))
    d.mkdir(parents=True)
    last = steps_completed
    ts = list(range(0, last + 1, 25))
    acc = [1.0 if gen is not None and t >= gen else 0.1 for t in ts]
    res = {"exp_id": "EXP-018", "condition": "baseline", "seed": s, "max_steps": an.CAP,
           "stop_after_generalization": 25, "config": {"eval_every_test": 25}, "status": "completed",
           "steps_completed": steps_completed, "dense": {"test_steps": ts, "test_acc": acc},
           "split_hash": split_hash(np.load(an.HERE / f"splits/seed{s}_train_{arm}.npy")),
           "test_hash": split_hash(np.load(an.HERE / f"splits/seed{s}_test.npy")), **over}
    (d / "result.json").write_text(json.dumps(res))
    np.save(d / "spectra.npy", np.tile(np.arange(56.0), (last // 250 + 1, 1)))
    np.save(d / "spectra_steps.npy", np.arange(0, last + 1, 250))


def with_tmp(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(an, "RUN", Path(str(an.RUN).replace(str(an.HERE / "raw"), str(tmp_path))))


def test_order_sign_censoring() -> None:
    assert an.order_sign((1000, True), (5000, True)) == 1
    assert an.order_sign((1000, True), (8000, False)) == 1           # D censored after E crossed
    assert an.order_sign((8000, False), (3000, True)) == -1          # E censored, D crossed
    assert an.order_sign((8000, False), (8000, False)) is None       # both censored: undetermined
    assert an.order_sign((2025, False), (3000, True)) is None        # E stopped early, before D's crossing
    assert an.order_sign((1000, True), (1000, True)) is None


def test_sign_test_exact() -> None:
    rows = [{"k": 1}] * 9 + [{"k": -1}] + [{"k": None}]
    t = an.sign_test(rows, "k")
    assert t["n_determined"] == 10 and t["n_first_arm_earlier"] == 9
    assert abs(t["p_one_sided"] - 11 / 1024) < 1e-12


def test_short_run_is_rejected(tmp_path, monkeypatch) -> None:
    with_tmp(tmp_path, monkeypatch)
    fake(tmp_path, 20, "E", 1000, 1025)
    fake(tmp_path, 20, "D", None, 50, max_steps=50)                  # debug run in raw/
    fake(tmp_path, 20, "R", 4000, 4025)
    r = an.row(20)
    assert not r["valid"] and "max_steps" in r["reason"]


def test_uncrossed_run_must_reach_cap(tmp_path, monkeypatch) -> None:
    with_tmp(tmp_path, monkeypatch)
    fake(tmp_path, 20, "E", 1000, 1025)
    fake(tmp_path, 20, "D", None, 3000)                              # aborted early without crossing
    fake(tmp_path, 20, "R", 4000, 4025)
    r = an.row(20)
    assert not r["valid"] and "no primary crossing" in r["reason"]


def test_valid_row_and_strict_threshold_censoring(tmp_path, monkeypatch) -> None:
    with_tmp(tmp_path, monkeypatch)
    fake(tmp_path, 20, "E", 1000, 1025)
    fake(tmp_path, 20, "D", None, an.CAP)
    fake(tmp_path, 20, "R", 4000, 4025)
    r = an.row(20)
    assert r["valid"] and r["gen_D_primary"] == (an.CAP, False)
    assert r["L_DE"] == np.log2(an.CAP / 1000)
    assert r["sign_ED_primary"] == 1 and r["sign_DR_primary"] == -1
