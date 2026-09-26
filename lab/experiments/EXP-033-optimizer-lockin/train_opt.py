"""EXP-033: is the early lock-in of EXP-032 an AdamW artifact?

Two-hot MLP as EXP-026/train_sigma.py (same init, split, loss, spectra). Phase 1 trains with sigma_3 = 3x + x^2 using
--opt1 (adamw: EXP-032 phase 1; gd: plain full-batch gradient descent, no momentum, no weight decay) until either
--switch-step steps (adamw) or the median feature amplitude r reaches --switch-r (gd). Phase 2 trains the pure x^2 net
with a FRESH AdamW (same hyperparameters as EXP-026) for --after-steps steps. Only phase 1 differs between arms.
--phase1-only stops after phase 1 (lr smoke for gd; outcome is not computed). Definition: README.md.
Run only through guarded_run.py.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
E26 = HERE.parents[0] / "EXP-026-parity-crossover"
sys.path.insert(0, str(E26))
from train_sigma import D, P, S16, spectra  # noqa: E402

SNAP2 = (0, 250, 1000, 2000, 3000, 5000)   # phase-2 steps (relative to the switch)


def amp_median(W_in: torch.Tensor) -> float:
    """Median over neurons of r_n = sqrt(mean_a(u_n^2 + v_n^2)), identical to spectra()['amp']['median']."""
    with torch.no_grad():
        return float(torch.sqrt((W_in[:P] ** 2 + W_in[P:] ** 2).mean(0)).median())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--opt1", choices=("adamw", "gd"), required=True)
    ap.add_argument("--switch-step", type=int, default=None, help="adamw: phase-1 length in steps")
    ap.add_argument("--switch-r", type=float, default=None, help="gd: switch when median r >= this")
    ap.add_argument("--gd-lr", type=float, default=1.0)
    ap.add_argument("--max-phase1", type=int, default=20000)
    ap.add_argument("--after-steps", type=int, default=5000)
    ap.add_argument("--phase1-only", action="store_true")
    ap.add_argument("--tag", default="")
    ap.add_argument("--out", default=str(HERE / "raw"))
    a = ap.parse_args()
    if (a.opt1 == "adamw") != (a.switch_step is not None) or (a.opt1 == "gd") != (a.switch_r is not None):
        ap.error("adamw needs --switch-step, gd needs --switch-r (and not the other)")

    idx = np.load(S16 / f"split_seed{a.seed}_eps2.0.npy")
    meta = json.loads((S16 / f"split_seed{a.seed}_eps2.0.json").read_text())
    test = np.setdiff1d(np.arange(P * P), idx)
    tr_a, tr_b = torch.tensor(idx // P), torch.tensor(idx % P)
    te_a, te_b = torch.tensor(test // P), torch.tensor(test % P)
    tr_y, te_y = (tr_a + tr_b) % P, (te_a + te_b) % P

    torch.manual_seed(a.seed)                     # identical init to EXP-026/032 (same calls, same order)
    torch.set_num_threads(4)
    W_in = torch.nn.Parameter(torch.randn(2 * P, D) * 0.1 / np.sqrt(2 * P))
    W_out = torch.nn.Parameter(torch.randn(D, P) * 0.1 / np.sqrt(D))
    params = [W_in, W_out]
    cur = {"alpha": 3.0}

    def fwd(xa, xb):
        h = W_in[xa] + W_in[P + xb]
        return (cur["alpha"] * h + h * h) @ W_out

    def accs():
        with torch.no_grad():
            return ((fwd(tr_a, tr_b).argmax(1) == tr_y).float().mean().item(),
                    (fwd(te_a, te_b).argmax(1) == te_y).float().mean().item())

    lvl = f"t{a.switch_step}" if a.opt1 == "adamw" else f"r{a.switch_r:g}_lr{a.gd_lr:g}"
    run_id = f"EXP-033_{a.opt1}_{lvl}_seed{a.seed}" + (f"_{a.tag}" if a.tag else "") + ("_p1" if a.phase1_only else "")
    out_dir = Path(a.out) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    snaps = {"p1_0": spectra(W_in, W_out, "sig")}
    r_trace, finite = [], True

    # phase 1
    opt1 = (torch.optim.AdamW(params, lr=1e-3, weight_decay=1.0, betas=(0.9, 0.98)) if a.opt1 == "adamw"
            else torch.optim.SGD(params, lr=a.gd_lr, momentum=0.0, weight_decay=0.0))
    n1, reached = 0, False
    while n1 < a.max_phase1:
        if a.opt1 == "adamw" and n1 == a.switch_step:
            reached = True
            break
        if a.opt1 == "gd":
            r = amp_median(W_in)
            if n1 % 10 == 0:
                r_trace.append([n1, r])
            if r >= a.switch_r:
                reached = True
                break
        loss = torch.nn.functional.cross_entropy(fwd(tr_a, tr_b), tr_y)
        opt1.zero_grad()
        loss.backward()
        opt1.step()
        n1 += 1
        if not (torch.isfinite(W_in).all() and torch.isfinite(W_out).all()):
            finite = False
            break
    snaps["switch"] = spectra(W_in, W_out, "sig")
    wout_norm_switch = float(W_out.detach().norm())
    r_switch = amp_median(W_in) if finite else None
    acc_switch = accs()

    # phase 2: pure x^2, fresh AdamW
    curve, gen, n2 = [], None, 0
    if reached and finite and not a.phase1_only:
        cur["alpha"] = 0.0
        opt2 = torch.optim.AdamW(params, lr=1e-3, weight_decay=1.0, betas=(0.9, 0.98))
        for step in range(a.after_steps + 1):
            if step in SNAP2:
                snaps[f"p2_{step}"] = spectra(W_in, W_out, "sig")
            if step % 50 == 0:
                tr, te = accs()
                curve.append([step, tr, te])
                if gen is None and te >= 0.95:
                    gen = step
                if not (torch.isfinite(W_in).all() and torch.isfinite(W_out).all()):
                    finite = False
                    break
            if step == a.after_steps:
                break
            loss = torch.nn.functional.cross_entropy(fwd(tr_a, tr_b), tr_y)
            opt2.zero_grad()
            loss.backward()
            opt2.step()
            n2 = step + 1
    complete = reached and finite and (a.phase1_only or (n2 == a.after_steps and f"p2_{a.after_steps}" in snaps))
    res = {"run_id": run_id, "args": vars(a), "targets": meta["targets"], "n_train": int(len(idx)),
           "phase1_steps": n1, "reached": reached, "finite": finite, "complete": complete,
           "r_switch": r_switch, "wout_norm_switch": wout_norm_switch,
           "acc_switch": acc_switch, "r_trace": r_trace, "gen_step_test95": gen,
           "final_test_acc": curve[-1][2] if curve else None, "final_train_acc": curve[-1][1] if curve else None,
           "curve": curve, "spectra": snaps, "elapsed_s": time.time() - t0, "torch": torch.__version__}
    tmp = out_dir / "result.json.tmp"
    tmp.write_text(json.dumps(res), encoding="utf-8")
    tmp.replace(out_dir / "result.json")
    print(json.dumps({k: res[k] for k in ("run_id", "phase1_steps", "reached", "r_switch", "acc_switch",
                                           "gen_step_test95", "final_test_acc", "complete", "elapsed_s")}))
    if not complete:
        sys.exit(4)


if __name__ == "__main__":
    main()
