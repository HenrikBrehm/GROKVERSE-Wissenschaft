"""EXP-102 (rule 20e, language-model ladder, stage 1): does K2 survive when (a + b) mod p is trained as a token sequence?

Small trainer with one switch per ladder rung; with every switch off it is the study's setup of freq_ban.py (arch25k,
one-layer transformer, AdamW lr 1e-3, wd 1, betas 0.9/0.98, full batch, cross-entropy on the p number logits of the
last position). Same parameter shapes, creation and init order as training/grokverse/models/transformer.py, so with
the switches off the init is bit-identical to the study model for the same seed (checked in --selftest).

Switches (each on its own):
  --op-token      sequence a + b = (n_ctx 4) instead of a b = ; '+' is a new vocabulary entry (p + 1)
  --full-softmax  answer loss over the whole vocabulary instead of the p number logits
  --tie           output layer = W_E^T (weight tying); W_U does not exist
  --loss answer | all | all_but_b
                  answer: only the '=' position predicts c (default). all: next-token loss at every position
                  (inputs a (+) b =, targets (+) b = c); needs --full-softmax. all_but_b: like all without the position
                  that predicts b (the best prediction of b there is p(b | a) of the TRAIN SET, i.e. the steering
                  signal itself; this arm separates "pair structure as a target" from "autoregressive format").
                  Positions are summed (each a batch mean), so the answer term has the same weight in every mode.
  --batch-size B  0 = full batch (default); otherwise i.i.d. minibatches, a fresh permutation per epoch from its own
                  stream (numpy SeedSequence [102, seed, 1] -> torch.Generator); last batch of an epoch may be smaller.

Measure: W_E[:p] snapshots (number tokens only) at SNAP_STEPS and at the end; Delta_pow as in P1 from these (analysis
script later). Test accuracy on the complement of the split (argmax over the p number logits of the answer position).

Usage (every run through the guard):
  python lab/tools/guarded_run.py -- python lab/experiments/EXP-102-lm-ladder-stage1/lm_ladder.py --selftest
  python lab/tools/guarded_run.py -- <python> lab/experiments/EXP-102-lm-ladder-stage1/lm_ladder.py --seed S \
      --split-file lab/confirm/splits/<stem>.npy --steps 2000 --device cuda [--op-token] [--full-softmax] [--tie] \
      [--loss all] [--batch-size 256] --out-root lab/experiments/EXP-102-lm-ladder-stage1/raw
UNTESTED (written in session 44 with the run window closed; reviewed read-only: train rows in file order as freq_ban.py,
threads in the run id, lock file, skip only if split and script hashes match).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "training"))
from grokverse.config import THRESHOLD_SETS, get_config  # noqa: E402
from grokverse.seed import set_seed  # noqa: E402

SNAP_STEPS = (0, 25, 50, 100, 250, 500, 1000, 2000)
EVAL_EVERY = 25
GEN_THR = THRESHOLD_SETS["primary"][1]


class LadderTransformer(nn.Module):
    """The study's OneLayerTransformer with a configurable vocabulary, context length and optional tying."""

    def __init__(self, cfg, vocab: int, n_ctx: int, tie: bool):
        super().__init__()
        d, h, dh = cfg.d_model, cfg.n_heads, cfg.d_head
        self.cfg, self.tie = cfg, tie
        self.W_E = nn.Parameter(torch.empty(vocab, d))            # same creation order as the study model
        self.W_pos = nn.Parameter(torch.empty(n_ctx, d))
        self.W_Q = nn.Parameter(torch.empty(h, d, dh))
        self.W_K = nn.Parameter(torch.empty(h, d, dh))
        self.W_V = nn.Parameter(torch.empty(h, d, dh))
        self.W_O = nn.Parameter(torch.empty(h, dh, d))
        self.W_in = nn.Parameter(torch.empty(d, cfg.d_mlp))
        self.W_out = nn.Parameter(torch.empty(cfg.d_mlp, d))
        self.W_U = None if tie else nn.Parameter(torch.empty(d, vocab))
        s = cfg.init_scale                                           # same init order and scales as the study model
        nn.init.normal_(self.W_E, std=s / math.sqrt(d))
        nn.init.normal_(self.W_pos, std=s / math.sqrt(d))
        for W in (self.W_Q, self.W_K, self.W_V):
            nn.init.normal_(W, std=s / math.sqrt(d))
        nn.init.normal_(self.W_O, std=s / math.sqrt(dh * h))
        nn.init.normal_(self.W_in, std=s / math.sqrt(d))
        nn.init.normal_(self.W_out, std=s / math.sqrt(cfg.d_mlp))
        if not tie:
            nn.init.normal_(self.W_U, std=s / math.sqrt(d))

    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        T = tokens.shape[1]
        x = self.W_E[tokens] + self.W_pos[None, :T, :]
        q = torch.einsum("btd,hde->bhte", x, self.W_Q)
        k = torch.einsum("btd,hde->bhte", x, self.W_K)
        v = torch.einsum("btd,hde->bhte", x, self.W_V)
        scores = torch.einsum("bhte,bhse->bhts", q, k) / math.sqrt(self.cfg.d_head)
        mask = torch.triu(torch.ones(T, T, dtype=torch.bool, device=x.device), diagonal=1)
        attn = scores.masked_fill(mask, float("-inf")).softmax(dim=-1)
        z = torch.einsum("bhts,bhse->bhte", attn, v)
        x = x + torch.einsum("bhte,hed->btd", z, self.W_O)
        x = x + torch.einsum("btf,fd->btd", torch.relu(torch.einsum("btd,df->btf", x, self.W_in)), self.W_out)
        return torch.einsum("btd,dv->btv", x, self.W_E.T if self.tie else self.W_U)


def sequences(idx: torch.Tensor, p: int, op_token: bool) -> tuple[torch.Tensor, torch.Tensor]:
    """Inputs [a, (+), b, =] and next-token targets [(+), b, =, c] for flat indices a*p + b ('=' = p, '+' = p + 1)."""
    a, b = idx // p, idx % p
    c = (a + b) % p
    eq, plus = torch.full_like(a, p), torch.full_like(a, p + 1)
    if op_token:
        return torch.stack([a, plus, b, eq], 1), torch.stack([plus, b, eq, c], 1)
    return torch.stack([a, b, eq], 1), torch.stack([b, eq, c], 1)


def loss_positions(mode: str, op_token: bool) -> list[int]:
    T = 4 if op_token else 3
    if mode == "answer":
        return [T - 1]
    if mode == "all":
        return list(range(T))
    b_pos = 1 if op_token else 0                                     # the position whose target is b
    return [t for t in range(T) if t != b_pos]


def loss_fn(logits: torch.Tensor, tgt: torch.Tensor, pos: list[int], p: int, full_softmax: bool) -> torch.Tensor:
    if not full_softmax:                                             # study setup: answer position, number logits only
        return F.cross_entropy(logits[:, -1, :p], tgt[:, -1])
    return sum(F.cross_entropy(logits[:, t, :], tgt[:, t]) for t in pos)


def batches(n: int, B: int, seed: int):
    """Endless i.i.d. minibatches: a fresh permutation per epoch from the stream SeedSequence([102, seed, 1])."""
    g = torch.Generator().manual_seed(int(np.random.SeedSequence([102, seed, 1]).generate_state(1, dtype=np.uint64)[0]
                                          % (2 ** 63)))
    while True:
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, B):
            yield perm[i:i + B]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_atomic(path: Path, arr=None, obj=None) -> None:
    tmp = path.with_name(path.name + ".tmp")
    if obj is not None:
        tmp.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    else:
        with open(tmp, "wb") as f:
            np.save(f, arr)
    os.replace(tmp, path)


def run(a: argparse.Namespace) -> None:
    if a.loss != "answer" and not a.full_softmax:
        raise SystemExit("--loss all/all_but_b needs --full-softmax")
    if a.tie and not a.full_softmax:
        raise SystemExit("--tie only with --full-softmax (design: the tie rung builds on the fs rung)")
    p = 113
    split = Path(a.split_file)
    raw = np.load(split)
    cfg = get_config("arch25k", seed=a.seed, steps=a.steps, threads=a.threads)
    if raw.ndim != 1 or len(raw) != int(round(cfg.train_frac * p * p)) or len(np.unique(raw)) != len(raw) \
            or raw.min() < 0 or raw.max() >= p * p:
        raise SystemExit(f"invalid split file {split}")
    if a.device.startswith("cuda") and not torch.cuda.is_available():
        raise SystemExit(f"device {a.device} requested but CUDA is not available")
    run_id = (f"lad_seed{a.seed}_{split.stem}_op{int(a.op_token)}_fs{int(a.full_softmax)}_tie{int(a.tie)}"
              f"_loss{a.loss}_B{a.batch_size}_steps{a.steps}_thr{a.threads}_{a.device}")
    out = Path(a.out_root) / run_id
    prev = previous(out)
    if prev is not None and prev.get("status") == "completed":
        if prev.get("split_sha256") != sha(split) or prev.get("script_sha256") != sha(Path(__file__)):
            raise SystemExit(f"{run_id}: completed with another split or script version; use a new --out-root")
        print(f"skip {run_id} (completed)")
        return
    out.mkdir(parents=True, exist_ok=True)
    lock = out / "run.lock"
    try:                                                                  # review s44: one process per run id
        with open(lock, "x", encoding="utf-8") as f:
            f.write(str(os.getpid()))
    except FileExistsError:
        raise SystemExit(f"{run_id}: {lock} exists (running elsewhere, or stale after a crash: inspect, then move aside)")
    try:
        train(a, cfg, raw, split, run_id, out)
    finally:
        lock.unlink(missing_ok=True)


def previous(out: Path) -> dict | None:
    try:
        return json.loads((out / "result.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def train(a: argparse.Namespace, cfg, raw: np.ndarray, split: Path, run_id: str, out: Path) -> None:
    p = 113
    torch.set_num_threads(a.threads)
    set_seed(cfg.seed)                                                   # as freq_ban.py: seed, then build the model
    vocab = p + 1 + int(a.op_token)
    model = LadderTransformer(cfg, vocab, 4 if a.op_token else 3, a.tie)
    dev = torch.device(a.device)
    model = model.to(dev)
    tr = torch.from_numpy(raw.astype(np.int64))       # file order, as freq_ban.py (review s44: sorting breaks bit-identity)
    te = torch.from_numpy(np.setdiff1d(np.arange(p * p), raw).astype(np.int64))
    trx, trt = (t.to(dev) for t in sequences(tr, p, a.op_token))
    tex, tet = (t.to(dev) for t in sequences(te, p, a.op_token))
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay, betas=(cfg.beta1, cfg.beta2))
    pos = loss_positions(a.loss, a.op_token)
    it = batches(len(tr), a.batch_size, a.seed) if a.batch_size else None
    snaps, snap_steps, curve, events = [], [], [], {}
    t0 = time.perf_counter()

    @torch.no_grad()
    def evaluate(step: int) -> None:
        model.eval()
        acc = lambda x, t: float((model(x)[:, -1, :p].argmax(1) == t[:, -1]).float().mean())   # noqa: E731
        curve.append([step, acc(trx, trt), acc(tex, tet)])
        model.train()

    def snap(step: int) -> None:
        snaps.append(model.W_E.detach().cpu().numpy()[:p].astype(np.float32).copy())
        snap_steps.append(step)

    snap(0)
    evaluate(0)
    step = 0
    for step in range(1, a.steps + 1):
        if it is None:
            x, t = trx, trt
        else:
            bi = next(it).to(dev)
            x, t = trx[bi], trt[bi]
        loss = loss_fn(model(x), t, pos, p, a.full_softmax)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        if step % EVAL_EVERY == 0:                   # finiteness only here: a per-step check syncs the GPU every step
            if not torch.isfinite(loss):
                events["nonfinite_step"] = step
                break
            evaluate(step)
            if "generalization_step" not in events and curve[-1][2] >= GEN_THR:
                events["generalization_step"] = step
        if step in SNAP_STEPS or step % 1000 == 0 or step == a.steps:
            if not snap_steps or snap_steps[-1] != step:
                snap(step)
    status = "error" if "nonfinite_step" in events else "completed"
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except OSError:
        commit = None
    save_atomic(out / "we_snapshots.npy", np.asarray(snaps))
    save_atomic(out / "we_snapshot_steps.npy", np.asarray(snap_steps))
    save_atomic(out / "result.json", obj={
        "status": status, "run_id": run_id, "seed": a.seed, "device": a.device, "threads": a.threads,
        "steps": a.steps, "steps_completed": step, "op_token": a.op_token, "full_softmax": a.full_softmax, "tie": a.tie,
        "loss": a.loss, "loss_positions": pos, "batch_size": a.batch_size, "vocab": vocab,
        "split_file": str(split).replace("\\", "/"), "split_sha256": sha(split), "script_sha256": sha(Path(__file__)),
        "commit": commit, "torch": torch.__version__, "python": platform.python_version(),
        "config": {"lr": cfg.lr, "weight_decay": cfg.weight_decay, "betas": [cfg.beta1, cfg.beta2], "d_model": cfg.d_model,
                   "d_mlp": cfg.d_mlp, "n_heads": cfg.n_heads, "train_frac": cfg.train_frac, "init_scale": cfg.init_scale},
        "events": events, "curve": curve, "elapsed_s": round(time.perf_counter() - t0, 1)})
    print(f"{run_id}: {status}, test acc {curve[-1][2]:.3f}, gen {events.get('generalization_step')}")


def selftest() -> None:
    from grokverse.models.transformer import OneLayerTransformer
    p = 113
    cfg = get_config("arch25k", seed=7)
    set_seed(7)
    ref = OneLayerTransformer(cfg)
    set_seed(7)
    lad = LadderTransformer(cfg, p + 1, 3, tie=False)
    for (n1, q1), (n2, q2) in zip(ref.named_parameters(), lad.named_parameters()):
        assert n1 == n2 and torch.equal(q1, q2), n1
    idx = torch.tensor([0, 5, 113 * 7 + 3, 113 * 113 - 1])
    x, t = sequences(idx, p, False)
    assert x.tolist()[2] == [7, 3, 113] and t.tolist()[2] == [3, 113, 10] and t.tolist()[3] == [112, 113, 111]
    xo, to = sequences(idx, p, True)
    assert xo.tolist()[2] == [7, 114, 3, 113] and to.tolist()[2] == [114, 3, 113, 10]
    assert torch.equal(ref(x), lad(x))
    assert torch.equal(F.cross_entropy(ref.logits_last(x)[:, :p], t[:, -1]), loss_fn(lad(x), t, [2], p, False))
    assert loss_positions("answer", True) == [3] and loss_positions("all", False) == [0, 1, 2]
    assert loss_positions("all_but_b", True) == [0, 2, 3] and loss_positions("all_but_b", False) == [1, 2]
    set_seed(7)
    tied = LadderTransformer(cfg, p + 2, 4, tie=True)
    assert tied.W_U is None and "W_U" not in dict(tied.named_parameters())
    set_seed(7)
    lad2 = LadderTransformer(cfg, p + 1, 3, tie=False)                   # one AdamW step on both: identical
    o1 = torch.optim.AdamW(ref.parameters(), lr=1e-3, weight_decay=1.0, betas=(0.9, 0.98))
    o2 = torch.optim.AdamW(lad2.parameters(), lr=1e-3, weight_decay=1.0, betas=(0.9, 0.98))
    for m, o, lf in ((ref, o1, lambda: F.cross_entropy(ref.logits_last(x)[:, :p], t[:, -1])),
                     (lad2, o2, lambda: loss_fn(lad2(x), t, [2], p, False))):
        o.zero_grad()
        lf().backward()
        o.step()
    assert torch.equal(ref.W_E, lad2.W_E) and torch.equal(ref.W_U, lad2.W_U)
    g = batches(10, 4, 1)
    seen = torch.cat([next(g) for _ in range(3)])
    assert sorted(seen.tolist()) == list(range(10))                     # one epoch = 4 + 4 + 2
    g1, g2 = batches(10, 4, 1), batches(10, 4, 1)
    assert all(torch.equal(next(g1), next(g2)) for _ in range(6))
    print("selftest ok")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--split-file")
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--op-token", action="store_true")
    ap.add_argument("--full-softmax", action="store_true")
    ap.add_argument("--tie", action="store_true")
    ap.add_argument("--loss", choices=("answer", "all", "all_but_b"), default="answer")
    ap.add_argument("--batch-size", type=int, default=0)
    ap.add_argument("--out-root", default=str(HERE / "raw"))
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.seed is None or a.split_file is None:
        ap.error("--seed and --split-file are required for a run")
    else:
        run(a)


if __name__ == "__main__":
    main()
