"""Session 59 (written before running). Separates PRETRAINING from ARCHITECTURE for the Pythia result of the first-gradient tests:
pretrained Pythia-160M with one fact per sequence gave Delta_pow(grad, in) -0.13 / -0.01 (first_gradient_shuffled_pythia_k1.json),
while the LM1 random init gave 1.21 / 1.31. Here: the SAME Pythia-160M architecture and tokenizer (config of the pinned revision),
but randomly initialized (transformers default init, torch.manual_seed from numpy SeedSequence([59, seed, 8])), measured exactly as
first_gradient_shuffled.py --model pythia --k 1 (training order of ft_pythia, operator " @", answer loss, number rows of embed_in /
embed_out). GPU.
Reading (fixed before running): 'gestuetzt' if Delta_pow(grad, in) > 1 in both seeds; 'nicht gestuetzt' if <= 0 in both; else 'unklar'.
Interpretation (fixed before running): 'gestuetzt' -> the pretrained weights, not the Pythia architecture, suppress the first-order
signal; 'nicht gestuetzt' -> the architecture (or init) alone already suppresses it, pretraining is not needed to explain the Pythia
result; 'unklar' -> not separated.
  python lab/tools/guarded_run.py -- <abs>/.venv-gpu/Scripts/python.exe lab/experiments/EXP-127-pretrained-lm/first_gradient_pythia_random.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze as A  # noqa: E402
import first_gradient_shuffled as S  # noqa: E402
import ft_pythia as T  # noqa: E402


def main() -> None:
    dev = "cuda"
    from transformers import AutoConfig, AutoTokenizer, GPTNeoXForCausalLM
    tok = AutoTokenizer.from_pretrained(T.REPO, revision=T.REVISION)
    cfg = AutoConfig.from_pretrained(T.REPO, revision=T.REVISION)
    ids = T.token_ids(tok)
    num_t = torch.tensor(ids["num"], device=dev)
    out = {"model": "pythia-160m architecture, random init", "k": 1, "rows": []}
    for s in (4000, 4001):
        tg = json.loads((S.SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        torch.manual_seed(int(np.random.default_rng(np.random.SeedSequence([59, s, 8])).integers(2**62)))
        model = GPTNeoXForCausalLM(cfg).to(dev).float()
        W = model.get_output_embeddings()
        g = {}
        for arm in "FG":
            facts = np.load(S.SPL / f"seed{s}_{arm}.npy").astype(np.int64)
            perm = np.random.default_rng(np.random.SeedSequence([127, s, 1])).permutation(len(facts))
            model.zero_grad(set_to_none=True)
            rows = S.sequences(facts[perm], ids["num"], ids["op"], ids["eq"], ids["nl"], ids["eot"], 1)
            S.run_grads(rows, lambda x: W(model.gpt_neox(x).last_hidden_state), len(facts), dev)
            g[arm] = (model.get_input_embeddings().weight.grad[num_t].double().cpu().numpy(),
                      W.weight.grad[num_t].double().cpu().numpy())
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
    (HERE / "first_gradient_pythia_random.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(out["reading"])


if __name__ == "__main__":
    main()
