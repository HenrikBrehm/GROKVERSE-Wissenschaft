"""EXP-133 first-order prediction (session 62, written before any EXP-133 training run and before running this script).
Gradient of the answer loss over one full first round of the training facts, one fact per sequence (K = 1, training order
of ft_pythia), at the INITIAL weights of EXP-133: pretrained Pythia-160M with the number-row deviations re-initialised
exactly as ft_reset.reset_rows (same seeds -> the same rows the EXP-133 runs start from). Measured as in S59
(first_gradient_pythia_random.py): Delta_pow of the gradient of the number rows of embed_in / embed_out.
Known before: pretrained Pythia K=1: -0.13 / -0.01 (top 5 = 1-5); Pythia architecture random init K=1: 0.84 / 1.04
(top 5 = own targets in all four arms).
Reading (fixed before running): 'gestuetzt' if Delta_pow(grad, in) > 1 in both seeds; 'nicht gestuetzt' if <= 0 in both;
else 'unklar'. Descriptive: top 5 per arm.
Use (fixed before running): a first-order PREDICTION for EXP-133. 'gestuetzt' predicts 'gesteuert (neue Zahlzeilen)'; if the
signal is absent although the rows are random, the pretrained body suppresses it at first order (predicts 'nicht gesteuert').
Whether the prediction is right is read only after EXP-133 has run.
  python lab/tools/guarded_run.py -- <abs>/.venv-gpu/Scripts/python.exe lab/experiments/EXP-133-pythia-reset-numbers/first_gradient_reset.py --device cpu --threads 4 [--limit N]
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
LAB = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(LAB / "experiments/EXP-127-pretrained-lm"))
import ft_reset as R  # noqa: E402  (also puts ft_pythia on the path)
import first_gradient_shuffled as S  # noqa: E402
import ft_pythia as T  # noqa: E402
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp127_analyze", LAB / "experiments/EXP-127-pretrained-lm/analyze.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0, help="timing only: use the first N facts per arm")
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    out = {"model": "pythia-160m pretrained, number-row deviations re-initialised (ft_reset.reset_rows)", "k": 1,
           "limit": a.limit, "rows": []}
    t0 = time.time()
    for s in (4000, 4001):
        tg = json.loads((S.SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        tok, model = R._orig_load(a.device)
        ids = T.token_ids(tok)
        R.reset_rows(model, ids["num"], s)
        num_t = torch.tensor(ids["num"], device=a.device)
        W = model.get_output_embeddings()
        g = {}
        for arm in "FG":
            facts = np.load(S.SPL / f"seed{s}_{arm}.npy").astype(np.int64)
            perm = np.random.default_rng(np.random.SeedSequence([127, s, 1])).permutation(len(facts))
            fx = facts[perm][: a.limit] if a.limit else facts[perm]
            model.zero_grad(set_to_none=True)
            rows = S.sequences(fx, ids["num"], ids["op"], ids["eq"], ids["nl"], ids["eot"], 1)
            S.run_grads(rows, lambda x: W(model.gpt_neox(x).last_hidden_state), len(fx), a.device, bs=128)
            g[arm] = (model.get_input_embeddings().weight.grad[num_t].double().cpu().numpy(),
                      W.weight.grad[num_t].double().cpu().numpy())
            print(f"seed {s} arm {arm}: {len(fx)} facts, {time.time() - t0:.0f}s", flush=True)
        r = {"seed": s, "targets": tg}
        for side, i in (("in", 0), ("out", 1)):
            pF, pG = A.power(g["F"][i]), A.power(g["G"][i])
            r[f"dpow_grad_{side}"] = A.delta_pow(pF, pG, tg["F"], tg["G"])
            r[f"top5_F_{side}"] = (np.argsort(pF)[::-1][:5] + 1).tolist()
            r[f"top5_G_{side}"] = (np.argsort(pG)[::-1][:5] + 1).tolist()
        out["rows"].append(r)
        print(json.dumps(r), flush=True)
    d = [r["dpow_grad_in"] for r in out["rows"]]
    out["reading"] = ("gestuetzt" if all(v is not None and v > 1 for v in d) else
                      "nicht gestuetzt" if all(v is not None and v <= 0 for v in d) else "unklar")
    out["seconds"] = time.time() - t0
    name = "first_gradient_reset.json" if not a.limit else f"first_gradient_reset_limit{a.limit}.json"
    (HERE / name).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(out["reading"])


if __name__ == "__main__":
    main()
