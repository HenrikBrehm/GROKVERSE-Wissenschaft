#!/usr/bin/env python3
"""EXP-080 trainer (N36 pilot, session 26, UNTESTED): task switch a+b -> a-b (routing) or a^2+b^2 (content) with an optional reset.

The study's one-layer transformer (preset arch25k, add 113, the seed's own random 30 % split from make_dataset) is trained on a+b for
--switch-step steps with full-batch AdamW (same order as lab/paper/repro/train.py: threads, seed, dataset, init on the CPU, .to(device),
AdamW). After the optimizer update of step t the LABELS change on the SAME pairs (new task), and optionally one part is reset to its init
weights with its AdamW state dropped (qk = W_Q, W_K; vo = W_V, W_O; as freq_ban --reset-at-switch). Then --post-steps steps on the new task.
Logged: training loss of every post-switch step (new labels), test accuracy of the new task every 100 steps and at the end.

  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-080-route-vs-content/train_switch.py --seed 800 --switch-step 50 --new-task sub --reset qk --device cuda --out DIR
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
sys.path.insert(0, str(ROOT / "training"))
from grokverse.config import get_config  # noqa: E402
from grokverse.data import make_dataset  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.seed import set_seed  # noqa: E402

RESET = {"none": (), "qk": ("W_Q", "W_K"), "vo": ("W_V", "W_O")}


def new_labels(x: torch.Tensor, task: str, p: int) -> torch.Tensor:
    a, b = x[:, 0], x[:, 1]
    if task == "sub":                       # antisymmetric: needs position-dependent processing (routing)
        return (a - b) % p
    if task == "sq":                        # symmetric: new content (x -> x^2), no new routing
        return (a * a + b * b) % p
    raise ValueError(task)


@torch.no_grad()
def accuracy(model: torch.nn.Module, x: torch.Tensor, y: torch.Tensor, p: int) -> float:
    return (model.logits_last(x)[:, :p].argmax(-1) == y).float().mean().item()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--switch-step", type=int, required=True)
    ap.add_argument("--new-task", choices=("sub", "sq"), required=True)
    ap.add_argument("--reset", choices=tuple(RESET), default="none")
    ap.add_argument("--post-steps", type=int, default=2000)
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.switch_step < 1 or a.post_steps < 1000:
        raise SystemExit("--switch-step >= 1 and --post-steps >= 1000 (the primary AUC covers 1000 post-switch steps)")
    cfg = get_config("arch25k", seed=a.seed, steps=a.switch_step + a.post_steps, threads=a.threads)
    p = cfg.p
    torch.set_num_threads(cfg.threads)
    set_seed(cfg.seed)
    data = make_dataset(cfg)                               # own generator: global RNG untouched (as repro/train.py)
    model = build_model(cfg)
    dev = torch.device(a.device)
    model = model.to(dev)
    trx, tex = data["train_x"].to(dev), data["test_x"].to(dev)
    y_old = data["train_y"].to(dev)
    y_new, te_new = new_labels(trx, a.new_task, p), new_labels(tex, a.new_task, p)
    init = {nm: q.detach().clone() for nm, q in model.named_parameters()}
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay, betas=(cfg.beta1, cfg.beta2))
    post_loss, test_curve, t0 = [], [], time.perf_counter()
    acc_old_at_switch = None
    for step in range(1, a.switch_step + a.post_steps + 1):
        model.train()
        y = y_old if step <= a.switch_step else y_new
        loss = F.cross_entropy(model.logits_last(trx)[:, :p], y)
        if step > a.switch_step:
            post_loss.append(float(loss.detach()))
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        if step == a.switch_step:
            acc_old_at_switch = accuracy(model, trx, y_old, p)
            with torch.no_grad():
                for nm, q in model.named_parameters():
                    if nm in RESET[a.reset]:
                        q.copy_(init[nm])
                        opt.state.pop(q, None)
        if step > a.switch_step and (step - a.switch_step) % 100 == 0:
            test_curve.append([step - a.switch_step, accuracy(model, tex, te_new, p)])
    pl = np.asarray(post_loss)
    if not np.all(np.isfinite(pl)):
        raise SystemExit("non-finite post-switch loss")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "post_loss.npy", pl)
    res = {"trainer": "lab/experiments/EXP-080-route-vs-content/train_switch.py", "argv": sys.argv, "seed": a.seed, "switch_step": a.switch_step,
           "new_task": a.new_task, "reset": a.reset, "post_steps": a.post_steps, "device": a.device, "config": cfg.to_dict(),
           "train_acc_old_at_switch": acc_old_at_switch, "auc1000": float(pl[:1000].mean()),
           "final": {"train_acc_new": accuracy(model, trx, y_new, p), "test_acc_new": accuracy(model, tex, te_new, p)},
           "test_curve": test_curve, "sec_per_step": round((time.perf_counter() - t0) / (a.switch_step + a.post_steps), 5),
           "versions": {"python": platform.python_version(), "torch": torch.__version__, "numpy": np.__version__},
           "end_utc": datetime.now(timezone.utc).isoformat()}
    (out / "result.json").write_text(json.dumps(res, indent=1), encoding="utf-8")   # written last: marks a complete run
    print(f"[EXP-080] seed {a.seed} t {a.switch_step} {a.new_task} reset {a.reset}: auc1000 {res['auc1000']:.4f}, "
          f"test acc new {res['final']['test_acc_new']:.3f}", flush=True)


if __name__ == "__main__":
    main()
