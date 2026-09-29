#!/usr/bin/env python3
"""Minimal trainer for the reproduction package (rule 19c). Session 25, UNTESTED (equivalence check in the run window).

The study's 1-layer transformer (preset arch25k: AdamW lr 1e-3, weight decay 1, full batch) on a op b mod p with an explicit train split,
optionally a one-time change of the train set at --switch-step and a reset of one parameter group to its init at that switch. It is the
standard path of lab/experiments/EXP-001-freq-ban/freq_ban.py without the lab's intervention options, bookkeeping and locking, and
is meant to compute the SAME numbers: same operation order (threads, seed, dataset, model init on the CPU, .to(device), AdamW), same
loss, same switch/reset semantics (after the optimizer update of step S the new train set is used; the reset part gets its init weights
back and loses its AdamW state). Session 49: --batch-size B trains on i.i.d. minibatches exactly as freq_ban --batch-size B (L0).

Outputs in --out: result.json (config, versions, accuracies, generalisation step), spectra.npy / spectra_steps.npy (W_E power per
frequency k = 1..(p-1)/2 every --spectra-every steps and at the last step), optionally model_final.pt.
--compare-to DIR compares the spectra with a stored freq_ban run directory at all common steps (equivalence check; exit 1 on a
relative deviation above --tol).

  python lab/tools/guarded_run.py -- python lab/paper/repro/train.py --seed 1000 --split-file S.npy --steps 2000 --out OUT
"""
from __future__ import annotations

import argparse
import hashlib
import io
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

from grokverse.config import THRESHOLD_SETS, get_config  # noqa: E402
from grokverse.data import make_dataset  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.seed import set_seed  # noqa: E402

ORDER_SALT = 100_043                  # s49 (L0 repro): same minibatch-order stream as freq_ban.py, independent of init and splits
RESET_PARTS = {"attn": ("W_Q", "W_K", "W_V", "W_O"), "mlp": ("W_in", "W_out"), "unembed": ("W_U",),
               "qk": ("W_Q", "W_K"), "vo": ("W_V", "W_O"), "we": ("W_E",)}


def fourier_basis(p: int) -> np.ndarray:
    """Orthonormal real DFT basis over Z_p, columns [const, cos_1, sin_1, ..., cos_K, sin_K], K = (p-1)//2 (p odd)."""
    if p % 2 == 0:
        raise ValueError("fourier_basis assumes odd p (no Nyquist column)")
    a = np.arange(p)
    cols = [np.ones(p) / np.sqrt(p)]
    for k in range(1, (p - 1) // 2 + 1):
        cols += [np.cos(2 * np.pi * k * a / p) * np.sqrt(2 / p), np.sin(2 * np.pi * k * a / p) * np.sqrt(2 / p)]
    return np.stack(cols, axis=1)


def freq_power(W: np.ndarray, basis: np.ndarray) -> np.ndarray:
    """Power of W [p, d] per frequency k = 1..(p-1)//2 (index k-1)."""
    sq = ((basis.T @ W) ** 2).sum(axis=1)
    return sq[1::2] + sq[2::2]


INPUT_SHA256: dict[str, str] = {}                  # s33 (Codex R7): sha256 of the exact bytes each index file was loaded from


def load_idx(path: str, p: int, n: int | None) -> torch.Tensor:
    data = Path(path).read_bytes()
    INPUT_SHA256[path] = hashlib.sha256(data).hexdigest()
    raw = np.load(io.BytesIO(data))
    if (raw.ndim != 1 or not np.issubdtype(raw.dtype, np.integer) or (n is not None and len(raw) != n)
            or len(np.unique(raw)) != len(raw) or raw.min() < 0 or raw.max() >= p * p):
        raise SystemExit(f"invalid index file {path}: need {n or 'some'} unique ints in [0, {p * p})")
    return torch.from_numpy(raw.astype(np.int64))


@torch.no_grad()
def accuracy(model: torch.nn.Module, x: torch.Tensor, y: torch.Tensor, p: int) -> float:
    return (model.logits_last(x)[:, :p].argmax(-1) == y).float().mean().item()


def train(a: argparse.Namespace) -> dict:
    cfg = get_config("arch25k", seed=a.seed, steps=a.steps, threads=a.threads, p=a.p, task=a.task)
    p = cfg.p
    if (a.switch_split_file is None) != (a.switch_step is None) or (a.reset_at_switch and a.switch_step is None):
        raise SystemExit("--switch-split-file and --switch-step go together; --reset-at-switch needs a switch")
    if a.reset_optim_part and (a.switch_step is None or a.reset_at_switch):   # s27: as freq_ban --reset-optim-part m (EXP-058/N28)
        raise SystemExit("--reset-optim-part needs a switch and excludes --reset-at-switch")
    if a.switch_split_file and not a.test_file:           # as freq_ban: a switch needs an explicit shared test set
        raise SystemExit("--switch-split-file needs --test-file")
    mbs = a.batch_size
    if mbs < 0 or (mbs and a.switch_step is not None):   # s49: L0 needs only i.i.d. minibatches without a switch
        raise SystemExit("--batch-size must be >= 0 and excludes a switch in this lean trainer")
    torch.set_num_threads(cfg.threads)
    set_seed(cfg.seed)
    data = make_dataset(cfg)                           # own torch.Generator: does not touch the global RNG (model init unchanged)
    tr = load_idx(a.split_file, p, int(round(cfg.train_frac * p * p)))
    te = (torch.from_numpy(np.sort(load_idx(a.test_file, p, None).numpy())) if a.test_file else torch.from_numpy(np.setdiff1d(np.arange(p * p), tr.numpy())))
    if np.intersect1d(te.numpy(), tr.numpy()).size:
        raise SystemExit("test set overlaps the train set")
    sw = load_idx(a.switch_split_file, p, len(tr)) if a.switch_split_file else None
    if sw is not None and np.intersect1d(sw.numpy(), te.numpy()).size:
        raise SystemExit("switch set overlaps the test set")
    X, Y = data["all_x"], data["all_y"]
    model = build_model(cfg)
    dev = torch.device(a.device)
    model = model.to(dev)
    trx, try_, tex, tey = X[tr].to(dev), Y[tr].to(dev), X[te].to(dev), Y[te].to(dev)
    init = {nm: q.detach().clone() for nm, q in model.named_parameters()}
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay, betas=(cfg.beta1, cfg.beta2))
    basis = fourier_basis(p)
    spectra, spectra_steps, test_curve = [], [], []
    gen_thr, gen_step = THRESHOLD_SETS["primary"][1], None

    def spectrum(step: int) -> None:
        spectra_steps.append(step)
        spectra.append(freq_power(model.W_E.detach().cpu().numpy().astype(np.float64)[:p], basis))

    t0 = time.perf_counter()
    spectrum(0)
    mb_rng = np.random.default_rng(np.random.SeedSequence([ORDER_SALT, a.seed]))
    mb_order, mb_pos = None, 0
    for step in range(1, a.steps + 1):
        model.train()
        if mbs:                                        # as freq_ban --batch-size (order iid): a new permutation per epoch
            if mb_order is None or mb_pos >= len(trx):
                mb_order, mb_pos = torch.from_numpy(mb_rng.permutation(len(trx)).astype(np.int64)).to(trx.device), 0
            bi = mb_order[mb_pos:mb_pos + mbs]
            mb_pos += mbs
            loss = F.cross_entropy(model.logits_last(trx[bi])[:, :p], try_[bi])
        else:
            loss = F.cross_entropy(model.logits_last(trx)[:, :p], try_)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        if sw is not None and step == a.switch_step:  # new train set from the next step on; optional reset of one part
            trx, try_ = X[sw].to(dev), Y[sw].to(dev)
            if a.reset_at_switch:
                done = []
                with torch.no_grad():
                    for nm, q in model.named_parameters():
                        if nm in RESET_PARTS[a.reset_at_switch]:
                            q.copy_(init[nm])
                            opt.state.pop(q, None)
                            done.append(nm)
                if sorted(done) != sorted(RESET_PARTS[a.reset_at_switch]):   # s27 review: no silent no-op reset (as freq_ban)
                    raise SystemExit(f"reset part {a.reset_at_switch}: parameters not found ({done})")
            if a.reset_optim_part == "m":             # s27: zero exp_avg only; exp_avg_sq and the step counters (bias correction) kept
                for q in model.parameters():
                    opt.state[q]["exp_avg"].zero_()
        if step % cfg.eval_every_test == 0:
            acc = accuracy(model, tex, tey, p)
            test_curve.append([step, acc])
            if gen_step is None and acc >= gen_thr:
                gen_step = step
        if step % a.spectra_every == 0:
            spectrum(step)
    if a.steps % a.spectra_every:
        spectrum(a.steps)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "spectra.npy", np.asarray(spectra))
    np.save(out / "spectra_steps.npy", np.asarray(spectra_steps))
    if a.save_model:
        torch.save(model.state_dict(), out / "model_final.pt")
    res = {"trainer": "lab/paper/repro/train.py", "argv": sys.argv, "seed": a.seed, "device": a.device, "config": cfg.to_dict(),
           "steps": a.steps, "switch_step": a.switch_step, "reset_at_switch": a.reset_at_switch,
           "reset_optim_part": a.reset_optim_part, "batch_size": mbs,
           "final_acc": {"train": accuracy(model, trx, try_, p), "test": accuracy(model, tex, tey, p)},
           "generalization_step": gen_step, "test_curve": test_curve, "sec_per_step": round((time.perf_counter() - t0) / a.steps, 5),
           "versions": {"python": platform.python_version(), "torch": torch.__version__, "numpy": np.__version__},
           "platform": platform.platform(), "end_utc": datetime.now(timezone.utc).isoformat(),
           "input_sha256": dict(INPUT_SHA256), "status": "completed"}                     # s33: bound_block binds only runs marked completed (R7)
    (out / "result.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    return res


def compare(out: Path, ref: Path, tol: float) -> bool:
    """Spectra of this run against a stored freq_ban run at every common step; prints the largest relative deviation."""
    s, st = np.load(out / "spectra.npy"), np.load(out / "spectra_steps.npy").tolist()
    r, rt = np.load(ref / "spectra.npy"), np.load(ref / "spectra_steps.npy").tolist()
    common = sorted(set(st) & set(rt))
    if not common:
        print("[repro] no common spectrum steps", flush=True)
        return False
    dev = max(float(np.max(np.abs(s[st.index(t)] - r[rt.index(t)]) / np.maximum(np.abs(r[rt.index(t)]), 1e-12))) for t in common)
    exact = all(np.array_equal(s[st.index(t)], r[rt.index(t)]) for t in common)
    print(f"[repro] compared {len(common)} steps ({common[0]}..{common[-1]}): max relative deviation {dev:.3e}, bit-identical {exact}",
          flush=True)
    return dev <= tol


def main() -> None:
    ap = argparse.ArgumentParser(description="minimal reproduction trainer (arch25k, full batch)")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--split-file", required=True)
    ap.add_argument("--test-file")
    ap.add_argument("--switch-split-file")
    ap.add_argument("--switch-step", type=int)
    ap.add_argument("--reset-at-switch", choices=tuple(RESET_PARTS))
    ap.add_argument("--reset-optim-part", choices=("m",), help="zero Adam's first moment at the switch (N28 arm m)")
    ap.add_argument("--batch-size", type=int, default=0, help="i.i.d. minibatch size as freq_ban (0 = full batch, unchanged)")
    ap.add_argument("--task", default="add", choices=("add", "mul"))
    ap.add_argument("--p", type=int, default=113)
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--spectra-every", type=int, default=250)
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--save-model", action="store_true")
    ap.add_argument("--out", required=True)
    ap.add_argument("--compare-to")
    ap.add_argument("--tol", type=float, default=1e-6)
    a = ap.parse_args()
    res = train(a)
    print(f"[repro] seed {a.seed}: test acc {res['final_acc']['test']:.3f}, gen {res['generalization_step']}, "
          f"{res['sec_per_step']} s/step", flush=True)
    if a.compare_to and not compare(Path(a.out), Path(a.compare_to), a.tol):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
