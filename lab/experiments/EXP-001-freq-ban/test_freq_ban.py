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


def test_init_swap_exchanges_power_and_keeps_norm() -> None:   # EXP-010
    B = fb.fourier_basis(P)
    W = np.random.default_rng(1).normal(size=(P, 16))
    before = fb.freq_power(W, B)
    pairs = fb.swap_pairs(before, 5, 99)
    strong = [k for k, _ in pairs]
    weak = [j for _, j in pairs]
    assert sorted(strong) == fb.top_frequencies(before, 5)
    assert not set(strong) & set(weak)
    W2 = fb.swap_frequency_coefficients(W, B, pairs)
    after = fb.freq_power(W2, B)
    for k, j in pairs:
        assert np.isclose(after[k - 1], before[j - 1]) and np.isclose(after[j - 1], before[k - 1])
    untouched = [k - 1 for k in range(1, 57) if k not in strong + weak]
    assert np.allclose(after[untouched], before[untouched])
    assert np.isclose((W2 ** 2).sum(), (W ** 2).sum())
    assert np.allclose(B[:, 0] @ W2, B[:, 0] @ W)                   # constant component kept
    assert fb.top_frequencies(after, 5) == sorted(weak)               # weak set now strongest


def test_init_magswap_moves_power_but_keeps_directions() -> None:   # EXP-011
    B = fb.fourier_basis(P)
    W = np.random.default_rng(2).normal(size=(P, 16))
    before = fb.freq_power(W, B)
    pairs = fb.swap_pairs(before, 5, 7)
    W_full = fb.swap_frequency_coefficients(W, B, pairs)
    W_mag = fb.magswap_frequency_coefficients(W, B, pairs)
    assert np.allclose(fb.freq_power(W_mag, B), fb.freq_power(W_full, B))
    assert np.isclose(np.linalg.norm(W_mag), np.linalg.norm(W))
    c0, cm, cf = B.T @ W, B.T @ W_mag, B.T @ W_full
    moved = set(fb.freq_columns([k for pr in pairs for k in pr]))
    for col in range(P):                       # untouched frequencies (and const) identical
        if col not in moved:
            assert np.allclose(cm[col], c0[col])
    for k, j in pairs:                         # directions stay with their own frequency
        ck = fb.freq_columns([k])
        u0 = c0[ck].ravel() / np.linalg.norm(c0[ck])
        um = cm[ck].ravel() / np.linalg.norm(cm[ck])
        uf = cf[ck].ravel() / np.linalg.norm(cf[ck])
        assert np.isclose(u0 @ um, 1.0)
        assert abs(u0 @ uf) < 0.99             # the full swap does move the direction


def test_split_seed_leaves_init_rng_untouched() -> None:   # EXP-014
    import torch
    from grokverse.config import get_config
    from grokverse.data import make_dataset, split_hash
    torch.manual_seed(10)
    ref = torch.rand(3)
    torch.manual_seed(10)
    d_other = make_dataset(get_config("arch25k", seed=11))
    assert torch.equal(torch.rand(3), ref)          # global RNG not consumed by the split
    d_own = make_dataset(get_config("arch25k", seed=10))
    assert split_hash(d_other["train_idx"]) != split_hash(d_own["train_idx"])


def test_engineered_split_indexing() -> None:   # EXP-016
    from grokverse.config import get_config
    from grokverse.data import make_dataset
    sys.path.append(str(HERE.parent / "EXP-016-engineered-split"))   # append: avoid shadowing analyze
    import make_split as mk
    d = make_dataset(get_config("arch25k", seed=0))
    ax = d["all_x"].numpy()
    for flat in (0, 5, 113 * 7 + 3, 113 * 113 - 1):         # flat index a*p + b <-> (a, b)
        assert ax[flat, 0] == flat // 113 and ax[flat, 1] == flat % 113
    F = mk.target_set(10)
    idx = mk.engineered_train_idx(10, F, 2.0)
    assert len(idx) == len(d["train_idx"]) and len(np.unique(idx)) == len(idx)
    assert np.array_equal(idx, mk.engineered_train_idx(10, F, 2.0))    # deterministic


def test_split_speed_sets() -> None:   # EXP-018
    sys.path.append(str(HERE.parent / "EXP-018-split-speed"))
    import make_splits as m18
    sets = m18.build(20)
    test = sets["test"]
    assert len(test) == round(0.2 * P * P) and len(np.unique(test)) == len(test)
    for arm in m18.ARMS:
        tr = sets[arm]
        assert len(tr) == round(0.3 * P * P) and len(np.unique(tr)) == len(tr)
        assert np.intersect1d(tr, test).size == 0                 # common test set is held out
    assert all(np.array_equal(sets[k], m18.build(20)[k]) for k in sets)   # deterministic
    meta = m18.describe(20, sets)
    assert meta["arms"]["E"]["M0_top5"] == meta["targets"]
    assert meta["arms"]["E"]["top5_power_share"] > 1.4 * meta["arms"]["D"]["top5_power_share"]


def test_data_switch_sets() -> None:   # EXP-020
    import importlib.util
    saved_path = list(sys.path)                  # make_splits prepends other EXP dirs (with their own analyze.py)
    try:
        spec = importlib.util.spec_from_file_location("m20", HERE.parent / "EXP-020-data-switch/make_splits.py")
        m20 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m20)
    finally:
        sys.path[:] = saved_path
    sets = m20.build(30)
    for arm in ("F", "G"):
        assert len(sets[arm]) == round(0.3 * P * P) and len(np.unique(sets[arm])) == len(sets[arm])
        assert np.intersect1d(sets[arm], sets["test"]).size == 0
    assert not np.array_equal(sets["F"], sets["G"])
    assert np.array_equal(sets["F"], m20.build(30)["F"])                 # deterministic


def test_switch_requires_test_file() -> None:   # EXP-020: fail closed on incomplete switch arguments
    import subprocess
    r = subprocess.run([sys.executable, str(HERE / "freq_ban.py"), "--seed", "0", "--condition", "baseline",
                        "--steps", "1", "--split-file", "x.npy", "--switch-split-file", "y.npy",
                        "--switch-step", "5", "--out-root", str(HERE / "raw_test_never")],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode != 0 and "needs --test-file" in (r.stderr + r.stdout)
    assert not (HERE / "raw_test_never").exists()


def test_split_value_variant() -> None:   # EXP-023
    import importlib.util
    import torch
    from grokverse.config import get_config
    from grokverse.models import build_model
    from grokverse.seed import set_seed
    spec = importlib.util.spec_from_file_location("sv", HERE.parent / "EXP-023-split-value/split_value.py")
    sv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sv)
    cfg = get_config("arch25k", seed=10)
    set_seed(10)
    base = build_model(cfg)
    set_seed(10)
    var = sv.convert(build_model(cfg), 10)
    for name, prm in base.named_parameters():                    # (1) baseline init untouched
        assert torch.equal(prm, dict(var.named_parameters())[name])
    assert "W_V1" in dict(var.named_parameters())                 # (3) W_V1 is trained
    x = torch.tensor([[1, 2, 113], [5, 7, 113], [40, 40, 113]])
    with torch.no_grad():
        assert not torch.allclose(var.logits_last(x), base.logits_last(x), atol=1e-6)   # rand changes the function
        set_seed(10)
        cp = sv.convert(build_model(cfg), 10, "copy")                 # (2) copy variant == original model
        assert torch.allclose(cp.logits_last(x), base.logits_last(x), atol=1e-6)
        assert sv.shared_checksum(cp) == sv.shared_checksum(var) == sv.shared_checksum(base)
    state = {k: v.clone() for k, v in var.state_dict().items()}       # (4) save/reload round trip
    re = sv.load_variant(cfg, state, 10, "rand")
    with torch.no_grad():
        assert torch.allclose(re.logits_last(x), var.logits_last(x), atol=1e-7)


def test_previous_status_tolerates_truncated_result(tmp_path) -> None:   # Codex review 2026-09-26
    f = tmp_path / "result.json"
    assert fb.previous_status(f) is None
    f.write_text('{"status": "completed", "dense": {"test_st')          # killed mid-write
    assert fb.previous_status(f) is None
    f.write_text('{"status": "completed"}')
    assert fb.previous_status(f) == "completed"


def test_shrink_matches_top_ban_energy() -> None:              # amendment 2026-09-25b
    B = fb.fourier_basis(P)
    W = np.random.default_rng(2).normal(size=(P, 16))
    pw = fb.freq_power(W, B)
    f = fb.shrink_factor(pw, 5)
    W2 = fb.shrink_nonconstant(W, B, f)
    removed_shrink = pw.sum() - fb.freq_power(W2, B).sum()
    removed_ban = pw.sum() - fb.freq_power(fb.ban_projector(B, fb.top_frequencies(pw, 5)) @ W, B).sum()
    assert np.isclose(removed_shrink, removed_ban)
    assert np.allclose(B[:, 0] @ W2, B[:, 0] @ W)


def test_censoring_intervals() -> None:                         # amendment 2026-09-25b
    import analyze as an
    cap = 15000
    assert an.classify((9000, 9000), (5000, 5000)) == "support"
    assert an.classify((cap, None), (5000, 5000)) == "support"        # lower bound 10000
    assert an.classify((cap, None), (14800, 14800)) == "unclear"      # lower bound only 200
    assert an.classify((cap, None), (cap, None)) == "unclear"         # both censored
    assert an.classify((6000, 6000), (5800, 5800)) == "against"
    assert an.classify((5000, 5000), (cap, None)) == "against"        # upper bound < 0
    assert an.classify((6000, 6000), (5200, 5200)) == "unclear"


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
    import inspect
    import tempfile
    for t in tests:
        if "tmp_path" in inspect.signature(t).parameters:   # pytest-style test, run without pytest
            with tempfile.TemporaryDirectory() as d:
                t(Path(d))
        else:
            t()
        print(f"ok  {t.__name__}")
    print(f"{len(tests)} passed")
