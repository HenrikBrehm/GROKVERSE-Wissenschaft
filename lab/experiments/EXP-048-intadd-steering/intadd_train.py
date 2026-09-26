#!/usr/bin/env python3
"""EXP-048: the study's 1-layer transformer (preset arch25k, full-batch AdamW) on NON-modular integer addition.

Inputs a, b in 0..112 (tokens 0..112), '=' token = 225; label c = a + b in 0..224. The config's p is the number of
outputs (225), so vocab = 226, '=' = 225 and the output width 225 follow unchanged; embedding rows 113..224 are never
used as inputs (they only decay). Train = --split-file (flat a*113+b), test = complement. Stores the DFT power of
W_E rows 0..112 (k = 1..56, k and 113-k combined) every 250 steps, the final W_E rows 0..112, and the linearity
R^2 of W_E rows on a (number-line measure). Same seed order as freq_ban.py / group_train.py (init on the CPU,
then .to(device)).

Run ONLY through lab/tools/guarded_run.py.
"""
from __future__ import annotations

import argparse
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
sys.path.insert(0, str(ROOT / "lab" / "tools"))

from grokverse.config import THRESHOLD_SETS, get_config  # noqa: E402
from grokverse.data import split_hash  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.seed import set_seed  # noqa: E402
from grokverse.train import all_transitions, evaluate  # noqa: E402
from grokverse.utils import git_commit, lib_versions  # noqa: E402
from trainer_guard import config_fingerprint, should_skip  # noqa: E402

P = 113
NC = 2 * P - 1
KMAX = (P - 1) // 2
SPECTRUM_EVERY = 250
M = 5


def dft_power(W: np.ndarray) -> np.ndarray:
    """Power of the P x d matrix W at k = 1..56 over the input index (k and P-k combined; k = 0 excluded)."""
    pw = (np.abs(np.fft.fft(W, axis=0)) ** 2).sum(axis=1)
    return pw[1:KMAX + 1] + pw[P - KMAX:][::-1]


def linear_r2(W: np.ndarray) -> float:
    """Share of the (column-centered) W variance explained by a linear function of the input index a."""
    Wc = W - W.mean(0, keepdims=True)
    x = np.arange(P, dtype=float) - (P - 1) / 2
    beta = x @ Wc / (x @ x)
    return float(((x[:, None] * beta[None]) ** 2).sum() / (Wc ** 2).sum())


def load_split(path: str, n_expected: int) -> np.ndarray:
    raw = np.load(path)
    if (raw.ndim != 1 or not np.issubdtype(raw.dtype, np.integer) or len(raw) != n_expected
            or len(np.unique(raw)) != len(raw) or raw.min() < 0 or raw.max() >= P * P):
        raise SystemExit(f"[i] invalid split file {path}: need {n_expected} unique ints in [0, {P * P})")
    return raw.astype(np.int64)


def run(a: argparse.Namespace) -> dict:
    cfg = get_config("arch25k", seed=a.seed, steps=a.steps, threads=a.threads, p=NC)
    if cfg.equals_token != NC or cfg.vocab_size != NC + 1:
        raise SystemExit(f"[i] unexpected token layout: '=' {cfg.equals_token}, vocab {cfg.vocab_size}")
    if a.device != "cpu" and (not a.device.startswith("cuda") or not torch.cuda.is_available()):
        raise SystemExit(f"[i] device {a.device!r} not available")
    run_id = f"EXP-048_seed{a.seed}_{Path(a.split_file).stem}_dev{a.device.replace(':', '')}"
    out_dir = Path(a.out_root) / run_id
    rj = out_dir / "result.json"
    fingerprint, fp_fields = config_fingerprint(a)     # session 19: resume guard, lab/tools/trainer_guard.py
    if should_skip(rj, fingerprint, a.steps, a.force, "i", run_id):
        raise SystemExit(0)
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in ("result.json", "spectra.npy", "spectra_steps.npy", "we_final.npy"):
        (out_dir / f).unlink(missing_ok=True)

    torch.set_num_threads(cfg.threads)
    set_seed(cfg.seed)
    a_idx, b_idx = np.arange(P).repeat(P), np.tile(np.arange(P), P)
    x_all = torch.from_numpy(np.stack([a_idx, b_idx, np.full(P * P, NC)], 1)).long()
    y_all = torch.from_numpy(a_idx + b_idx).long()
    tr = load_split(a.split_file, int(round(cfg.train_frac * P * P)))
    te = np.setdiff1d(np.arange(P * P), tr)
    model = build_model(cfg)
    dev = torch.device(a.device)
    model = model.to(dev)
    trx, try_ = x_all[tr].to(dev), y_all[tr].to(dev)
    tex, tey = x_all[te].to(dev), y_all[te].to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay,
                            betas=(cfg.beta1, cfg.beta2))

    def we() -> np.ndarray:
        return model.W_E.detach().cpu().numpy().astype(np.float64)[:P]

    dense = {"train_steps": [], "train_acc": [], "train_loss": [], "test_steps": [], "test_acc": [], "test_loss": [],
             "eval_every_train": cfg.eval_every_train, "eval_every_test": cfg.eval_every_test}
    spectra, spectra_steps, lin = [], [], []
    res = {"exp_id": "EXP-048", "run_id": run_id, "status": "running", "config_fingerprint": fingerprint,
           "fingerprint_fields": fp_fields, "seed": a.seed, "task": "intadd", "n_in": P,
           "n_out": NC, "split_file": a.split_file, "split_hash": split_hash(torch.from_numpy(tr)),
           "device": a.device,
           "device_name": torch.cuda.get_device_name(dev) if dev.type == "cuda" else platform.processor(),
           "max_steps": a.steps, "config": cfg.to_dict(), "git_commit": git_commit(), "versions": lib_versions(),
           "platform": platform.platform(), "argv": sys.argv, "start_utc": datetime.now(timezone.utc).isoformat()}

    def dense_eval(step: int) -> None:
        if step % cfg.eval_every_train == 0:
            loss, acc = evaluate(model, trx, try_, NC)
            dense["train_steps"].append(step); dense["train_acc"].append(acc); dense["train_loss"].append(loss)
        if step % cfg.eval_every_test == 0:
            loss, acc = evaluate(model, tex, tey, NC)
            dense["test_steps"].append(step); dense["test_acc"].append(acc); dense["test_loss"].append(loss)

    def spectrum(step: int) -> None:
        W = we()
        spectra_steps.append(step)
        spectra.append(dft_power(W))
        lin.append(linear_r2(W))

    def write(status: str) -> None:
        res.update({"status": status, "steps_completed": step, "dense": dense,
                    "transitions": all_transitions(dense) if dense["test_steps"] else None,
                    "elapsed_s": round(time.perf_counter() - t0, 1),
                    "sec_per_step": round((time.perf_counter() - t0) / max(step, 1), 5), "linear_r2": lin})
        if dev.type == "cuda":
            res["cuda_max_mem_mb"] = round(torch.cuda.max_memory_allocated(dev) / 2**20, 1)
        np.save(out_dir / "spectra.npy", np.asarray(spectra))
        np.save(out_dir / "spectra_steps.npy", np.asarray(spectra_steps))
        tmp = out_dir / "result.json.tmp"
        tmp.write_text(json.dumps(res, indent=1))
        os.replace(tmp, rj)

    step, t0 = 0, time.perf_counter()
    dense_eval(0); spectrum(0)
    gen_thr = THRESHOLD_SETS["primary"][1]
    for step in range(1, a.steps + 1):
        model.train()
        loss = F.cross_entropy(model.logits_last(trx)[:, :NC], try_)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        dense_eval(step)
        if step % SPECTRUM_EVERY == 0:
            spectrum(step)
        if ("generalization_step" not in res and step % cfg.eval_every_test == 0
                and dense["test_acc"][-1] >= gen_thr):
            res["generalization_step"] = step
        if step % 500 == 0:
            write("running")
    if step % SPECTRUM_EVERY:
        spectrum(step)
    W = we()
    np.save(out_dir / "we_final.npy", W.astype(np.float32))
    pw = dft_power(W)
    res["final_top_m_freqs"] = sorted((np.argsort(-pw, kind="stable")[:M] + 1).tolist())
    res["final_top_m_share"] = float(np.sort(pw)[::-1][:M].sum() / pw.sum())
    res["final_acc"] = {"train": evaluate(model, trx, try_, NC)[1], "test": evaluate(model, tex, tey, NC)[1]}
    res["end_utc"] = datetime.now(timezone.utc).isoformat()
    write("completed")
    print(f"[i] {run_id} completed: {step} steps, gen {res.get('generalization_step')}, top-{M} "
          f"{res['final_top_m_freqs']} (share {res['final_top_m_share']:.3f}), linR2 {lin[-1]:.3f}, "
          f"{res['sec_per_step']} s/step", flush=True)
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description="EXP-048 integer addition")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--split-file", required=True)
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--out-root", default=str(HERE / "raw"))
    ap.add_argument("--force", action="store_true")
    run(ap.parse_args())


if __name__ == "__main__":
    main()
