"""Session 59, last step of the first-gradient line (written before running). K = 1 at the LM1 random init carried the mask targets
('gestuetzt', first_gradient_shuffled_scratch_k1.json); stored LM runs with K = 2 but ~230 text tokens per sequence showed no early
steering (EXP-116/posthoc_early_k_s59). Claim to test: text in the context hides the first-order signal as other facts do.
Same measurement as first_gradient_shuffled.py --model scratch --k 1 (training order, answer loss, number-row gradient, output layer as
a second copy of the tied matrix), but each sequence = N_TEXT = 90 TinyStories validation tokens (offset per sequence from numpy
SeedSequence([59, model_seed, 7]); valid_u16.npy of lm_stage2) followed by <eot> a <plus> b <eq> c <eot>. Loss only on c.
Reading (fixed before running): 'gestuetzt' if Delta_pow(grad, in) > 1 in both seeds; 'nicht gestuetzt' if <= 0 in both; else 'unklar'.
Interpretation (fixed before running): 'nicht gestuetzt' or 'unklar' with both values < 0.5 -> text context also hides the signal
(supports the reading of posthoc_early_k_s59); 'gestuetzt' -> only other facts in the context interfere, text does not.
  python lab/tools/guarded_run.py -- <abs>/.venv-gpu/Scripts/python.exe lab/experiments/EXP-127-pretrained-lm/first_gradient_text.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "lab/experiments/EXP-105-lm-ladder-stage2"))
import analyze as A  # noqa: E402
import first_gradient_shuffled as S  # noqa: E402
import lm_stage2 as L  # noqa: E402

N_TEXT = 90


def main() -> None:
    dev = "cuda"
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(L.TOK_FILE))
    ids = L.special_ids(tok)
    vocab = tok.get_vocab_size()
    valid = np.load(L.VALID_NPY, mmap_mode="r")
    num_t = torch.tensor(ids["num"], device=dev)
    out = {"n_text": N_TEXT, "rows": []}
    for s in (4000, 4001):
        ms = s + 100
        tg = json.loads((S.SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        g = {}
        for arm in "FG":
            facts = np.load(S.SPL / f"seed{s}_{arm}.npy").astype(np.int64)
            g_init = np.random.default_rng(np.random.SeedSequence([105, ms, 4]))
            torch.manual_seed(int(g_init.integers(2**62)))
            m = L.GPT(vocab, 256, 384, 6, 6).to(dev)
            w_out = torch.nn.Parameter(m.emb.weight.detach().clone())

            def logits(x, m=m, w_out=w_out):
                h = m.emb(x) + m.pos(torch.arange(x.shape[1], device=dev))
                for b in m.blocks:
                    h = b(h)
                return m.ln(h) @ w_out.T
            perm = np.random.default_rng(np.random.SeedSequence([105, ms, 2])).permutation(len(facts))
            offs = np.random.default_rng(np.random.SeedSequence([59, ms, 7])).integers(0, len(valid) - N_TEXT, len(facts))
            rows = []
            for (row, lab), o in zip(S.sequences(facts[perm], ids["num"], ids["plus"], ids["eq"], ids["eot"], ids["eot"], 1), offs):
                txt = valid[o:o + N_TEXT].astype(np.int64).tolist()
                rows.append((txt + row, [-100] * N_TEXT + lab))
            S.run_grads(rows, logits, len(facts), dev)
            g[arm] = (m.emb.weight.grad[num_t].double().cpu().numpy(), w_out.grad[num_t].double().cpu().numpy())
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
    (HERE / "first_gradient_text.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(out["reading"])


if __name__ == "__main__":
    main()
