"""Control for first_gradient.py (session 59, written before computing anything here). first_gradient.py found that the first
answer-loss gradient of the number-token INPUT rows of pretrained Pythia-160M does not carry the mask frequencies ('nicht gestuetzt',
Delta_pow -0.01 / -0.04). Question: is that due to PRETRAINING, or does it also hold for the LM architecture at RANDOM init?
Same measurement at the random init of the LM1 model (lm_stage2.GPT, defaults d 384, 6 layers, 6 heads, ctx 256, vocab of the BPE
tokenizer; init stream exactly as lm_stage2.run: SeedSequence([105, model_seed, 4]), model seed = split seed + 100), LM1 splits of
seeds 4000/4001 (same facts as in first_gradient.py), template T0 "<na> <plus> <nb> <eq> <nc>", K = 16 facts per sequence joined by
the newline token, framed by end-of-text, every training fact exactly once in stored order, loss only on the answer tokens c, summed
over all facts / number of facts. The model is tied; to separate the sides, the output layer uses a second copy of the same initial
matrix (tied gradient = in + out, reported descriptively).
Reading (fixed before running): 'gestuetzt' if Delta_pow(grad, in) > 1 in both seeds; 'nicht gestuetzt' if <= 0 in both; else
'unklar'. Descriptive: output side, tied sum, top-5 frequencies. Interpretation (fixed before running): 'gestuetzt' here together with
'nicht gestuetzt' for Pythia -> the pretrained number structure, not the LM architecture, blocks the first-order account; 'nicht
gestuetzt' here too -> the first-order account does not carry over to this LM at all (then pretraining is not the explanation).
CPU, 2 threads (timed on one sequence batch first).
  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-127-pretrained-lm/first_gradient_scratch.py
"""
from __future__ import annotations

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
import lm_stage2 as L  # noqa: E402

SPL = ROOT / "lab/confirm/lm1_splits"


def build(model_seed: int, vocab: int) -> tuple[L.GPT, torch.nn.Parameter]:
    g_init = np.random.default_rng(np.random.SeedSequence([105, model_seed, 4]))
    torch.manual_seed(int(g_init.integers(2**62)))
    m = L.GPT(vocab, 256, 384, 6, 6)
    w_out = torch.nn.Parameter(m.emb.weight.detach().clone())
    return m, w_out


def logits(m: L.GPT, w_out: torch.nn.Parameter, idx: torch.Tensor) -> torch.Tensor:
    x = m.emb(idx) + m.pos(torch.arange(idx.shape[1]))
    for b in m.blocks:
        x = b(x)
    return m.ln(x) @ w_out.T


def grads(m, w_out, ids: dict, nl: int, facts: np.ndarray, k: int = 16, bs: int = 16, limit: int | None = None):
    num = torch.tensor(ids["num"])
    m.zero_grad(set_to_none=True)
    w_out.grad = None
    rows = []
    for i in range(-(-len(facts) // k)):
        row, lab = [ids["eot"]], [-100]
        chunk = facts[i * k:(i + 1) * k]
        for j, f in enumerate(chunk):
            a, b = divmod(int(f), L.P)
            c = (a + b) % L.P
            row += [ids["num"][a], ids["plus"], ids["num"][b], ids["eq"], ids["num"][c], nl if j < len(chunk) - 1 else ids["eot"]]
            lab += [-100, -100, -100, ids["num"][c], -100, -100]
        rows.append((row[:-1], lab[:-1]))                  # inputs x_t predict x_{t+1}: label at the <eq> position is c
    rows = rows[:limit] if limit else rows
    for j in range(0, len(rows), bs):
        part = rows[j:j + bs]
        Lm = max(len(r) for r, _ in part)
        x = torch.tensor([r + [ids["eot"]] * (Lm - len(r)) for r, _ in part])
        y = torch.tensor([lb + [-100] * (Lm - len(lb)) for _, lb in part])
        loss = F.cross_entropy(logits(m, w_out, x).flatten(0, 1), y.flatten(), ignore_index=-100, reduction="sum") / len(facts)
        loss.backward()
    gi = m.emb.weight.grad[num].double().numpy()
    go = w_out.grad[num].double().numpy()
    return gi, go


def main() -> None:
    torch.set_num_threads(2)
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(L.TOK_FILE))
    ids = L.special_ids(tok)
    nl, vocab = tok.token_to_id("Ċ"), tok.get_vocab_size()
    # label check: the label of each <eq> position is the answer token c
    m, w = build(4100, vocab)
    t = time.time()
    grads(m, w, ids, nl, np.load(SPL / "seed4000_F.npy").astype(np.int64), limit=16)
    print(f"timing: one batch of 16 sequences {time.time() - t:.2f} s", flush=True)
    out = {"rows": [], "config": {"model": "lm_stage2.GPT d384 L6 H6 ctx256", "vocab": vocab, "k": 16, "template": "T0"}}
    for s in (4000, 4001):
        tg = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        g = {}
        for arm in "FG":
            m, w = build(s + 100, vocab)                    # identical init for F and G
            g[arm] = grads(m, w, ids, nl, np.load(SPL / f"seed{s}_{arm}.npy").astype(np.int64))
        r = {"seed": s, "model_seed": s + 100, "targets": tg}
        for side, fn in (("in", lambda x: x[0]), ("out", lambda x: x[1]), ("tied", lambda x: x[0] + x[1])):
            pF, pG = A.power(fn(g["F"])), A.power(fn(g["G"]))
            r[f"dpow_grad_{side}"] = A.delta_pow(pF, pG, tg["F"], tg["G"])
            r[f"top5_F_{side}"] = (np.argsort(pF)[::-1][:5] + 1).tolist()
            r[f"top5_G_{side}"] = (np.argsort(pG)[::-1][:5] + 1).tolist()
        out["rows"].append(r)
        print(json.dumps(r), flush=True)
    d = [r["dpow_grad_in"] for r in out["rows"]]
    out["reading"] = ("gestuetzt" if all(v is not None and v > 1 for v in d) else
                      "nicht gestuetzt" if all(v is not None and v <= 0 for v in d) else "unklar")
    (HERE / "first_gradient_scratch.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(out["reading"])


if __name__ == "__main__":
    main()
