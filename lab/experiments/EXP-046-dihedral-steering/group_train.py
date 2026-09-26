#!/usr/bin/env python3
"""EXP-046: train the study's 1-layer transformer (preset arch25k, full-batch AdamW) on composition in D_n.

Tokens 0..2n-1 are group elements (dihedral.py indexing), token 2n is '='; the config's p is the group order 2n,
so vocab, '=' token and output width follow unchanged. Input (a, b, '='), label a*b. Train = --split-file (flat
a*2n+b), test = complement. Stores the W_E irrep power (2-dim irreps k = 1..(n-1)/2) every 250 steps and the
top-5 at the end. Same seed order as freq_ban.py: threads, seed, model init on the CPU, then .to(device).

Run ONLY through lab/tools/guarded_run.py:
    python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-046-dihedral-steering/group_train.py \
        --seed 140 --split-file lab/experiments/EXP-046-dihedral-steering/splits/split_D59_seed140_eps2.0_F.npy --device cuda
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
sys.path.insert(0, str(HERE))

from grokverse.config import THRESHOLD_SETS, get_config  # noqa: E402
from grokverse.data import split_hash  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.seed import set_seed  # noqa: E402
from grokverse.train import all_transitions, evaluate  # noqa: E402
from grokverse.utils import git_commit, lib_versions  # noqa: E402

from dihedral import compose_table, irrep_basis, irrep_power  # noqa: E402

SPECTRUM_EVERY = 250
M = 5


def load_split(path: str, G: int, train_frac: float) -> np.ndarray:
    raw = np.load(path)                                    # fail closed, as freq_ban.py
    n_expected = int(round(train_frac * G * G))
    if (raw.ndim != 1 or not np.issubdtype(raw.dtype, np.integer) or len(raw) != n_expected
            or len(np.unique(raw)) != len(raw) or raw.min() < 0 or raw.max() >= G * G):
        raise SystemExit(f"[g] invalid split file {path}: need {n_expected} unique ints in [0, {G * G})")
    return raw.astype(np.int64)


def run(a: argparse.Namespace) -> dict:
    G = 2 * a.n
    cfg = get_config("arch25k", seed=a.seed, steps=a.steps, threads=a.threads, p=G)
    if cfg.equals_token != G or cfg.vocab_size != G + 1:
        raise SystemExit(f"[g] unexpected token layout: '=' {cfg.equals_token}, vocab {cfg.vocab_size}")
    if a.device != "cpu" and (not a.device.startswith("cuda") or not torch.cuda.is_available()):
        raise SystemExit(f"[g] device {a.device!r} not available")
    run_id = f"EXP-046_seed{a.seed}_{Path(a.split_file).stem}_dev{a.device.replace(':', '')}"
    out_dir = Path(a.out_root) / run_id
    rj = out_dir / "result.json"
    if not a.force and rj.exists() and json.loads(rj.read_text()).get("status") == "completed":
        print(f"[g] {run_id} already completed; use --force to overwrite", flush=True)
        raise SystemExit(0)
    out_dir.mkdir(parents=True, exist_ok=True)

    torch.set_num_threads(cfg.threads)
    set_seed(cfg.seed)
    T = compose_table(a.n)
    a_idx, b_idx = np.arange(G).repeat(G), np.tile(np.arange(G), G)
    x_all = torch.from_numpy(np.stack([a_idx, b_idx, np.full(G * G, G)], 1)).long()
    y_all = torch.from_numpy(T.reshape(-1)).long()
    tr = load_split(a.split_file, G, cfg.train_frac)
    te = np.setdiff1d(np.arange(G * G), tr)
    model = build_model(cfg)
    dev = torch.device(a.device)
    model = model.to(dev)
    trx, try_ = x_all[tr].to(dev), y_all[tr].to(dev)
    tex, tey = x_all[te].to(dev), y_all[te].to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay,
                            betas=(cfg.beta1, cfg.beta2))
    B, labels = irrep_basis(a.n)

    def power() -> np.ndarray:
        return irrep_power(model.W_E.detach().cpu().numpy().astype(np.float64)[:G], B, labels, a.n)

    def total_nonconst() -> float:                        # all W_E power except the trivial irrep (for concentration)
        W = model.W_E.detach().cpu().numpy().astype(np.float64)[:G]
        C = B.T @ W
        return float((C[1:] ** 2).sum())

    dense = {"train_steps": [], "train_acc": [], "train_loss": [], "test_steps": [], "test_acc": [], "test_loss": [],
             "eval_every_train": cfg.eval_every_train, "eval_every_test": cfg.eval_every_test}
    spectra, spectra_steps, sign_power = [], [], []
    res = {"exp_id": "EXP-046", "run_id": run_id, "status": "running", "seed": a.seed, "group": f"D{a.n}",
           "n": a.n, "order": G, "split_file": a.split_file, "split_hash": split_hash(torch.from_numpy(tr)),
           "device": a.device,
           "device_name": torch.cuda.get_device_name(dev) if dev.type == "cuda" else platform.processor(),
           "max_steps": a.steps, "config": cfg.to_dict(), "git_commit": git_commit(), "versions": lib_versions(),
           "platform": platform.platform(), "argv": sys.argv, "start_utc": datetime.now(timezone.utc).isoformat()}

    def dense_eval(step: int) -> None:
        if step % cfg.eval_every_train == 0:
            loss, acc = evaluate(model, trx, try_, G)
            dense["train_steps"].append(step); dense["train_acc"].append(acc); dense["train_loss"].append(loss)
        if step % cfg.eval_every_test == 0:
            loss, acc = evaluate(model, tex, tey, G)
            dense["test_steps"].append(step); dense["test_acc"].append(acc); dense["test_loss"].append(loss)

    def spectrum(step: int) -> None:
        spectra_steps.append(step)
        spectra.append(power())
        W = model.W_E.detach().cpu().numpy().astype(np.float64)[:G]
        sign_power.append(float(((B.T @ W)[1]) @ ((B.T @ W)[1])))

    def write(status: str) -> None:
        res.update({"status": status, "steps_completed": step, "dense": dense,
                    "transitions": all_transitions(dense) if dense["test_steps"] else None,
                    "elapsed_s": round(time.perf_counter() - t0, 1),
                    "sec_per_step": round((time.perf_counter() - t0) / max(step, 1), 5), "sign_power": sign_power})
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
        loss = F.cross_entropy(model.logits_last(trx)[:, :G], try_)
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
    pw = power()
    res["final_top_m_irreps"] = sorted((np.argsort(-pw, kind="stable")[:M] + 1).tolist())
    res["final_top_m_share"] = float(np.sort(pw)[::-1][:M].sum() / total_nonconst())
    res["final_acc"] = {"train": evaluate(model, trx, try_, G)[1], "test": evaluate(model, tex, tey, G)[1]}
    res["end_utc"] = datetime.now(timezone.utc).isoformat()
    write("completed")
    print(f"[g] {run_id} completed: {step} steps, gen {res.get('generalization_step')}, top-{M} "
          f"{res['final_top_m_irreps']} (share {res['final_top_m_share']:.3f}), {res['sec_per_step']} s/step", flush=True)
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description="EXP-046 dihedral composition")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--n", type=int, default=59)
    ap.add_argument("--split-file", required=True)
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--out-root", default=str(HERE / "raw"))
    ap.add_argument("--force", action="store_true")
    run(ap.parse_args())


if __name__ == "__main__":
    main()
