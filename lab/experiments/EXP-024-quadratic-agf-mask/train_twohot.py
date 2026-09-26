"""EXP-024: train a two-hot MLP (quadratic or ReLU activation) on an EXP-016 engineered split.

f(a,b) = W_out^T act(W_in[a] + W_in[p+b]), no biases (Codex review: a bias adds a frequency-k term to the
quadratic feature), cross-entropy, full batch, AdamW. Records at fixed steps the output-weighted input spectrum
S(k) (rescaling-invariant, see spectra()),
the unweighted spectrum and the W_out spectrum over c, plus train/test accuracy (test = complement of the split).
Definition and pre-registered prediction: README.md. Run only through guarded_run.py.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
S16 = HERE.parents[0] / "EXP-016-engineered-split" / "splits"
P, K, D = 113, 56, 512
SNAP = (0, 1, 50, 250, 1000, 2000, 3000, 5000)


def _fold(pw: np.ndarray) -> np.ndarray:
    return pw[1:K + 1] + pw[P - K:][::-1]


def spectra(W: torch.Tensor, Wo: torch.Tensor, act: str) -> dict:
    """Primary: per-neuron normalised input power weighted by the neuron's output scale, invariant under the
    rescaling symmetry (quad: u -> s u, w -> w / s^2; relu: w -> w / s):
    S(k) = sum_n ||w_n|| ||(u_n, v_n)||^h * frac_n(k), h = 2 (quad) / 1 (relu), frac_n = normalised power of neuron n."""
    u, v = W[:P].detach().numpy(), W[P:].detach().numpy()          # [p, d] each
    per = np.abs(np.fft.fft(u, axis=0)) ** 2 + np.abs(np.fft.fft(v, axis=0)) ** 2   # [p, d]
    tot = per.sum(axis=0)                                            # = p * ||(u_n, v_n)||^2
    h = 2 if act == "quad" else 1
    scale = np.linalg.norm(Wo.detach().numpy(), axis=1) * (tot / P) ** (h / 2)
    frac = per / np.maximum(tot, 1e-30)
    out_pw = (np.abs(np.fft.fft(Wo.detach().numpy(), axis=1)) ** 2).sum(axis=0)       # W_out over c
    return {"weighted": _fold((frac * scale).sum(axis=1)).tolist(), "raw": _fold(per.sum(axis=1)).tolist(),
            "out": _fold(out_pw).tolist()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--arm", choices=("F", "G"), default="F")
    ap.add_argument("--act", choices=("quad", "relu"), required=True)
    ap.add_argument("--steps", type=int, default=5000)
    ap.add_argument("--init-scale", type=float, default=0.1)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--wd", type=float, default=1.0)
    ap.add_argument("--init-seed", type=int, default=None, help="default: --seed")
    ap.add_argument("--out", default=str(HERE / "raw"))
    ap.add_argument("--split-dir", default=str(S16))
    a = ap.parse_args()
    suf = "" if a.arm == "F" else "_G"
    sd = Path(a.split_dir)
    idx = np.load(sd / f"split_seed{a.seed}_eps2.0{suf}.npy")
    meta = json.loads((sd / f"split_seed{a.seed}_eps2.0{suf}.json").read_text())
    test = np.setdiff1d(np.arange(P * P), idx)
    tr_a, tr_b = torch.tensor(idx // P), torch.tensor(idx % P)
    te_a, te_b = torch.tensor(test // P), torch.tensor(test % P)
    tr_y, te_y = (tr_a + tr_b) % P, (te_a + te_b) % P

    torch.manual_seed(a.seed if a.init_seed is None else a.init_seed)
    torch.set_num_threads(4)
    W_in = torch.nn.Parameter(torch.randn(2 * P, D) * a.init_scale / np.sqrt(2 * P))
    W_out = torch.nn.Parameter(torch.randn(D, P) * a.init_scale / np.sqrt(D))
    params = [W_in, W_out]
    opt = torch.optim.AdamW(params, lr=a.lr, weight_decay=a.wd, betas=(0.9, 0.98))
    act = (lambda x: x * x) if a.act == "quad" else torch.relu

    def fwd(xa, xb):
        return act(W_in[xa] + W_in[P + xb]) @ W_out

    run_id = f"EXP-024_{a.act}_seed{a.seed}_{a.arm}" + ("" if a.init_seed is None else f"_init{a.init_seed}")
    out_dir = Path(a.out) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    snaps, curve, t0, gen, steps_done, finite = {}, [], time.time(), None, 0, True
    for step in range(a.steps + 1):
        if step in SNAP:
            snaps[step] = spectra(W_in, W_out, a.act)
        if step % 50 == 0:
            with torch.no_grad():
                tr_acc = (fwd(tr_a, tr_b).argmax(1) == tr_y).float().mean().item()
                te_acc = (fwd(te_a, te_b).argmax(1) == te_y).float().mean().item()
            curve.append([step, tr_acc, te_acc])
            if gen is None and te_acc >= 0.95:
                gen = step
            if not (torch.isfinite(W_in).all() and torch.isfinite(W_out).all()):
                finite = False
                break
        if step == a.steps:
            break
        loss = torch.nn.functional.cross_entropy(fwd(tr_a, tr_b), tr_y)
        opt.zero_grad()
        loss.backward()
        opt.step()
        steps_done = step + 1
    complete = finite and steps_done == a.steps and a.steps in snaps
    last = snaps[max(snaps)]
    top5 = sorted(int(k) for k in np.argsort(-np.array(last["weighted"]))[:5] + 1)
    top5_raw = sorted(int(k) for k in np.argsort(-np.array(last["raw"]))[:5] + 1)
    top5_out = sorted(int(k) for k in np.argsort(-np.array(last["out"]))[:5] + 1)
    res = {"run_id": run_id, "args": vars(a), "targets": meta["targets"], "n_train": int(len(idx)),
           "gen_step_test95": gen, "final_train_acc": curve[-1][1], "final_test_acc": curve[-1][2],
           "final_top5": top5, "final_top5_raw": top5_raw, "final_top5_out": top5_out, "complete": complete,
           "steps_done": steps_done, "curve": curve, "spectra": snaps, "elapsed_s": time.time() - t0,
           "torch": torch.__version__}
    (out_dir / "result.json").write_text(json.dumps(res), encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("run_id", "gen_step_test95", "final_train_acc", "final_test_acc",
                                           "final_top5", "final_top5_raw", "final_top5_out", "targets",
                                           "complete", "elapsed_s")}))


if __name__ == "__main__":
    main()
