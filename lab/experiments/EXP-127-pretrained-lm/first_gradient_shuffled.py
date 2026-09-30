"""Order-corrected first-gradient test (session 59, written before computing anything here). first_gradient.py (S58, Pythia) and
first_gradient_scratch.py (S59, LM1 random init) fed the facts in the STORED order of the split files, which is SORTED (a*113 + b):
every sequence of K = 16 facts then holds one value of a with consecutive b, so numbers close in value share contexts. Training
never sees that order (both trainers draw a permutation per round). Here the facts are fed in the order of the FIRST TRAINING ROUND:
  pythia : permutation of numpy SeedSequence([127, seed, 1]) as ft_pythia.Stream (seed = split seed 4000/4001), operator " @"
  scratch: permutation of numpy SeedSequence([105, model_seed, 2]) as lm_stage2.Stream (model seed = split seed + 100), template T0
Everything else as in the two earlier scripts (answer loss only, K = 16, loss sum / number of facts, gradient of the number-token rows;
scratch: output layer as a second copy of the tied matrix). F and G of a seed use the same permutation of positions.
Reading per model (fixed before running): 'gestuetzt' if Delta_pow(grad, in) > 1 in both seeds; 'nicht gestuetzt' if <= 0 in both;
else 'unklar'. Interpretation (fixed before running): Pythia 'gestuetzt' -> the S58 'nicht gestuetzt' was an order artefact and the
first-order account holds even at pretrained weights; Pythia 'nicht gestuetzt' with scratch 'gestuetzt' -> pretraining blocks it;
both 'nicht gestuetzt' -> the account does not carry over to these LMs. Descriptive: output side, tied sum (scratch), top-5.
  python lab/tools/guarded_run.py -- <abs>/.venv-gpu/Scripts/python.exe lab/experiments/EXP-127-pretrained-lm/first_gradient_shuffled.py --model pythia --device cuda
Session 59 addition (after the K = 16 results, before any K = 1 run): --k sets the facts per sequence (default 16 = results above,
unchanged). Question: does the multi-fact context (attention at init mixes all earlier facts) dilute the first-order signal? Reading
for --k 1 as above; interpretation (fixed before running): scratch K = 1 'gestuetzt' -> context mixing hides the first-order signal
in the LM; 'nicht gestuetzt' -> the LM architecture itself (depth, LayerNorm, init) breaks the account. Output file gets suffix _k1.
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
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "lab/experiments/EXP-105-lm-ladder-stage2"))
import analyze as A  # noqa: E402

SPL = ROOT / "lab/confirm/lm1_splits"
P = 113


def sequences(facts: np.ndarray, num: list[int], op: int, eq: int, sep: int, eot: int, k: int = 16) -> list[tuple[list, list]]:
    rows = []
    for i in range(-(-len(facts) // k)):
        row, lab = [eot], [-100]
        for f in facts[i * k:(i + 1) * k]:
            a, b = divmod(int(f), P)
            c = (a + b) % P
            row += [num[a], op, num[b], eq, num[c], sep]
            lab += [-100, -100, -100, num[c], -100, -100]        # label at the eq position = next token c
        rows.append((row, lab))
    return rows


K = 16


def run_grads(rows, logits_fn, n_facts: int, dev, bs: int = 16) -> None:
    for j in range(0, len(rows), bs):
        part = rows[j:j + bs]
        L = max(len(r) for r, _ in part)
        x = torch.tensor([r + [r[-1]] * (L - len(r)) for r, _ in part], device=dev)
        y = torch.tensor([lb + [-100] * (L - len(lb)) for _, lb in part], device=dev)
        loss = F.cross_entropy(logits_fn(x).flatten(0, 1), y.flatten(), ignore_index=-100, reduction="sum") / n_facts
        loss.backward()


def pythia(dev: str):
    import ft_pythia as T
    tok, model = T.load_model(dev)
    ids = T.token_ids(tok)
    num_t = torch.tensor(ids["num"], device=dev)
    W = model.get_output_embeddings()

    def arm(seed: int, facts: np.ndarray):
        perm = np.random.default_rng(np.random.SeedSequence([127, seed, 1])).permutation(len(facts))
        model.zero_grad(set_to_none=True)
        rows = sequences(facts[perm], ids["num"], ids["op"], ids["eq"], ids["nl"], ids["eot"], K)
        run_grads(rows, lambda x: W(model.gpt_neox(x).last_hidden_state), len(facts), dev)
        gi = model.get_input_embeddings().weight.grad[num_t].double().cpu().numpy()
        go = W.weight.grad[num_t].double().cpu().numpy()
        return gi, go, perm
    return arm, ("in", "out")


def scratch(dev: str):
    import lm_stage2 as L
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(L.TOK_FILE))
    ids = L.special_ids(tok)
    nl, vocab = tok.token_to_id("Ċ"), tok.get_vocab_size()
    num_t = torch.tensor(ids["num"], device=dev)

    def arm(seed: int, facts: np.ndarray):
        ms = seed + 100
        g_init = np.random.default_rng(np.random.SeedSequence([105, ms, 4]))
        torch.manual_seed(int(g_init.integers(2**62)))
        m = L.GPT(vocab, 256, 384, 6, 6).to(dev)
        w_out = torch.nn.Parameter(m.emb.weight.detach().clone())

        def logits(x):
            h = m.emb(x) + m.pos(torch.arange(x.shape[1], device=dev))
            for b in m.blocks:
                h = b(h)
            return m.ln(h) @ w_out.T
        perm = np.random.default_rng(np.random.SeedSequence([105, ms, 2])).permutation(len(facts))
        rows = sequences(facts[perm], ids["num"], ids["plus"], ids["eq"], nl, ids["eot"], K)
        run_grads(rows, logits, len(facts), dev)
        gi = m.emb.weight.grad[num_t].double().cpu().numpy()
        go = w_out.grad[num_t].double().cpu().numpy()
        return gi, go, perm
    return arm, ("in", "out", "tied")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=("pythia", "scratch"), required=True)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--k", type=int, default=16)
    a = ap.parse_args()
    global K
    K = a.k
    torch.set_num_threads(a.threads)
    t0 = time.time()
    arm, sides = (pythia if a.model == "pythia" else scratch)(a.device)
    out = {"model": a.model, "device": a.device, "order": "first training round", "k": K, "rows": []}
    for s in (4000, 4001):
        tg = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        g = {x: arm(s, np.load(SPL / f"seed{s}_{x}.npy").astype(np.int64)) for x in "FG"}
        assert (g["F"][2] == g["G"][2]).all()
        r = {"seed": s, "targets": tg, "perm_head": g["F"][2][:5].tolist()}
        for side in sides:
            fn = {"in": lambda v: v[0], "out": lambda v: v[1], "tied": lambda v: v[0] + v[1]}[side]
            pF, pG = A.power(fn(g["F"])), A.power(fn(g["G"]))
            r[f"dpow_grad_{side}"] = A.delta_pow(pF, pG, tg["F"], tg["G"])
            r[f"top5_F_{side}"] = (np.argsort(pF)[::-1][:5] + 1).tolist()
            r[f"top5_G_{side}"] = (np.argsort(pG)[::-1][:5] + 1).tolist()
        out["rows"].append(r)
        print(json.dumps(r), f"{time.time() - t0:.0f}s", flush=True)
    d = [r["dpow_grad_in"] for r in out["rows"]]
    out["reading"] = ("gestuetzt" if all(v is not None and v > 1 for v in d) else
                      "nicht gestuetzt" if all(v is not None and v <= 0 for v in d) else "unklar")
    (HERE / f"first_gradient_shuffled_{a.model}{'' if K == 16 else f'_k{K}'}.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(out["reading"])


if __name__ == "__main__":
    main()
