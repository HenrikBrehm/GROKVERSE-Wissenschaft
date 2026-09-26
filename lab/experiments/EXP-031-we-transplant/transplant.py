"""EXP-031: is the early W_E imprint causal? Continue a study run B from its step-500 checkpoint on B's own split, with
W_E replaced by the step-500 W_E of study run A (arm 'transplant') or kept (arm 'control'). Both arms start a FRESH AdamW
(the checkpoints hold weights only), so the control isolates the optimizer reset. Trains --steps more steps (default
2500, i.e. up to step 3000), stores W_E power spectra every 250 steps, final top-5, train/test accuracy.
Definition and pre-registered prediction: README.md. Run only through guarded_run.py.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "training"))
sys.path.insert(0, str(HERE.parent / "EXP-001-freq-ban"))

from grokverse.config import get_config  # noqa: E402
from grokverse.data import make_dataset, split_hash  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.train import evaluate  # noqa: E402
import freq_ban as fb  # noqa: E402

RUNS = ROOT / "training" / "runs"
START = 500


def ckpt(seed: int) -> dict:
    return torch.load(RUNS / f"txf_add_p113_wd1.0_frac0.3_seed{seed}_arch25k" / f"ckpt_step{START:06d}.pt",
                      map_location="cpu", weights_only=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-b", type=int, required=True, help="run whose weights, split and data are continued")
    ap.add_argument("--seed-a", type=int, default=None, help="donor of W_E (arm transplant); omit for the control")
    ap.add_argument("--steps", type=int, default=2500)
    ap.add_argument("--out", default=str(HERE / "raw"))
    a = ap.parse_args()
    arm = "control" if a.seed_a is None else "transplant"
    run_id = f"EXP-031_{arm}_B{a.seed_b}" + ("" if a.seed_a is None else f"_A{a.seed_a}")
    out = Path(a.out) / run_id
    out.mkdir(parents=True, exist_ok=True)

    cfg = get_config("arch25k", seed=a.seed_b, steps=START + a.steps, threads=4)
    torch.set_num_threads(cfg.threads)
    torch.manual_seed(31_000 + a.seed_b)            # no RNG is consumed below; fixed for completeness
    data = make_dataset(cfg)
    model = build_model(cfg)
    state = ckpt(a.seed_b)
    missing = model.load_state_dict(state, strict=True)
    p = cfg.p
    basis = fb.fourier_basis(p)
    pw_b = fb.freq_power(model.W_E.detach().numpy().astype(np.float64)[:p], basis)
    if a.seed_a is not None:
        with torch.no_grad():
            model.W_E.copy_(ckpt(a.seed_a)["W_E"])  # whole embedding incl. the '=' row
    trx, try_, tex, tey = data["train_x"], data["train_y"], data["test_x"], data["test_y"]
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay, betas=(cfg.beta1, cfg.beta2))
    acc0 = {"train": evaluate(model, trx, try_, p)[1], "test": evaluate(model, tex, tey, p)[1]}
    spectra, steps_logged, curve, t0 = [], [], [], time.time()
    finite = True
    for step in range(0, a.steps + 1):
        if step % 250 == 0:
            spectra.append(fb.freq_power(model.W_E.detach().numpy().astype(np.float64)[:p], basis).tolist())
            steps_logged.append(START + step)
        if step % 100 == 0:
            curve.append([START + step, evaluate(model, trx, try_, p)[1], evaluate(model, tex, tey, p)[1]])
            if not all(torch.isfinite(x).all() for x in model.parameters()):
                finite = False
                break
        if step == a.steps:
            break
        model.train()
        loss = F.cross_entropy(model.logits_last(trx)[:, :p], try_)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
    final = np.array(spectra[-1])
    res = {"run_id": run_id, "arm": arm, "args": vars(a), "start_step": START, "complete": finite and step == a.steps,
           "split_hash": split_hash(data["train_idx"]), "load": str(missing), "acc_after_transplant": acc0,
           "top5_B_at_500": fb.top_frequencies(pw_b, 5), "final_top5": fb.top_frequencies(final, 5),
           "spectra": spectra, "spectra_steps": steps_logged, "curve": curve, "elapsed_s": time.time() - t0,
           "torch": torch.__version__}
    if a.seed_a is not None:
        res["top5_A_at_500"] = fb.top_frequencies(fb.freq_power(ckpt(a.seed_a)["W_E"].numpy().astype(np.float64)[:p],
                                                                basis), 5)
    (out / "result.json").write_text(json.dumps(res), encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("run_id", "complete", "acc_after_transplant", "top5_B_at_500",
                                          "final_top5", "elapsed_s")} | {"final_acc": curve[-1]}))
    if not res["complete"]:
        sys.exit(4)


if __name__ == "__main__":
    main()
