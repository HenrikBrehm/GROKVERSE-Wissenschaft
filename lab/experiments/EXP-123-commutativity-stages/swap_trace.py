#!/usr/bin/env python3
"""EXP-123 (session 55): dense commutativity trace during full-batch training (read-only measurement, no intervention).

Same training path as lab/paper/repro/train.py without switch/minibatch (imports its helpers; same operation order: threads, seed,
dataset, model init on the CPU, .to(device), AdamW, full-batch cross-entropy on logits_last[:, :p]), so the overall test curve must
equal the frozen R5 freq_ban run of the same seed/split (technical check in analyze.py). Every --every steps (default 25, the
trainer's test cadence) it records train accuracy, overall test accuracy, and test accuracy split into held-out pairs (a, b) whose
swapped pair (b, a) is in the training split (acc_swap) and the others (acc_other). Stops --after-gen steps after the first test
accuracy >= 0.95 (primary threshold) or at --steps.

  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-123-commutativity-stages/swap_trace.py \
      --seed 2743 --split-file lab/confirm/r5_splits/r5_u0_R.npy --test-file lab/confirm/r5_splits/r5_u0_test.npy --device cuda --out OUT
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "lab" / "paper" / "repro"))
sys.path.insert(0, str(ROOT / "training"))

import train as repro  # noqa: E402  (lab/paper/repro/train.py: load_idx, INPUT_SHA256)
from grokverse.config import THRESHOLD_SETS, get_config  # noqa: E402
from grokverse.data import make_dataset  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.seed import set_seed  # noqa: E402


@torch.no_grad()
def correct(model: torch.nn.Module, x: torch.Tensor, y: torch.Tensor, p: int) -> torch.Tensor:
    return model.logits_last(x)[:, :p].argmax(-1) == y


def swap_mask(tr: np.ndarray, te: np.ndarray, p: int) -> np.ndarray:
    """True for held-out pairs (a, b) = divmod(idx, p) whose swapped index b*p + a is in the training split."""
    a, b = te // p, te % p
    return np.isin(b * p + a, tr)


def run(a: argparse.Namespace) -> dict:
    cfg = get_config("arch25k", seed=a.seed, steps=a.steps, threads=a.threads, p=a.p, task="add")
    p = cfg.p
    torch.set_num_threads(cfg.threads)
    set_seed(cfg.seed)
    data = make_dataset(cfg)
    tr = repro.load_idx(a.split_file, p, int(round(cfg.train_frac * p * p)))
    te = torch.from_numpy(np.sort(repro.load_idx(a.test_file, p, None).numpy()))
    if np.intersect1d(te.numpy(), tr.numpy()).size:
        raise SystemExit("test set overlaps the train set")
    sw = swap_mask(tr.numpy(), te.numpy(), p)
    X, Y = data["all_x"], data["all_y"]
    model = build_model(cfg)
    dev = torch.device(a.device)
    model = model.to(dev)
    trx, try_, tex, tey = X[tr].to(dev), Y[tr].to(dev), X[te].to(dev), Y[te].to(dev)
    swd = torch.from_numpy(sw).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay, betas=(cfg.beta1, cfg.beta2))
    gen_thr, gen_step = THRESHOLD_SETS["primary"][1], None
    trace = {"step": [], "train": [], "test": [], "swap": [], "other": []}

    def record(step: int) -> float:
        ok_tr = correct(model, trx, try_, p).float().mean().item()
        ok = correct(model, tex, tey, p)
        acc = ok.float().mean().item()
        trace["step"].append(step); trace["train"].append(ok_tr); trace["test"].append(acc)
        trace["swap"].append(ok[swd].float().mean().item()); trace["other"].append(ok[~swd].float().mean().item())
        return acc

    t0 = time.perf_counter()
    record(0)
    last = a.steps
    for step in range(1, a.steps + 1):
        model.train()
        loss = F.cross_entropy(model.logits_last(trx)[:, :p], try_)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        if step % a.every == 0:
            acc = record(step)
            if gen_step is None and acc >= gen_thr:
                gen_step = step
            if gen_step is not None and step >= gen_step + a.after_gen:
                last = step
                break
        if step % 1000 == 0:
            print(f"step {step} train {trace['train'][-1]:.3f} test {trace['test'][-1]:.3f} swap {trace['swap'][-1]:.3f} "
                  f"other {trace['other'][-1]:.3f}", flush=True)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    res = {"trainer": "lab/experiments/EXP-123-commutativity-stages/swap_trace.py", "argv": sys.argv, "seed": a.seed,
           "device": a.device, "config": cfg.to_dict(), "steps_max": a.steps, "last_step": last, "every": a.every,
           "generalization_step": gen_step, "n_test": int(len(te)), "n_swap": int(sw.sum()), "trace": trace,
           "sec_per_step": round((time.perf_counter() - t0) / max(last, 1), 5),
           "versions": {"python": platform.python_version(), "torch": torch.__version__, "numpy": np.__version__},
           "platform": platform.platform(), "end_utc": datetime.now(timezone.utc).isoformat(),
           "input_sha256": dict(repro.INPUT_SHA256), "status": "completed"}
    tmp = out / "result.json.tmp"
    tmp.write_text(json.dumps(res), encoding="utf-8")
    tmp.replace(out / "result.json")
    print(f"done: last {last}, gen {gen_step}, test {trace['test'][-1]:.3f}", flush=True)
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description="EXP-123 dense commutativity trace (full batch, arch25k, add)")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--split-file", required=True)
    ap.add_argument("--test-file", required=True)
    ap.add_argument("--p", type=int, default=113)
    ap.add_argument("--steps", type=int, default=8000)
    ap.add_argument("--every", type=int, default=25)
    ap.add_argument("--after-gen", type=int, default=250)
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if (Path(a.out) / "result.json").exists():
        print(f"skip: {a.out} already completed", flush=True)
        return
    run(a)


if __name__ == "__main__":
    main()
