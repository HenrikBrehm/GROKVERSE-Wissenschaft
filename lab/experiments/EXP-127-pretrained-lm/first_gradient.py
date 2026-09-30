"""EXP-127 side question (session 58, written BEFORE any pilot run and before computing anything here): does the first-order
account of Appendix G (the first embedding gradient carries the spectrum of the training-pair mask) hold at the weights of a
PRETRAINED model? No training: pretrained Pythia-160M, full-dataset gradient of the answer loss (same batches as
ft_pythia.py: K = 16 facts per sequence, every training fact exactly once, fixed order) w.r.t. the number-token rows of
embed_in and embed_out, for arms F and G of the pilot seeds 4000 and 4001.
Measure: Delta_pow (EXP-102 definition) of the gradient rows, input side primary, output side secondary.
Reading (fixed before running): 'gestuetzt' if Delta_pow(grad, in) > 1 in both seeds; 'nicht gestuetzt' if <= 0 in both;
else 'unklar'. Later (descriptive): compare with the pilot's residual-update Delta_pow (does the first gradient predict it?).
CPU, 4 threads.
  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-127-pretrained-lm/first_gradient.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze as A  # noqa: E402
import ft_pythia as T  # noqa: E402

ROOT = HERE.parents[2]
SPL = ROOT / "lab/confirm/lm1_splits"


def grads(model, ids: dict, facts: np.ndarray, k: int = 16, bs: int = 16) -> tuple[np.ndarray, np.ndarray]:
    num = torch.tensor(ids["num"])
    model.zero_grad(set_to_none=True)
    n_seq = -(-len(facts) // k)
    rows = []
    for i in range(n_seq):
        chunk = facts[i * k:(i + 1) * k]
        row, lab = [ids["eot"]], [-100]
        for f in chunk:
            a, b = divmod(int(f), T.P)
            c = (a + b) % T.P
            row += [ids["num"][a], ids["op"], ids["num"][b], ids["eq"], ids["num"][c], ids["nl"]]
            lab += [-100, -100, -100, ids["num"][c], -100, -100]
        rows.append((row, lab))
    total = len(facts)
    for j in range(0, len(rows), bs):
        part = rows[j:j + bs]
        L = max(len(r) for r, _ in part)
        x = torch.tensor([r + [ids["eot"]] * (L - len(r)) for r, _ in part])
        y = torch.tensor([lb + [-100] * (L - len(lb)) for _, lb in part])
        sel = y != -100
        h = model.gpt_neox(x).last_hidden_state[sel]
        loss = F.cross_entropy(model.get_output_embeddings()(h), y[sel], reduction="sum") / total
        loss.backward()
    gi = model.get_input_embeddings().weight.grad[num].double().numpy()
    go = model.get_output_embeddings().weight.grad[num].double().numpy()
    return gi, go


def main() -> None:
    torch.set_num_threads(4)
    tok, model = T.load_model("cpu")
    ids = T.token_ids(tok)
    out = {"rows": []}
    for s in (4000, 4001):
        tg = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        g = {}
        for arm in "FG":
            facts = np.load(SPL / f"seed{s}_{arm}.npy").astype(np.int64)
            g[arm] = grads(model, ids, facts)
        r = {"seed": s, "targets": tg}
        for side, idx in (("in", 0), ("out", 1)):
            pF, pG = A.power(g["F"][idx]), A.power(g["G"][idx])
            r[f"dpow_grad_{side}"] = A.delta_pow(pF, pG, tg["F"], tg["G"])
            r[f"top5_F_{side}"] = (np.argsort(pF)[::-1][:5] + 1).tolist()
            r[f"top5_G_{side}"] = (np.argsort(pG)[::-1][:5] + 1).tolist()
        out["rows"].append(r)
        print(json.dumps(r), flush=True)
    d = [r["dpow_grad_in"] for r in out["rows"]]
    out["reading"] = ("gestuetzt" if all(v is not None and v > 1 for v in d) else
                      "nicht gestuetzt" if all(v is not None and v <= 0 for v in d) else "unklar")
    (HERE / "first_gradient.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(out["reading"])


if __name__ == "__main__":
    main()
