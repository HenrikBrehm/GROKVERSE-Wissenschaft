#!/usr/bin/env python3
"""Unit checks for the pure helpers of EXP-001 and for the run-window guard.

Pure numpy; no training. It is still an automated test run, so it too is only
executed through lab/tools/guarded_run.py inside the run window:

    python lab/tools/guarded_run.py -- python lab/experiments/EXP-001-freq-ban/test_freq_ban.py
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "tools"))

import freq_ban as fb  # noqa: E402
import guarded_run as gr  # noqa: E402

P = 113


def test_basis_orthonormal() -> None:
    B = fb.fourier_basis(P)
    assert B.shape == (P, P)
    assert np.allclose(B.T @ B, np.eye(P), atol=1e-10)


def test_power_of_pure_frequency() -> None:
    B = fb.fourier_basis(P)
    a = np.arange(P)
    W = np.stack([np.cos(2 * np.pi * 7 * a / P + 0.3), np.sin(2 * np.pi * 40 * a / P)], axis=1)
    pw = fb.freq_power(W, B)
    assert pw.shape == ((P - 1) // 2,)
    assert fb.top_frequencies(pw, 2) == [7, 40]
    assert pw.sum() > 0.999 * (W ** 2).sum() - 1e-9  # no constant component here


def test_ban_removes_only_banned() -> None:
    B = fb.fourier_basis(P)
    rng = np.random.default_rng(0)
    W = rng.normal(size=(P, 16))
    before = fb.freq_power(W, B)
    Q = fb.ban_projector(B, [3, 17, 56])
    after = fb.freq_power(Q @ W, B)
    for k in (3, 17, 56):
        assert after[k - 1] < 1e-20
    keep = [k for k in range(1, 57) if k not in (3, 17, 56)]
    assert np.allclose(after[[k - 1 for k in keep]], before[[k - 1 for k in keep]])
    assert np.allclose(Q @ Q, Q) and np.allclose(Q, Q.T)
    # the constant component survives
    assert np.allclose(B[:, 0] @ (Q @ W), B[:, 0] @ W)


def test_random_frequencies_avoid_top() -> None:
    pw = np.arange(56, dtype=float)[::-1].copy()  # frequency 1 strongest ... 56 weakest
    top = fb.top_frequencies(pw, 5)
    assert top == [1, 2, 3, 4, 5]
    r = fb.random_frequencies(pw, 5, 123)
    assert len(set(r)) == 5 and min(r) > 10          # ranks >= 2m excluded
    assert r == fb.random_frequencies(pw, 5, 123)     # seeded => reproducible


def test_guard_window() -> None:
    # 2026-09-25 is CEST (UTC+2). 10:00 UTC = 12:00 Berlin -> in window, ~57 min left
    st = gr.window_status(datetime(2026, 9, 25, 10, 0, tzinfo=timezone.utc), None, 20.0)
    assert st["in_window"] and st["max_minutes"] == 20.0
    st = gr.window_status(datetime(2026, 9, 25, 10, 50, tzinfo=timezone.utc), None, 20.0)
    assert st["in_window"] and abs(st["max_minutes"] - 7.0) < 1e-6
    st = gr.window_status(datetime(2026, 9, 25, 11, 0, tzinfo=timezone.utc), None, 20.0)
    assert not st["in_window"] and st["max_minutes"] == 0.0            # 13:00 Berlin
    st = gr.window_status(datetime(2026, 9, 25, 21, 59, tzinfo=timezone.utc), None, 20.0)
    assert not st["in_window"]                                         # 23:59 Berlin
    st = gr.window_status(datetime(2026, 9, 25, 22, 0, tzinfo=timezone.utc), None, 20.0)
    assert st["in_window"]                                             # 00:00 Berlin
    # winter time (CET, UTC+1): 11:30 UTC = 12:30 Berlin -> 27 min to 13:00, minus buffer
    st = gr.window_status(datetime(2026, 12, 1, 11, 30, tzinfo=timezone.utc), None, 30.0)
    assert st["in_window"] and abs(st["max_minutes"] - 27.0) < 1e-6
    # session deadline binds
    now = datetime(2026, 9, 25, 2, 0, tzinfo=timezone.utc)
    st = gr.window_status(now, datetime(2026, 9, 25, 2, 5, tzinfo=timezone.utc), 20.0)
    assert st["binding_limit"] == "session_budget" and abs(st["max_minutes"] - 5.0) < 1e-6


if __name__ == "__main__":
    tests = [v for k, v in dict(globals()).items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"ok  {t.__name__}")
    print(f"{len(tests)} passed")
