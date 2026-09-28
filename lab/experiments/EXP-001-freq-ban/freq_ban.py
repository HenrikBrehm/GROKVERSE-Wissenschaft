#!/usr/bin/env python3
"""EXP-001 — training-time frequency ban ("Frequenzverbot").

Question: are the Fourier frequencies that emerge in the transformer's embedding
DURING the memorization plateau causally needed for the grokking transition, or
does the network route around a ban with little delay?

From step ``t0`` on, after every optimizer step, the token rows ``W_E[:p]`` are
projected onto the orthogonal complement of the real-DFT subspace of a banned
frequency set K (each frequency k spans cos(2πka/p) and sin(2πka/p) over a).
The '=' row is left alone. Everything else mirrors ``grokverse.train``
(same preset ``arch25k``, same seed order, full-batch AdamW), so up to ``t0``
the trajectory is the baseline's.

Conditions
  baseline       no ban
  ban_emerging   K = the m frequencies with the largest W_E power at t0
  ban_random     K = m frequencies drawn (seeded) from power ranks > 2m at t0
  ban_destined   K = top-m W_E frequencies of the STORED 25k baseline model of
                 the same seed, banned from step 1 (t0 is ignored)
  shrink_matched (amendment, secondary control) at t0, ONCE, scale the non-constant
                 Fourier part of W_E[:p] so that the removed power equals the power a
                 top-m ban would remove at t0. No persistent constraint.
  init_swap      (EXP-010) no ban. At init, the DFT coefficients of W_E[:p] of the m
                 strongest frequencies T are swapped with those of m weak frequencies S
                 (drawn like ban_random, seed + SWAP_SALT). Norm and distribution of the
                 iid-normal init are preserved; data split and all other weights are
                 identical to the baseline of the same seed. t0 is ignored.
  init_magswap   (EXP-011) like init_swap, but only the block NORMS of each pair (t, s) are
                 exchanged; each frequency keeps its own coefficient direction. The power
                 spectrum after the swap equals init_swap's; only the directions differ.

Run ONLY through lab/tools/guarded_run.py (run window). Example, from the root:
    python lab/tools/guarded_run.py -- python lab/experiments/EXP-001-freq-ban/freq_ban.py \
        --seed 0 --condition ban_emerging
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "training"))

from grokverse.config import THRESHOLD_SETS, get_config  # noqa: E402
from grokverse.data import make_dataset, split_hash  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.seed import set_seed  # noqa: E402
from grokverse.train import all_transitions, evaluate  # noqa: E402
from grokverse.utils import git_commit, lib_versions  # noqa: E402

CONDITIONS = ("baseline", "ban_emerging", "ban_random", "ban_destined", "init_swap",
              "shrink_matched", "init_magswap")
INIT_CONDITIONS = ("init_swap", "init_magswap")   # init-only interventions, no ban
EXP_ID = "EXP-001"
EXP_ID_BY_CONDITION = {"init_swap": "EXP-010", "init_magswap": "EXP-011"}
SWAP_SALT = 20_011            # init_swap draws S with seed + salt
RANDOM_SALT = 10_007          # ban_random draws with seed + salt, never the run seed itself
LR_SCALE_UNTIL = 250          # EXP-039: last step with the scaled lr (on the first train set)
LR_AFTER_SWITCH_STEPS = 500   # P3 ELR arm (session 18): steps after the switch trained with lr * c
SPECTRUM_EVERY = 250          # steps between stored W_E power spectra
PARTIAL_WRITE_EVERY = 500     # steps between partial result.json writes
RESET_PARTS = {"attn": ("W_Q", "W_K", "W_V", "W_O"), "mlp": ("W_in", "W_out"), "unembed": ("W_U",),   # EXP-067
               "qk": ("W_Q", "W_K"), "vo": ("W_V", "W_O")}                                          # EXP-069
REWIND_PARTS = tuple(RESET_PARTS) + ("we", "rest", "all")   # EXP-073: "rest" = every parameter except W_E, "all" = every parameter

STORED_RUN = "txf_add_p113_wd1.0_frac0.3_seed{seed}_arch25k"
# Astra review point 3 (session 13): run fingerprint over every argument that changes the run or its artifacts, plus the
# content hashes of the data files. Run ids stay unchanged (old results remain valid); the fingerprint decides skipping.
FINGERPRINT_VERSION = 1
FINGERPRINT_ARGS = ("seed", "condition", "t0", "m", "steps", "stop_after_gen", "threads", "split_seed", "switch_step",
                    "split_value", "warmup", "alternate_every", "reset_at_switch", "lr_scale", "we_init_scale",
                    "spectra_at", "p", "task", "arch", "device", "save_model")
FINGERPRINT_FILES = ("split_file", "test_file", "switch_split_file")
LATE_ARGS = {"lr_scale_after_switch": 1.0, "reset_optim_at_switch": False, "reset_optim_part": None, "log_update_norms": 0,
             "rewind_at_switch": None, "rewind_from": None,
             "lr": None, "weight_decay": None, "train_frac": None,
             "plant_targets": None, "plant_c": None, "plant_noise": False, "beta1": None, "beta2": None,
             "pre_switch_betas": None, "pre_switch_grad_every": 1,
             "batch_size": 0, "order": "iid", "optimizer": "adamw", "sgd_lr": None, "sgd_momentum": 0.9}   # name -> default; in the fingerprint only if != default (s18, s21, s24, s39, s40, s42, s43)
ORDER_SALT = 100_043                  # L0 (session 43): own random stream for the minibatch order, independent of init and splits
HP_OVERRIDES = ("lr", "weight_decay", "train_frac", "beta1", "beta2")   # session 24 (rule 19a), s39 betas (EXP-081): None = preset
LOCK_NAME = "run.lock"


# --------------------------------------------------------------------------- #
# Fourier helpers (pure; tested in test_freq_ban.py)
# --------------------------------------------------------------------------- #
def fourier_basis(p: int) -> np.ndarray:
    """Orthonormal real DFT basis over Z_p as a [p, p] matrix, columns
    [const, cos_1, sin_1, ..., cos_K, sin_K] with K = (p-1)//2 (p odd)."""
    if p % 2 == 0:
        raise ValueError("fourier_basis assumes odd p (no Nyquist column)")
    a = np.arange(p)
    cols = [np.ones(p) / np.sqrt(p)]
    for k in range(1, (p - 1) // 2 + 1):
        cols.append(np.cos(2 * np.pi * k * a / p) * np.sqrt(2 / p))
        cols.append(np.sin(2 * np.pi * k * a / p) * np.sqrt(2 / p))
    return np.stack(cols, axis=1)


def freq_columns(freqs) -> list[int]:
    """Column indices of frequencies ``freqs`` (1-based) in ``fourier_basis``."""
    return [c for k in freqs for c in (2 * k - 1, 2 * k)]


def freq_power(W: np.ndarray, basis: np.ndarray) -> np.ndarray:
    """Power of W [p, d] per frequency k = 1..(p-1)//2 (index k-1)."""
    coef = basis.T @ W                               # [p, d]
    sq = (coef ** 2).sum(axis=1)
    return sq[1::2] + sq[2::2]


def top_frequencies(power: np.ndarray, m: int) -> list[int]:
    """1-based frequencies of the m largest entries; ties broken by lower k."""
    order = np.lexsort((np.arange(len(power)), -power))
    return sorted(int(i) + 1 for i in order[:m])


def random_frequencies(power: np.ndarray, m: int, rng_seed: int) -> list[int]:
    """m frequencies drawn from power ranks strictly below 2m (i.e. far from the top)."""
    order = np.lexsort((np.arange(len(power)), -power))
    pool = np.sort(order[2 * m:]) + 1
    rng = np.random.default_rng(rng_seed)
    return sorted(int(k) for k in rng.choice(pool, size=m, replace=False))


def swap_pairs(power: np.ndarray, m: int, rng_seed: int) -> list[tuple[int, int]]:
    """Pairs (t, s): the m strongest frequencies (by descending power) with m weak ones
    drawn from power ranks >= 2m (ascending k), both 1-based."""
    order = np.lexsort((np.arange(len(power)), -power))
    strong = [int(i) + 1 for i in order[:m]]
    weak = random_frequencies(power, m, rng_seed)
    return list(zip(strong, weak))


def swap_frequency_coefficients(W: np.ndarray, basis: np.ndarray,
                                pairs: list[tuple[int, int]]) -> np.ndarray:
    """New W [p, d] with the (cos, sin) DFT coefficient rows of each pair (k, j) exchanged.
    Orthonormal basis: Frobenius norm and all other frequencies are unchanged."""
    coef = basis.T @ W
    new = coef.copy()
    for k, j in pairs:
        ck, cj = freq_columns([k]), freq_columns([j])
        new[ck], new[cj] = coef[cj], coef[ck]
    return basis @ new


def magswap_frequency_coefficients(W: np.ndarray, basis: np.ndarray,
                                   pairs: list[tuple[int, int]]) -> np.ndarray:
    """New W [p, d] where, for each pair (k, j), the (cos, sin) coefficient block of k is
    rescaled to the norm of j's block and vice versa. Directions stay with their frequency;
    power per frequency equals that of ``swap_frequency_coefficients``; Frobenius norm kept."""
    coef = basis.T @ W
    new = coef.copy()
    for k, j in pairs:
        ck, cj = freq_columns([k]), freq_columns([j])
        nk, nj = np.linalg.norm(coef[ck]), np.linalg.norm(coef[cj])
        new[ck], new[cj] = coef[ck] * (nj / nk), coef[cj] * (nk / nj)
    return basis @ new


def shrink_factor(power: np.ndarray, m: int) -> float:
    """Amplitude factor that removes the same power as banning the top-m frequencies."""
    top = np.sort(power)[::-1][:m].sum()
    return float(np.sqrt(1.0 - top / power.sum()))


def shrink_nonconstant(W: np.ndarray, basis: np.ndarray, factor: float) -> np.ndarray:
    """W with all non-constant DFT coefficients scaled by ``factor`` (constant row kept)."""
    coef = basis.T @ W
    coef[1:] *= factor
    return basis @ coef


def ban_projector(basis: np.ndarray, freqs) -> np.ndarray:
    """[p, p] projector onto the orthogonal complement of the banned frequencies."""
    B = basis[:, freq_columns(freqs)]
    return np.eye(basis.shape[0]) - B @ B.T


# --------------------------------------------------------------------------- #
# the run
# --------------------------------------------------------------------------- #
def _stored_final_W_E(seed: int, p: int) -> np.ndarray:
    path = ROOT / "training" / "runs" / STORED_RUN.format(seed=seed) / "model_final.pt"
    if not path.exists():
        raise FileNotFoundError(f"ban_destined needs the stored baseline model: {path}")
    state = torch.load(path, map_location="cpu", weights_only=True)
    return state["W_E"].numpy().astype(np.float64)[:p]


def _choose_ban(cond: str, W_E: np.ndarray, basis: np.ndarray, m: int, seed: int) -> list[int]:
    power = freq_power(W_E, basis)
    if cond == "ban_emerging":
        return top_frequencies(power, m)
    if cond == "ban_random":
        return random_frequencies(power, m, seed + RANDOM_SALT)
    raise ValueError(cond)


def lr_mult_after_switch(step: int, switch_step: int, c: float) -> float:
    """P3 ELR arm (session 18): c for the first LR_AFTER_SWITCH_STEPS steps on the second split, else 1. The switch takes
    effect after opt.step() at switch_step, so the second split is trained from switch_step + 1 on."""
    return c if switch_step < step <= switch_step + LR_AFTER_SWITCH_STEPS else 1.0


def previous_status(path: Path) -> str | None:
    """Status of an earlier run; a result.json truncated by a kill counts as unfinished (Codex review 2026-09-26)."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text()).get("status")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def file_sha256(path: str | None) -> str | None:
    return None if path is None else hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_fingerprint(a: argparse.Namespace) -> tuple[str, dict]:
    """sha256 of the canonical JSON of all effective arguments and data-file contents (not out_root/force)."""
    fields = {k: getattr(a, k) for k in FINGERPRINT_ARGS}
    fields["spectra_at"] = sorted({int(x) for x in a.spectra_at.split(",") if x.strip()})
    fields.update({f"{k}_sha256": file_sha256(getattr(a, k)) for k in FINGERPRINT_FILES})
    # session 18: arguments added after the fingerprint enter it ONLY when they differ from their default, so the
    # fingerprints of all existing runs stay unchanged (otherwise every resume would fail with 'another configuration')
    for k, default in LATE_ARGS.items():
        if getattr(a, k, default) != default:
            fields[k] = getattr(a, k)
    fields["fingerprint_version"] = FINGERPRINT_VERSION
    blob = json.dumps(fields, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode()).hexdigest(), fields


def legacy_mismatch(prev: dict, a: argparse.Namespace, out_dir: Path) -> str | None:
    """A completed run from before the fingerprint: reject a skip if any recorded setting differs from the request."""
    checks = (("max_steps", a.steps), ("stop_after_generalization", a.stop_after_gen), ("switch_step", a.switch_step),
              ("warmup", a.warmup), ("alternate_every", a.alternate_every), ("reset_at_switch", a.reset_at_switch),
              ("split_value", a.split_value), ("device", a.device))
    for key, want in checks:
        if key in prev and prev[key] != want:
            return f"{key} {prev[key]!r} != requested {want!r}"
    for key, path in (("split_hash", a.split_file), ("test_hash", a.test_file), ("switch_hash", a.switch_split_file)):
        if path is not None and key in prev and prev[key] != split_hash(np.load(path)):
            return f"{key} differs from the content of {path}"
    if a.save_model and not (out_dir / "model_final.pt").exists():
        return "--save-model requested but no model_final.pt"
    return None


def _pid_alive_since(pid: int, not_after_unix: float) -> bool:
    """True if process pid runs and was created no later than not_after_unix (guards against PID reuse).
    Windows via OpenProcess/GetProcessTimes (os.kill(pid, 0) would TERMINATE the process on Windows)."""
    if os.name != "nt":
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.OpenProcess.restype = wintypes.HANDLE
    k32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    k32.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
    k32.GetProcessTimes.argtypes = (wintypes.HANDLE,) + (ctypes.POINTER(wintypes.FILETIME),) * 4
    k32.CloseHandle.argtypes = (wintypes.HANDLE,)
    h = k32.OpenProcess(0x1000, False, pid)            # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return ctypes.get_last_error() == 5            # access denied: the process exists (review s13), else gone
    try:
        code = wintypes.DWORD()
        if not k32.GetExitCodeProcess(h, ctypes.byref(code)) or code.value != 259:   # STILL_ACTIVE
            return False
        ft = [wintypes.FILETIME() for _ in range(4)]
        if not k32.GetProcessTimes(h, *[ctypes.byref(x) for x in ft]):
            return True
        created = ((ft[0].dwHighDateTime << 32) | ft[0].dwLowDateTime) / 1e7 - 11644473600.0   # FILETIME -> unix
        return created <= not_after_unix + 5.0
    finally:
        k32.CloseHandle(h)


def acquire_lock(out_dir: Path, run_id: str) -> Path:
    """Exclusive lock per run id; a lock of a dead (or reused) PID is taken over."""
    out_dir.mkdir(parents=True, exist_ok=True)
    lock = out_dir / LOCK_NAME
    for _ in range(2):
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            try:
                info = json.loads(lock.read_text())
                holder_alive = _pid_alive_since(int(info["pid"]), float(info["created_unix"]))
            except (OSError, ValueError, KeyError, TypeError):
                # review s13: a lock file still being written by its creator is empty for a moment -> young = alive
                try:
                    young = time.time() - lock.stat().st_mtime < 30
                except OSError:
                    young = False
                info, holder_alive = {"pid": "?"}, young
            if holder_alive:
                raise SystemExit(f"[exp] {run_id} is locked by running pid {info['pid']} ({lock})")
            lock.unlink(missing_ok=True)                   # stale lock of a dead run
            continue
        with os.fdopen(fd, "w") as f:
            json.dump({"pid": os.getpid(), "created_unix": time.time(),
                       "start_utc": datetime.now(timezone.utc).isoformat()}, f)
        import atexit
        atexit.register(lambda: lock.unlink(missing_ok=True))
        return lock
    raise SystemExit(f"[exp] could not acquire {lock}")


def save_npy_atomic(path: Path, arr) -> None:
    tmp = path.with_name(path.name + ".tmp")           # no with_suffix: stems may contain dots (eps2.0)
    with open(tmp, "wb") as f:
        np.save(f, arr)
    os.replace(tmp, path)


def verify_artifacts(out_dir: Path, step: int, extra_spec: set[int], save_model: bool) -> None:
    """Fail closed before 'completed': arrays load, match each other, end at the final step and are finite."""
    sp, st = np.load(out_dir / "spectra.npy"), np.load(out_dir / "spectra_steps.npy")
    if len(sp) != len(st) or len(st) == 0 or int(st[-1]) != step or not np.isfinite(sp).all():
        raise SystemExit(f"[exp] artifact check failed in {out_dir}: spectra/steps inconsistent or non-finite")
    if extra_spec:
        ws, wst = np.load(out_dir / "we_snapshots.npy"), np.load(out_dir / "we_snapshot_steps.npy")
        want = {0} | {x for x in extra_spec if x <= step}
        if len(ws) != len(wst) or not want <= set(wst.tolist()) or not np.isfinite(ws).all():
            raise SystemExit(f"[exp] artifact check failed in {out_dir}: W_E snapshots incomplete or non-finite")
    if save_model and not (out_dir / "model_final.pt").exists():
        raise SystemExit(f"[exp] artifact check failed in {out_dir}: model_final.pt missing")


def hp_overrides(a: argparse.Namespace) -> dict:
    """Rule 19a: optional overrides of the preset's lr / weight_decay / train_frac; {} (preset values) when not given."""
    out = {k: getattr(a, k, None) for k in HP_OVERRIDES if getattr(a, k, None) is not None}
    for k, v in out.items():
        if (not np.isfinite(v) or v < 0 or (k != "weight_decay" and v == 0) or (k == "train_frac" and not 0 < v < 1)
                or (k in ("beta1", "beta2") and not 0 < v < 1)):
            raise SystemExit(f"--{k.replace('_', '-')} out of range: {v!r}")
    return out


def run(a: argparse.Namespace) -> dict:
    if ((a.p, a.task, a.arch) != (113, "add", "transformer")
            and (a.split_file is None or a.split_seed is not None or a.condition != "baseline" or a.split_value)):
        raise SystemExit("--p/--task/--arch other than 113/add/transformer only with --split-file and --condition baseline")
    hp = hp_overrides(a)
    cfg = get_config("arch25k", seed=a.seed, steps=a.steps, threads=a.threads, p=a.p, task=a.task, arch=a.arch, **hp)
    p = cfg.p
    if not 0 < int(round(cfg.train_frac * p * p)) < p * p:   # Codex s24: a fraction may not round to an empty train or test set
        raise SystemExit(f"--train-frac {cfg.train_frac} gives an empty train or test set for p = {p}")
    exp_id = EXP_ID_BY_CONDITION.get(a.condition, EXP_ID)
    if a.split_seed is not None:     # EXP-014: data split from another seed, init from --seed
        exp_id = "EXP-014"
    run_id = f"{exp_id}_{a.condition}_t{a.t0}_m{a.m}_seed{a.seed}_thr{a.threads}"
    if a.split_seed is not None:
        run_id += f"_split{a.split_seed}"
    if a.split_file is not None:     # EXP-016: engineered train split from a .npy of flat indices a*p+b
        if a.split_seed is not None:
            raise SystemExit("--split-file and --split-seed are exclusive")
        exp_id = "EXP-016" if a.test_file is None else "EXP-018"
        run_id = f"{exp_id}_{a.condition}_seed{a.seed}_thr{a.threads}_{Path(a.split_file).stem}"
        if a.switch_split_file is not None:      # EXP-020: change the train set once at --switch-step
            if a.test_file is None or a.switch_step is None or a.switch_step < 1:
                raise SystemExit("--switch-split-file needs --test-file and --switch-step >= 1")
            exp_id = "EXP-020"
            run_id = (f"{exp_id}_{a.condition}_seed{a.seed}_thr{a.threads}_{Path(a.split_file).stem}"
                      f"_to_{Path(a.switch_split_file).stem}_at{a.switch_step}")
        if (a.p, a.task) != (113, "add"):          # EXP-043: other modulus / multiplication (split stem names the task)
            exp_id = "EXP-044" if a.switch_split_file is not None else "EXP-043"   # EXP-044: data switch
            run_id = run_id.replace(run_id.split("_")[0], exp_id, 1) + f"_{a.task}{a.p}"
        if a.arch != "transformer":                # EXP-045: shared-embedding MLP (model.W_E exists, same analysis)
            exp_id = "EXP-045"
            run_id = run_id.replace(run_id.split("_")[0], exp_id, 1) + f"_{a.arch}"
    elif a.test_file is not None or a.switch_split_file is not None:
        raise SystemExit("--test-file / --switch-split-file need --split-file")
    if a.warmup:                     # EXP-035: linear learning-rate warmup (default 0 = unchanged behaviour)
        run_id += f"_wu{a.warmup}"
    for nm in ("lr_scale", "we_init_scale"):   # Codex s10: reject NaN/inf (they would pass the <= 0 checks)
        if not np.isfinite(getattr(a, nm)):
            raise SystemExit(f"--{nm.replace('_', '-')} must be finite")
    if a.lr_scale != 1.0:            # EXP-039: lr * c on the first train set for steps <= LR_SCALE_UNTIL (1.0 = off)
        if a.lr_scale <= 0 or a.warmup or a.alternate_every:
            raise SystemExit("--lr-scale needs c > 0, no --warmup and no --alternate-every")
        run_id += f"_lrs{a.lr_scale:g}"
    if a.we_init_scale != 1.0:       # EXP-040: W_E multiplied by s right after the (unchanged) init (1.0 = off)
        if a.we_init_scale <= 0:
            raise SystemExit("--we-init-scale needs s > 0")
        run_id += f"_wes{a.we_init_scale:g}"
    plant_tg = None
    if a.plant_targets is not None or a.plant_c is not None or a.plant_noise:   # EXP-087 (session 39): additive W_E plant after init
        try:
            plant_tg = sorted(int(x) for x in str(a.plant_targets).split(","))
        except ValueError:
            raise SystemExit("--plant-targets needs comma-separated integers")
        if (a.plant_c is None or not np.isfinite(a.plant_c) or a.plant_c <= 0 or len(set(plant_tg)) != len(plant_tg)
                or min(plant_tg) < 1 or max(plant_tg) > (a.p - 1) // 2 or a.arch != "transformer" or a.split_value
                or a.we_init_scale != 1.0 or a.condition != "baseline"):
            raise SystemExit("--plant-targets/--plant-c need distinct k in 1..(p-1)/2, a finite c > 0, --condition baseline, "
                             "the transformer, no --split-value and no --we-init-scale")
        run_id += f"_{'pn' if a.plant_noise else 'pl'}{a.plant_c:g}"
    if a.lr_scale_after_switch != 1.0:   # P3 ELR arm (session 18, Lyle et al. 2025): lr * c for the first
        # LR_AFTER_SWITCH_STEPS steps after --switch-step, full lr otherwise (1.0 = off)
        if (not np.isfinite(a.lr_scale_after_switch) or a.lr_scale_after_switch <= 0 or a.switch_split_file is None
                or a.warmup or a.lr_scale != 1.0 or a.alternate_every):
            raise SystemExit("--lr-scale-after-switch needs a finite c > 0, --switch-split-file, "
                             "no --warmup, no --lr-scale and no --alternate-every")
        run_id += f"_lras{a.lr_scale_after_switch:g}"
    if a.alternate_every:            # EXP-037: F/G blocks of this many steps before --switch-step (0 = off)
        if a.switch_split_file is None or a.alternate_every < 1 or a.alternate_every >= a.switch_step:
            raise SystemExit("--alternate-every needs --switch-split-file and 1 <= A < --switch-step")
        run_id += f"_alt{a.alternate_every}"
    if a.reset_at_switch:            # EXP-038: reset W_E ("we") or all other parameters ("rest") at --switch-step
        if a.switch_split_file is None:
            raise SystemExit("--reset-at-switch needs --switch-split-file")
        run_id += f"_rs{a.reset_at_switch}"
    if a.reset_optim_at_switch:      # EXP-057 (session 21): clear the AdamW state of ALL parameters at --switch-step, weights kept
        if a.switch_split_file is None:
            raise SystemExit("--reset-optim-at-switch needs --switch-split-file")
        run_id += "_ro"
    if a.reset_optim_part:           # EXP-058 (session 21): zero only exp_avg ("m") or exp_avg and exp_avg_sq ("moments"); step kept
        if a.switch_split_file is None or a.reset_optim_at_switch or a.reset_at_switch:
            raise SystemExit("--reset-optim-part needs --switch-split-file and excludes the other reset options")
        run_id += f"_ro{a.reset_optim_part}"
    psb = None
    if a.pre_switch_betas is not None:   # EXP-090 (session 40): AdamW betas for steps 1..switch_step, preset betas afterwards
        try:
            psb = tuple(float(x) for x in str(a.pre_switch_betas).split(","))
        except ValueError:
            raise SystemExit("--pre-switch-betas needs 'b1,b2'")
        if (len(psb) != 2 or not all(np.isfinite(x) and 0 < x < 1 for x in psb) or a.switch_split_file is None
                or a.reset_optim_at_switch or a.reset_optim_part or a.reset_at_switch or a.rewind_at_switch
                or a.alternate_every or a.beta1 is not None or a.beta2 is not None):
            raise SystemExit("--pre-switch-betas needs 'b1,b2' in (0, 1), --switch-split-file, and excludes the reset, rewind, "
                             "alternation and --beta1/--beta2 options")
        run_id += f"_psb{psb[0]!r}_{psb[1]!r}"
    gek = int(getattr(a, "pre_switch_grad_every", 1))
    if gek != 1:                     # EXP-095 (session 42): before the switch a fresh gradient only every k steps, reused in between
        if (gek < 1 or a.switch_split_file is None or a.switch_step is None or a.switch_step % gek or a.condition != "baseline"
                or a.warmup or a.alternate_every or a.lr_scale != 1.0 or a.lr_scale_after_switch != 1.0 or psb is not None
                or a.reset_at_switch or a.reset_optim_at_switch or a.reset_optim_part or a.rewind_at_switch):
            raise SystemExit("--pre-switch-grad-every k needs k >= 1, --switch-split-file with --switch-step a multiple of k, "
                             "--condition baseline, and excludes the warmup, alternation, lr-scale, pre-switch-betas, reset and rewind options")
        run_id += f"_ge{gek}"
    mbs = int(getattr(a, "batch_size", 0) or 0)
    order = getattr(a, "order", "iid")
    optim_name = getattr(a, "optimizer", "adamw")
    if optim_name != "sgdm" and (getattr(a, "sgd_lr", None) is not None or float(getattr(a, "sgd_momentum", 0.9)) != 0.9):
        raise SystemExit("--sgd-lr / --sgd-momentum only with --optimizer sgdm")   # review s43: else fingerprint != run id
    if mbs or order != "iid" or optim_name != "adamw":   # L0 (session 43): minibatch, data order, SGD with momentum
        sgd_lr, sgd_mom = getattr(a, "sgd_lr", None), float(getattr(a, "sgd_momentum", 0.9))
        if (mbs < 0 or (order != "iid" and not mbs) or a.condition != "baseline" or a.warmup or a.alternate_every
                or a.lr_scale != 1.0 or a.lr_scale_after_switch != 1.0 or psb is not None or gek != 1
                or a.reset_at_switch or a.reset_optim_at_switch or a.reset_optim_part or a.rewind_at_switch
                or a.log_update_norms or a.plant_targets is not None or a.split_value
                or (optim_name == "sgdm" and not (sgd_lr is not None and np.isfinite(sgd_lr) and sgd_lr > 0 and 0 <= sgd_mom < 1))
                or (optim_name == "sgdm" and (a.beta1 is not None or a.beta2 is not None))):
            raise SystemExit("--batch-size/--order/--optimizer need --condition baseline, --order fixed/stride needs --batch-size > 0, "
                             "--optimizer sgdm needs --sgd-lr > 0 and 0 <= --sgd-momentum < 1; excludes warmup, alternation, lr-scale, "
                             "pre-switch options, resets, rewind, update norms, plant and split-value")
        run_id += (f"_bs{mbs}" if mbs else "") + (f"_ord{order}" if order != "iid" else "") + (
            f"_sgdm{float(sgd_lr)!r}_{sgd_mom!r}" if optim_name == "sgdm" else "")
    if (a.rewind_at_switch is None) != (a.rewind_from is None):
        raise SystemExit("--rewind-at-switch and --rewind-from go together")
    if a.rewind_at_switch:           # EXP-073 (session 24): one part back to its own state (weights + AdamW state) at step R
        if (a.switch_split_file is None or not 0 <= a.rewind_from < a.switch_step or a.condition != "baseline"   # Codex s24: ban/shrink state is not rewound
                or a.reset_at_switch or a.reset_optim_at_switch
                or a.reset_optim_part or a.alternate_every or a.warmup or a.lr_scale != 1.0 or a.lr_scale_after_switch != 1.0):
            raise SystemExit("--rewind-at-switch needs --switch-split-file, 0 <= --rewind-from < --switch-step, --condition baseline "
                             "and excludes the reset, alternation, warmup and lr-scale options")
        run_id += f"_rw{a.rewind_at_switch}{a.rewind_from}"
    for k, tag in (("lr", "lr"), ("weight_decay", "wd"), ("train_frac", "tf"), ("beta1", "b1"), ("beta2", "b2")):   # rule 19a: distinct run ids for overrides
        if k in hp:
            run_id += f"_{tag}{float(hp[k])!r}"          # Codex s24: repr is injective for floats, :g is not
    if a.log_update_norms and (a.switch_split_file is None or a.log_update_norms < 1):
        raise SystemExit("--log-update-norms needs --switch-split-file and N >= 1")
    if a.split_value:                # EXP-023: position 1 gets its own attention value matrix
        exp_id = "EXP-023"
        run_id = run_id.replace(run_id.split("_")[0], exp_id, 1) + f"_sv{a.split_value}"
    if a.device != "cpu":            # rule 16: GPU runs get their own run_id, never mixed with CPU runs of an experiment
        if not a.device.startswith("cuda") or not torch.cuda.is_available():
            raise SystemExit(f"[exp] device {a.device!r} not available (torch.cuda.is_available() is False)")
        run_id += "_dev" + a.device.replace(":", "")
    extra_spec = {int(x) for x in a.spectra_at.split(",") if x.strip()}   # logging only: run_id unchanged
    if any(x < 1 for x in extra_spec):
        raise SystemExit("--spectra-at needs steps >= 1")
    out_dir = Path(a.out_root) / run_id
    fingerprint, fp_fields = run_fingerprint(a)
    if not a.force and previous_status(out_dir / "result.json") == "completed":
        prev = json.loads((out_dir / "result.json").read_text())
        if "fingerprint" in prev:     # Astra 3: skip only the identical run; anything else is an error, not a skip
            if prev["fingerprint"] != fingerprint:
                raise SystemExit(f"[exp] {run_id} completed with another configuration (fingerprint differs); "
                                 "use another --out-root or --force")
        elif (why := legacy_mismatch(prev, a, out_dir)) is not None:
            raise SystemExit(f"[exp] {run_id} completed (pre-fingerprint) with another configuration: {why}; "
                             "use another --out-root or --force")
        if (float(prev.get("lr_scale", 1.0)) != a.lr_scale              # Codex s10: same intervention as requested
                or float(prev.get("we_init_scale", 1.0)) != a.we_init_scale):
            raise SystemExit(f"[exp] {run_id} completed with other scale metadata; rerun with --force")
        if extra_spec:                # Codex 2026-09-26: a skipped run must already hold the requested spectra
            done = prev.get("steps_completed", 0)
            have = set(np.load(out_dir / "spectra_steps.npy").tolist())
            want = {x for x in extra_spec if x <= done}
            snap = out_dir / "we_snapshot_steps.npy"   # Codex s10: and the W_E snapshots (step 0 + requested)
            if not want <= have or not snap.exists() or not ({0} | want) <= set(np.load(snap).tolist()):
                raise SystemExit(f"[exp] {run_id} completed without the --spectra-at steps/snapshots; rerun with --force")
        print(f"[exp] {run_id} already completed; use --force to overwrite", flush=True)
        raise SystemExit(0)           # skip is not an error (EXP-020 queue stops on every other failure)
    acquire_lock(out_dir, run_id)     # Astra 3: no two processes on one run id (creates out_dir)
    for stale in ("we_snapshots.npy", "we_snapshot_steps.npy"):   # Codex s10: no stale snapshots from an earlier run
        (out_dir / stale).unlink(missing_ok=True)
    if a.force:                      # Codex s12: a forced rerun that dies before its first write must not leave the old record
        for stale in ("result.json", "spectra.npy", "spectra_steps.npy"):
            (out_dir / stale).unlink(missing_ok=True)

    # identical order to grokverse.train.train(): threads, seed, data, model, optimizer
    torch.set_num_threads(cfg.threads)
    set_seed(cfg.seed)
    # make_dataset uses its own torch.Generator (seeded with cfg.seed), not the global RNG,
    # so a foreign split leaves the model init unchanged
    data = make_dataset(cfg if a.split_seed is None
                        else get_config("arch25k", seed=a.split_seed, steps=a.steps, threads=a.threads,
                                        **{k: v for k, v in hp.items() if k == "train_frac"}))
    if a.split_file is not None:
        raw = np.load(a.split_file)       # fail closed (Codex review 2026-09-26)
        n_expected = int(round(cfg.train_frac * p * p))
        if (raw.ndim != 1 or not np.issubdtype(raw.dtype, np.integer) or len(raw) != n_expected
                or len(np.unique(raw)) != len(raw) or raw.min() < 0 or raw.max() >= p * p):
            raise SystemExit(f"[exp] invalid split file {a.split_file}: need {n_expected} unique ints in [0, p*p)")
        tr = torch.from_numpy(raw.astype(np.int64))
        te = torch.from_numpy(np.setdiff1d(np.arange(p * p), tr.numpy()))
        if a.test_file is not None:       # EXP-018: common held-out test set instead of the complement
            rt = np.load(a.test_file)
            if (rt.ndim != 1 or not np.issubdtype(rt.dtype, np.integer) or len(rt) == 0
                    or len(np.unique(rt)) != len(rt) or rt.min() < 0 or rt.max() >= p * p
                    or np.intersect1d(rt, raw).size):
                raise SystemExit(f"[exp] invalid test file {a.test_file}: need unique ints in [0, p*p) disjoint from train")
            te = torch.from_numpy(np.sort(rt).astype(np.int64))
        data = {**data, "train_x": data["all_x"][tr], "train_y": data["all_y"][tr],
                "test_x": data["all_x"][te], "test_y": data["all_y"][te], "train_idx": tr, "test_idx": te}
    trx, try_, tex, tey = data["train_x"], data["train_y"], data["test_x"], data["test_y"]
    switch_idx = None
    if a.switch_split_file is not None:
        rs = np.load(a.switch_split_file)
        if (rs.ndim != 1 or not np.issubdtype(rs.dtype, np.integer) or len(rs) != len(data["train_idx"])
                or len(np.unique(rs)) != len(rs) or rs.min() < 0 or rs.max() >= p * p
                or np.intersect1d(rs, data["test_idx"].numpy()).size):
            raise SystemExit(f"[exp] invalid switch file {a.switch_split_file}: same size, unique, disjoint from test")
        switch_idx = torch.from_numpy(rs.astype(np.int64))
    model = build_model(cfg)
    init_checksum = hashlib.sha256()          # EXP-023: all parameters of the plain init, name-sorted
    for name, prm in sorted(model.named_parameters()):
        init_checksum.update(name.encode())
        init_checksum.update(np.ascontiguousarray(prm.detach().cpu().numpy()).tobytes())
    if a.split_value:                # after the baseline init (identical weights), before the optimizer
        if cfg.arch != "transformer":
            raise SystemExit("--split-value needs the transformer")
        sys.path.insert(0, str(HERE.parent / "EXP-023-split-value"))
        from split_value import convert
        model = convert(model, a.seed, a.split_value)
    if a.we_init_scale != 1.0:       # EXP-040 (Nachtrag a): only the non-DC part of the number rows W_E[:p] is scaled;
        with torch.no_grad():          # the '=' row and the per-dimension mean over numbers stay unchanged
            num = model.W_E[:p]
            mean = num.mean(dim=0, keepdim=True)
            model.W_E[:p] = mean + a.we_init_scale * (num - mean)
    plant_norm = None
    if plant_tg is not None:         # EXP-087: plant (or norm-matched noise) on W_E[:p]; numpy only, no torch RNG consumed
        sys.path.insert(0, str(HERE.parent / "EXP-087-planted-signal-mediation"))
        from plant import noise_delta, plant_delta
        W0 = model.W_E.detach().cpu().numpy().astype(np.float64)[:p]
        delta = plant_delta(W0, plant_tg, a.plant_c, a.seed)
        if a.plant_noise:
            delta = noise_delta(W0, float(np.linalg.norm(delta)), a.seed)
        plant_norm = float(np.linalg.norm(delta))
        with torch.no_grad():
            model.W_E[:p] += torch.tensor(delta, dtype=model.W_E.dtype)
    dev = torch.device(a.device)       # rule 16: init is built on the CPU (identical weights), then moved
    model = model.to(dev)
    trx, try_, tex, tey = (t.to(dev) for t in (trx, try_, tex, tey))
    keep_init = bool(a.warmup or a.reset_at_switch or a.lr_scale != 1.0 or a.we_init_scale != 1.0)
    init_params = [q.detach().clone() for q in model.parameters()] if keep_init else []   # EXP-035/038
    we_idx = next((i for i, q in enumerate(model.parameters()) if q is model.W_E), None) if keep_init else None
    if optim_name == "sgdm":         # L0: SGD with momentum; weight decay applied by hand, decoupled, with AdamW's per-step shrink
        opt = torch.optim.SGD(model.parameters(), lr=float(a.sgd_lr), momentum=float(a.sgd_momentum), weight_decay=0.0)
    else:
        opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay,
                                betas=psb if psb is not None else (cfg.beta1, cfg.beta2))
    basis = fourier_basis(p)

    events: dict = {}
    if a.condition in INIT_CONDITIONS:   # numpy only: consumes no torch RNG, so data/weights match baseline
        W0 = model.W_E.detach().cpu().numpy().astype(np.float64)[:p]
        pw0 = freq_power(W0, basis)
        pairs = swap_pairs(pw0, a.m, a.seed + SWAP_SALT)
        swap_fn = (swap_frequency_coefficients if a.condition == "init_swap"
                   else magswap_frequency_coefficients)
        with torch.no_grad():
            model.W_E[:p] = torch.tensor(swap_fn(W0, basis, pairs), dtype=model.W_E.dtype, device=dev)
        events[a.condition] = {"pairs": pairs, "power_before": pw0.tolist(),
                               "power_after": freq_power(
                                   model.W_E.detach().cpu().numpy().astype(np.float64)[:p], basis).tolist()}

    ban_from = 1 if a.condition == "ban_destined" else a.t0
    banned: list[int] | None = None
    proj: torch.Tensor | None = None
    if a.condition == "ban_destined":
        banned = top_frequencies(freq_power(_stored_final_W_E(a.seed, p), basis), a.m)
        proj = torch.tensor(ban_projector(basis, banned), dtype=model.W_E.dtype, device=dev)

    dense = {"train_steps": [], "train_acc": [], "train_loss": [], "test_steps": [],
             "test_acc": [], "test_loss": [], "eval_every_train": cfg.eval_every_train,
             "eval_every_test": cfg.eval_every_test}
    spectra, spectra_steps = [], []
    res = {"exp_id": exp_id, "run_id": run_id, "status": "running",
           "condition": a.condition, "seed": a.seed, "t0": a.t0, "m": a.m,
           "ban_from_step": None if a.condition in ("baseline",) + INIT_CONDITIONS else ban_from,
           "amendment": "2026-09-25b: projected grad + exp_avg; shrink_matched control",
           "stop_after_generalization": a.stop_after_gen, "split_seed": a.split_seed, "split_file": a.split_file, "test_file": a.test_file, "switch_split_file": a.switch_split_file,
           "switch_step": a.switch_step, "split_value": a.split_value, "warmup": a.warmup, "lr_scale": a.lr_scale, "we_init_scale": a.we_init_scale, "plant_targets": plant_tg, "plant_c": a.plant_c, "plant_noise": a.plant_noise, "plant_delta_norm": plant_norm, "pre_switch_betas": list(psb) if psb else None, "pre_switch_grad_every": gek, "batch_size": mbs, "order": order, "optimizer": optim_name,
           "sgd_lr": getattr(a, "sgd_lr", None), "sgd_momentum": getattr(a, "sgd_momentum", 0.9), "lr_scale_until": LR_SCALE_UNTIL, "lr_scale_after_switch": a.lr_scale_after_switch, "lr_after_switch_steps": LR_AFTER_SWITCH_STEPS, "alternate_every": a.alternate_every, "reset_at_switch": a.reset_at_switch, "rewind_at_switch": a.rewind_at_switch, "rewind_from": a.rewind_from, "spectra_at": sorted(extra_spec),
           "device": a.device, "device_name": (torch.cuda.get_device_name(dev) if dev.type == "cuda" else platform.processor()),
           "init_checksum_shared": init_checksum.hexdigest(), "max_steps": a.steps,
           "config": {**cfg.to_dict(), "device": a.device},   # Astra 10: Config keeps 'cpu'; record the real device
           "fingerprint": fingerprint, "fingerprint_fields": fp_fields,
           "split_hash": split_hash(data["train_idx"]),
           "test_hash": split_hash(data["test_idx"]),
           "switch_hash": None if switch_idx is None else split_hash(switch_idx),
           "git_commit": git_commit(), "versions": lib_versions(),
           "platform": platform.platform(), "argv": sys.argv,
           "start_utc": datetime.now(timezone.utc).isoformat()}

    def dense_eval(step: int) -> None:
        if step % cfg.eval_every_train == 0:
            loss, acc = evaluate(model, trx, try_, p)
            dense["train_steps"].append(step); dense["train_acc"].append(acc); dense["train_loss"].append(loss)
        if step % cfg.eval_every_test == 0:
            loss, acc = evaluate(model, tex, tey, p)
            dense["test_steps"].append(step); dense["test_acc"].append(acc); dense["test_loss"].append(loss)

    we_snaps, we_snap_steps = [], []   # EXP-040 Nachtrag a: W_E[:p] at step 0 and the --spectra-at steps (float32)

    def spectrum(step: int) -> None:
        spectra_steps.append(step)
        spectra.append(freq_power(model.W_E.detach().cpu().numpy().astype(np.float64)[:p], basis))
        if extra_spec and (step == 0 or step in extra_spec):
            we_snap_steps.append(step)
            we_snaps.append(model.W_E.detach().cpu().numpy()[:p].astype(np.float32).copy())

    def write(status: str, arrays: bool = True) -> None:
        res.update({"status": status, "steps_completed": step, "banned_freqs": banned,
                    "events": events, "dense": dense,
                    "transitions": all_transitions(dense) if dense["test_steps"] else None,
                    "elapsed_s": round(time.perf_counter() - t_start, 1),
                    "sec_per_step": round((time.perf_counter() - t_start) / max(step, 1), 5)})
        if dev.type == "cuda":        # rule 16c: memory per process, to size parallel GPU runs
            res["cuda_max_mem_mb"] = round(torch.cuda.max_memory_allocated(dev) / 2**20, 1)
        if arrays:                    # Astra 3: atomic like result.json (a kill cannot leave a truncated array)
            save_npy_atomic(out_dir / "spectra.npy", np.asarray(spectra))
            save_npy_atomic(out_dir / "spectra_steps.npy", np.asarray(spectra_steps))
            if we_snaps:
                save_npy_atomic(out_dir / "we_snapshots.npy", np.asarray(we_snaps))
                save_npy_atomic(out_dir / "we_snapshot_steps.npy", np.asarray(we_snap_steps))
        tmp = out_dir / "result.json.tmp"             # atomic: a kill during the write cannot truncate result.json
        tmp.write_text(json.dumps(res, indent=1))
        os.replace(tmp, out_dir / "result.json")

    rw_names: list[str] = []            # EXP-073: parameters to rewind and their snapshot (weights + AdamW state) at step R
    rw_snap: dict = {}
    if a.rewind_at_switch:
        all_names = [nm for nm, _ in model.named_parameters()]
        rw_names = (all_names if a.rewind_at_switch == "all" else [nm for nm in all_names if nm != "W_E"]
                    if a.rewind_at_switch == "rest" else ["W_E"] if a.rewind_at_switch == "we"
                    else [nm for nm in all_names if nm in RESET_PARTS[a.rewind_at_switch]])
        if a.rewind_at_switch in RESET_PARTS and len(rw_names) != len(RESET_PARTS[a.rewind_at_switch]):
            raise SystemExit(f"[exp] EXP-073 rewind part {a.rewind_at_switch}: parameters not found")

    def rewind_snapshot() -> dict:
        prm = dict(model.named_parameters())
        return {nm: (prm[nm].detach().clone(),
                     {k: (v.detach().clone() if torch.is_tensor(v) else v) for k, v in opt.state[prm[nm]].items()}
                     if prm[nm] in opt.state else None) for nm in rw_names}

    step, t_start = 0, time.perf_counter()
    if a.rewind_at_switch and a.rewind_from == 0:
        rw_snap = rewind_snapshot()
    dense_eval(0); spectrum(0)
    gen_thr = THRESHOLD_SETS["primary"][1]
    stop_at = a.steps
    ge_saved, ge_evals, ge_steps = None, 0, []
    mb_rng = np.random.default_rng(np.random.SeedSequence([ORDER_SALT, a.seed]))
    mb_ref, mb_order, mb_pos, mb_epoch, mb_log = None, None, 0, 0, []

    def mb_new_order(x: torch.Tensor, fresh_set: bool):
        """L0: index order of one epoch over the current train set x (rows (a, b, '='))."""
        n = len(x)
        if order == "stride":        # LeDoux 2026: sorted by (a mod floor(sqrt p), a); ties keep the train-set order
            av = x[:, 0].detach().cpu().numpy()
            idx = np.lexsort((np.arange(n), av, av % int(np.floor(np.sqrt(p)))))
        elif order == "fixed" and not fresh_set and mb_order is not None:
            return mb_order
        else:
            idx = mb_rng.permutation(n)
        return torch.from_numpy(idx.astype(np.int64)).to(x.device)
    for step in range(1, a.steps + 1):
        model.train()
        if gek > 1 and step <= a.switch_step and (step - 1) % gek:    # EXP-095: Adam step on the stored (stale) gradient
            for q, g0 in zip(model.parameters(), ge_saved):
                q.grad = None if g0 is None else g0.clone()
        else:
            if mbs:                      # L0: next minibatch of the current epoch order
                if mb_ref is not trx:
                    mb_order, mb_pos, mb_ref = mb_new_order(trx, True), 0, trx
                elif mb_pos >= len(trx):
                    mb_order, mb_pos = mb_new_order(trx, False), 0
                if mb_pos == 0:
                    mb_epoch += 1
                    if len(mb_log) < 4:  # first epochs: head and hash of the order (tests, audit)
                        o = mb_order.cpu().numpy()
                        flat = (trx[mb_order[:12], 0] * p + trx[mb_order[:12], 1]).cpu().numpy().tolist()
                        mb_log.append({"step": step, "head_flat": flat, "sha": hashlib.sha256(o.tobytes()).hexdigest()[:16]})
                bi = mb_order[mb_pos:mb_pos + mbs]
                mb_pos += mbs
                loss = F.cross_entropy(model.logits_last(trx[bi])[:, :p], try_[bi])
            else:
                loss = F.cross_entropy(model.logits_last(trx)[:, :p], try_)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            ge_evals += 1
            if gek > 1 and step <= a.switch_step:
                ge_saved = [None if q.grad is None else q.grad.detach().clone() for q in model.parameters()]
                ge_steps.append(step)
        if proj is not None and step > ban_from:   # amendment 2026-09-25: projected gradient
            with torch.no_grad():
                model.W_E.grad[:p] = proj @ model.W_E.grad[:p]
        if a.warmup:    # EXP-035: lr_t = lr * min(1, t / warmup) on the first train set only; full lr after a switch
            on_first = switch_idx is None or step <= a.switch_step
            for g in opt.param_groups:
                g["lr"] = cfg.lr * (min(1.0, step / a.warmup) if on_first else 1.0)
        if a.lr_scale != 1.0:   # EXP-039: c * lr while on the first train set and step <= LR_SCALE_UNTIL, else full lr
            on_first = switch_idx is None or step <= a.switch_step
            for g in opt.param_groups:
                g["lr"] = cfg.lr * (a.lr_scale if on_first and step <= LR_SCALE_UNTIL else 1.0)
        if a.lr_scale_after_switch != 1.0:   # P3 ELR arm: c * lr for switch_step < step <= switch_step + 500
            for g in opt.param_groups:
                g["lr"] = cfg.lr * lr_mult_after_switch(step, a.switch_step, a.lr_scale_after_switch)
        log_un = bool(a.log_update_norms and a.switch_step - 4 <= step <= a.switch_step + a.log_update_norms)
        if log_un:                       # EXP-058: size of the actual parameter update around the switch
            before = [q.detach().clone() for q in model.parameters()]
        if optim_name == "sgdm":
            with torch.no_grad():        # L0: decoupled decay with AdamW's per-step shrink lr * wd, before the SGD step
                for q in model.parameters():
                    q.mul_(1 - cfg.lr * cfg.weight_decay)
        opt.step()
        if mbs:
            events["minibatch"] = {"batch_size": mbs, "order": order, "epochs_started": mb_epoch,
                                   "steps_per_epoch": -(-len(trx) // mbs), "first_epochs": mb_log}
        if log_un:
            with torch.no_grad():
                d2 = [float(((q - q0) ** 2).sum()) for q, q0 in zip(model.parameters(), before)]
            wi = next(i for i, q in enumerate(model.parameters()) if q is model.W_E)   # we_idx is only set with keep_init
            events.setdefault("update_norms", []).append([step, sum(d2) ** 0.5, d2[wi] ** 0.5])
        if (a.warmup or a.lr_scale != 1.0 or a.we_init_scale != 1.0) and switch_idx is not None and step == a.switch_step:   # EXP-035 Nachtrag a: displacement at the switch
            with torch.no_grad():
                d_all = sum(float(((q - q0) ** 2).sum()) for q, q0 in zip(model.parameters(), init_params)) ** 0.5
                d_we = float((model.W_E - init_params[we_idx]).norm())
            events["displacement_at_switch"] = {"all": d_all, "W_E": d_we}
        if a.condition not in ("baseline",) + INIT_CONDITIONS and step == ban_from:
            W_now = model.W_E.detach().cpu().numpy().astype(np.float64)[:p]
            if banned is None and a.condition != "shrink_matched":
                banned = _choose_ban(a.condition, W_now, basis, a.m, a.seed)
                proj = torch.tensor(ban_projector(basis, banned), dtype=model.W_E.dtype, device=dev)
            events["pre_ban_acc"] = {"train": evaluate(model, trx, try_, p)[1],
                                     "test": evaluate(model, tex, tey, p)[1]}
            events["power_at_ban"] = freq_power(W_now, basis).tolist()
            if a.condition == "shrink_matched":     # one-time, energy matched to a top-m ban
                factor = shrink_factor(np.asarray(events["power_at_ban"]), a.m)
                with torch.no_grad():
                    model.W_E[:p] = torch.tensor(shrink_nonconstant(W_now, basis, factor),
                                                 dtype=model.W_E.dtype, device=dev)
                events["shrink_factor"] = factor
                events["post_ban_acc"] = {"train": evaluate(model, trx, try_, p)[1],
                                          "test": evaluate(model, tex, tey, p)[1]}
        if proj is not None and step >= ban_from:
            with torch.no_grad():
                model.W_E[:p] = proj @ model.W_E[:p]
                if step == ban_from:                # first-moment state into the allowed subspace
                    m1 = opt.state[model.W_E]["exp_avg"]
                    m1[:p] = proj @ m1[:p]
            if step == ban_from:
                events["post_ban_acc"] = {"train": evaluate(model, trx, try_, p)[1],
                                          "test": evaluate(model, tex, tey, p)[1]}
        if a.rewind_at_switch and step == a.rewind_from:          # EXP-073: state after the update of step R
            rw_snap = rewind_snapshot()
        if switch_idx is not None and step == a.switch_step:     # EXP-020: new train set from the next step on
            ge_saved = None
            old = data["train_idx"].numpy()
            sub = {"G_minus_F": np.setdiff1d(switch_idx.numpy(), old), "F_minus_G": np.setdiff1d(old, switch_idx.numpy()),
                   "F_and_G": np.intersect1d(old, switch_idx.numpy())}    # Codex review: new pairs separately
            events["switch"] = {"step": step, "train_acc_before": evaluate(model, trx, try_, p)[1],
                                "new_train_hash": split_hash(switch_idx),
                                **{f"acc_{k}": evaluate(model, data["all_x"][torch.from_numpy(v)].to(dev),
                                                        data["all_y"][torch.from_numpy(v)].to(dev), p)[1]
                                   for k, v in sub.items() if len(v)},
                                **{f"n_{k}": int(len(v)) for k, v in sub.items()}}
            trx, try_ = data["all_x"][switch_idx].to(dev), data["all_y"][switch_idx].to(dev)
            if psb is not None:      # EXP-090: preset betas from the next step on; moments rescaled so m_hat, v_hat stay continuous
                post = (cfg.beta1, cfg.beta2)
                params = list(model.parameters())
                snap = [q.detach().clone() for q in params]
                hat_before, factors = [], None
                with torch.no_grad():
                    for q in params:
                        st = opt.state[q]
                        s = float(st["step"])
                        f1, f2 = (1 - post[0] ** s) / (1 - psb[0] ** s), (1 - post[1] ** s) / (1 - psb[1] ** s)
                        hat_before.append((st["exp_avg"] / (1 - psb[0] ** s), st["exp_avg_sq"] / (1 - psb[1] ** s)))
                        st["exp_avg"].mul_(f1)
                        st["exp_avg_sq"].mul_(f2)
                        factors = factors or (f1, f2, s)
                    for g in opt.param_groups:
                        g["betas"] = post
                check = (all(torch.equal(q, s0) for q, s0 in zip(params, snap))
                         and all(g["betas"] == post for g in opt.param_groups)
                         and all(torch.allclose(opt.state[q]["exp_avg"] / (1 - post[0] ** float(opt.state[q]["step"])), mb, rtol=1e-5, atol=1e-12)
                                 and torch.allclose(opt.state[q]["exp_avg_sq"] / (1 - post[1] ** float(opt.state[q]["step"])), vb, rtol=1e-5, atol=1e-20)
                                 for q, (mb, vb) in zip(params, hat_before)))
                events["pre_switch_betas"] = {"pre": list(psb), "post": list(post), "step": factors[2] if factors else None,
                                              "factor_m": factors[0] if factors else None, "factor_v": factors[1] if factors else None,
                                              "check": check}
                if not check:
                    raise SystemExit("[exp] EXP-090 beta switch check failed")
            if a.reset_at_switch:    # EXP-038: selected parameters back to their init, their AdamW state cleared
                params = list(model.parameters())
                if a.reset_at_switch in RESET_PARTS:      # EXP-067: one named part of the rest
                    names = [nm for nm, _ in model.named_parameters()]
                    sel = [nm in RESET_PARTS[a.reset_at_switch] for nm in names]
                    if sum(sel) != len(RESET_PARTS[a.reset_at_switch]):
                        raise SystemExit(f"[exp] EXP-067 reset part {a.reset_at_switch}: parameters not found")
                else:
                    sel = [(i == we_idx) == (a.reset_at_switch == "we") for i in range(len(params))]
                snap = [q.detach().clone() for q in params]
                disp = {"W_E": float((params[we_idx] - init_params[we_idx]).norm()),
                        "rest": sum(float(((q - q0) ** 2).sum()) for i, (q, q0) in enumerate(zip(params, init_params))
                                    if i != we_idx) ** 0.5}
                with torch.no_grad():
                    for i, q in enumerate(params):
                        if sel[i]:
                            q.copy_(init_params[i])
                            opt.state.pop(q, None)
                check = all((torch.equal(q, init_params[i]) and q not in opt.state) if sel[i]
                            else (torch.equal(q, snap[i]) and q in opt.state) for i, q in enumerate(params))
                events["reset_at_switch"] = {"which": a.reset_at_switch,
                                             "n_params": sum(q.numel() for i, q in enumerate(params) if sel[i]),
                                             "displacement_before": disp, "check": check,
                                             "train_acc_after": evaluate(model, trx, try_, p)[1]}
                if not check:
                    raise SystemExit("[exp] EXP-038 reset check failed")
            if a.rewind_at_switch:        # EXP-073: selected parameters and their AdamW state back to step R, the rest untouched
                prm = dict(model.named_parameters())
                before = {nm: q.detach().clone() for nm, q in prm.items()}
                old_x, old_y = data["all_x"][data["train_idx"]].to(dev), data["all_y"][data["train_idx"]].to(dev)
                diag = lambda: {"new": list(evaluate(model, trx, try_, p)), "old": list(evaluate(model, old_x, old_y, p))}   # noqa: E731
                diag_before = diag()          # Codex s24: loss/acc [loss, acc] on the new and old split before and after the rewind
                with torch.no_grad():
                    for nm, (w, st) in rw_snap.items():
                        prm[nm].copy_(w)
                        if st is None:
                            opt.state.pop(prm[nm], None)
                        else:
                            opt.state[prm[nm]] = {k: (v.clone() if torch.is_tensor(v) else v) for k, v in st.items()}
                same = lambda s1, s2: s1.keys() == s2.keys() and all(torch.equal(s1[k], s2[k]) if torch.is_tensor(s1[k])   # noqa: E731
                                                                   else s1[k] == s2[k] for k in s1)
                check = (set(rw_snap) == set(rw_names) and len(rw_names) > 0
                         and all(torch.equal(prm[nm], rw_snap[nm][0]) and ((prm[nm] not in opt.state) if rw_snap[nm][1] is None
                                                                       else same(opt.state[prm[nm]], rw_snap[nm][1]))
                                 for nm in rw_names)
                         and all(torch.equal(q, before[nm]) and q in opt.state for nm, q in prm.items() if nm not in rw_names))
                events["rewind_at_switch"] = {"which": a.rewind_at_switch, "from_step": a.rewind_from, "names": rw_names,
                                              "n_params": sum(prm[nm].numel() for nm in rw_names), "check": check,
                                              "change_norm": {nm: float((before[nm] - prm[nm]).norm()) for nm in rw_names},
                                              "train_acc_after": evaluate(model, trx, try_, p)[1],
                                              "diag_before": diag_before, "diag_after": diag()}
                if not check:
                    raise SystemExit("[exp] EXP-073 rewind check failed")
            if a.reset_optim_at_switch:   # EXP-057: fresh AdamW state (moments and step counters) for every parameter
                params = list(model.parameters())
                snap = [q.detach().clone() for q in params]
                for q in params:
                    opt.state.pop(q, None)
                check = all(q not in opt.state and torch.equal(q, s0) for q, s0 in zip(params, snap))
                events["reset_optim_at_switch"] = {"n_params": sum(q.numel() for q in params), "check": check}
                if not check:
                    raise SystemExit("[exp] EXP-057 optimizer reset check failed")
            if a.reset_optim_part:        # EXP-058: partial reset, per-parameter step counters (bias correction) kept
                params = list(model.parameters())
                snap = [q.detach().clone() for q in params]
                steps_before = [float(opt.state[q]["step"]) for q in params]
                for q in params:
                    opt.state[q]["exp_avg"].zero_()
                    if a.reset_optim_part == "moments":
                        opt.state[q]["exp_avg_sq"].zero_()
                check = all(torch.equal(q, s0) and not opt.state[q]["exp_avg"].any()
                            and (a.reset_optim_part == "m" or not opt.state[q]["exp_avg_sq"].any())
                            and float(opt.state[q]["step"]) == st0
                            for q, s0, st0 in zip(params, snap, steps_before))
                events["reset_optim_part"] = {"part": a.reset_optim_part, "step_kept": steps_before[0], "check": check}
                if not check:
                    raise SystemExit("[exp] EXP-058 partial optimizer reset check failed")
            # session 18, P3 model (iii): ELR = lr / ||theta|| at the switch (read-only, additive field); after a reset,
            # so it describes the parameters the post-switch updates act on (Codex s18)
            events["switch"]["param_norm"] = float(sum(float((q.detach() ** 2).sum()) for q in model.parameters()) ** 0.5)
        elif a.alternate_every and step < a.switch_step and step % a.alternate_every == 0:
            # EXP-037: block k = steps (k-1)A+1 .. kA trains on F for odd k, on G for even k
            nxt = switch_idx if (step // a.alternate_every) % 2 == 1 else data["train_idx"]
            trx, try_ = data["all_x"][nxt].to(dev), data["all_y"][nxt].to(dev)
            events["alternations"] = events.get("alternations", 0) + 1
            events.setdefault("alternation_trace", []).append([step, split_hash(nxt)])   # Codex: behavioural check
        dense_eval(step)
        if step % SPECTRUM_EVERY == 0 or step in extra_spec:
            spectrum(step)
        if ("generalization_step" not in events and step % cfg.eval_every_test == 0
                and dense["test_acc"][-1] >= gen_thr):
            events["generalization_step"] = step
            stop_at = min(a.steps, step + a.stop_after_gen)
        if step % PARTIAL_WRITE_EVERY == 0:
            write("running")
        if step >= stop_at:
            break
    if gek > 1:
        events["pre_switch_grad_every"] = {"k": gek, "eval_steps_pre_switch": ge_steps, "evals_total": ge_evals}
    if step % SPECTRUM_EVERY and step not in extra_spec:
        spectrum(step)
    final_power = freq_power(model.W_E.detach().cpu().numpy().astype(np.float64)[:p], basis)
    res["final_top_m_freqs"] = top_frequencies(final_power, a.m)
    res["final_acc"] = {"train": evaluate(model, trx, try_, p)[1],
                        "test": evaluate(model, tex, tey, p)[1]}
    res["end_utc"] = datetime.now(timezone.utc).isoformat()
    if a.save_model:
        tmp_model = out_dir / "model_final.pt.tmp"
        torch.save(model.state_dict(), tmp_model)
        os.replace(tmp_model, out_dir / "model_final.pt")
    write("finalizing")               # Astra 3: all arrays on disk, then check them, then mark completed
    verify_artifacts(out_dir, step, extra_spec, a.save_model)
    write("completed", arrays=False)
    print(f"[exp] {run_id} completed: steps {step}, gen {events.get('generalization_step')}, "
          f"banned {banned}, final top-{a.m} {res['final_top_m_freqs']}, "
          f"{res['sec_per_step']} s/step", flush=True)
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description="EXP-001 training-time frequency ban")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--condition", choices=CONDITIONS, required=True)
    ap.add_argument("--t0", type=int, default=2000, help="first banned step (not ban_destined)")
    ap.add_argument("--m", type=int, default=5, help="number of banned frequencies")
    ap.add_argument("--steps", type=int, default=15000, help="hard step cap")
    ap.add_argument("--stop-after-gen", type=int, default=2000,
                    help="continue this many steps after the generalization crossing, then stop")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--out-root", default=str(HERE / "raw"))
    ap.add_argument("--split-seed", type=int, default=None,
                    help="EXP-014: take the train/test split of this seed (init stays from --seed)")
    ap.add_argument("--split-file", default=None,
                    help="EXP-016: .npy with flat train indices a*p+b (test = complement)")
    ap.add_argument("--test-file", default=None,
                    help="EXP-018: .npy with flat test indices (disjoint from --split-file) instead of the complement")
    ap.add_argument("--switch-split-file", default=None,
                    help="EXP-020: .npy train set that replaces --split-file after --switch-step (needs --test-file)")
    ap.add_argument("--switch-step", type=int, default=None, help="EXP-020: last step trained on --split-file")
    ap.add_argument("--split-value", choices=("rand", "copy"), default=None,
                    help="EXP-023: position 1 gets its own attention value matrix W_V1 (rand: separate generator, "
                         "copy: copy of W_V, untied afterwards)")
    ap.add_argument("--warmup", type=int, default=0, help="EXP-035: linear lr warmup over this many steps (0 = off)")
    ap.add_argument("--alternate-every", type=int, default=0,
                    help="EXP-037: alternate F/G in blocks of this many steps until --switch-step (0 = off)")
    ap.add_argument("--reset-optim-part", choices=("m", "moments"), default=None,
                    help="EXP-058: at --switch-step zero AdamW exp_avg ('m') or exp_avg and exp_avg_sq ('moments'); step counters kept")
    ap.add_argument("--log-update-norms", type=int, default=0,
                    help="EXP-058: log the parameter update norm (all, W_E) for steps switch-4 .. switch+N")
    ap.add_argument("--reset-optim-at-switch", action="store_true",
                    help="EXP-057: at --switch-step clear the AdamW state of all parameters (weights unchanged)")
    ap.add_argument("--reset-at-switch", choices=("we", "rest") + tuple(RESET_PARTS), default=None,
                    help="EXP-038: at --switch-step reset W_E or all other parameters to init (+ their AdamW state); "
                         "EXP-067/069: or only one part of the rest (attn, mlp, unembed, qk, vo)")
    ap.add_argument("--rewind-at-switch", choices=REWIND_PARTS, default=None,
                    help="EXP-073: at --switch-step set this part (weights + AdamW state) back to its state after step --rewind-from")
    ap.add_argument("--rewind-from", type=int, default=None, help="EXP-073: step R of the rewind snapshot (0 = init)")
    ap.add_argument("--lr", type=float, default=None, help="rule 19a: override the preset learning rate (default: preset)")
    ap.add_argument("--weight-decay", type=float, default=None, help="rule 19a: override the preset AdamW weight decay (default: preset)")
    ap.add_argument("--train-frac", type=float, default=None, help="rule 19a: override the preset train fraction (split files must match)")
    ap.add_argument("--beta1", type=float, default=None, help="EXP-081: override AdamW beta1 (default: preset 0.9)")
    ap.add_argument("--beta2", type=float, default=None, help="EXP-081: override AdamW beta2 (default: preset 0.98)")
    ap.add_argument("--pre-switch-betas", default=None,
                    help="EXP-090: 'b1,b2' AdamW betas for steps 1..--switch-step; preset betas afterwards, moments rescaled so the bias-corrected moments stay continuous")
    ap.add_argument("--pre-switch-grad-every", type=int, default=1,
                    help="EXP-095: before the switch compute the gradient only every k steps and reuse it in between (1 = off)")
    ap.add_argument("--batch-size", type=int, default=0, help="L0: minibatch size (0 = full batch, unchanged)")
    ap.add_argument("--order", choices=("iid", "fixed", "stride"), default="iid",
                    help="L0: minibatch order: iid (new permutation per epoch), fixed (one permutation), stride (sorted by (a mod floor(sqrt p), a))")
    ap.add_argument("--optimizer", choices=("adamw", "sgdm"), default="adamw", help="L0: sgdm = SGD with momentum (decoupled matched decay)")
    ap.add_argument("--sgd-lr", type=float, default=None, help="L0: learning rate of --optimizer sgdm")
    ap.add_argument("--sgd-momentum", type=float, default=0.9, help="L0: momentum of --optimizer sgdm")
    ap.add_argument("--lr-scale", type=float, default=1.0,
                    help="EXP-039: lr * c on the first train set for steps <= 250, full lr afterwards (1.0 = off)")
    ap.add_argument("--lr-scale-after-switch", type=float, default=1.0,
                    help="P3 ELR arm: lr * c for the 500 steps after --switch-step, full lr otherwise (1.0 = off)")
    ap.add_argument("--we-init-scale", type=float, default=1.0,
                    help="EXP-040: scale the non-DC part of W_E[:p] by s right after init (checksum = plain init; 1.0 = off)")
    ap.add_argument("--plant-targets", default=None,
                    help="EXP-087: comma-separated k; add C x median init power at each k to W_E[:p] after init (off by default)")
    ap.add_argument("--plant-c", type=float, default=None, help="EXP-087: planted power per target as a multiple C of the median")
    ap.add_argument("--plant-noise", action="store_true",
                    help="EXP-087: instead add norm-matched zero-mean noise (control RN)")
    ap.add_argument("--spectra-at", default="",
                    help="EXP-036 Nachtrag d: extra comma-separated steps with stored W_E spectra (logging only)")
    ap.add_argument("--p", type=int, default=113, help="EXP-043: modulus (default 113 = unchanged)")
    ap.add_argument("--task", choices=("add", "mul"), default="add", help="EXP-043: task (default add = unchanged)")
    ap.add_argument("--arch", choices=("transformer", "mlp"), default="transformer",
                    help="EXP-045: shared-embedding MLP (default transformer = unchanged)")
    ap.add_argument("--device", default="cpu", help="rule 16: 'cpu' (default, unchanged) or 'cuda' (AMD ROCm via .venv-gpu)")
    ap.add_argument("--save-model", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if a.t0 < 1:
        ap.error("--t0 must be >= 1 (the loop starts at step 1; t0=0 would silently ban nothing)")
    run(a)


if __name__ == "__main__":
    main()
