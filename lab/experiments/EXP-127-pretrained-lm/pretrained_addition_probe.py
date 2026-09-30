"""EXP-127 context (session 58, descriptive): can pretrained Pythia-160M add small integers with "+", before any fine-tuning?
Prompt " a + b =" (greedy next token restricted to the number tokens " 0".." 224"), all pairs with a, b < 113 on a fixed
grid (every 7th a and b), split by whether a + b < 113. Also the neutral-operator prompt " a @ b =" used in EXP-127.
  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-127-pretrained-lm/pretrained_addition_probe.py
"""
import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

REPO, REV = "EleutherAI/pythia-160m", "50f5173d932e8e61f858120bcb800b97af589f46"
tok = AutoTokenizer.from_pretrained(REPO, revision=REV)
m = AutoModelForCausalLM.from_pretrained(REPO, revision=REV).eval()
num = [tok.encode(f" {n}", add_special_tokens=False) for n in range(225)]
assert all(len(x) == 1 for x in num)
num = torch.tensor([x[0] for x in num])
grid = range(0, 113, 7)
out = {}
for op in ("+", "@"):
    rows = []
    for a in grid:
        for b in grid:
            ids = tok.encode(f" {a} {op} {b} =", add_special_tokens=False)
            with torch.no_grad():
                pred = int(m(torch.tensor([ids])).logits[0, -1, num].argmax())
            rows.append((a, b, pred))
    r = np.array(rows)
    small = r[:, 0] + r[:, 1] < 113
    exact = r[:, 2] == r[:, 0] + r[:, 1]
    mod = r[:, 2] == (r[:, 0] + r[:, 1]) % 113
    out[op] = {"n": len(r), "int_acc_small": float(exact[small].mean()), "int_acc_large": float(exact[~small].mean()),
               "mod_acc_large": float(mod[~small].mean())}
    print(op, out[op], flush=True)
Path(__file__).with_name("pretrained_addition_probe.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
