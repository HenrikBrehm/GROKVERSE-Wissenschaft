"""EXP-129 feasibility (session 60, no training): draw the unchanged lm_stage2 Stream without a model until the first
text wrap, for K = 1 and K = 2 (check against the known K = 2 wrap at about 15 135 steps), EXP-116 seeds/splits.
Reports: steps before the first wrap (batch 32), arithmetic token share, fact rounds (exposures per fact) at the wrap and
at 10 000 steps.   python lab/tools/guarded_run.py -- <.venv-gpu python> lab/experiments/EXP-129-lm-k1-share/wrap_budget.py"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "EXP-105-lm-ladder-stage2"))
import lm_stage2 as L  # noqa: E402
from tokenizers import Tokenizer  # noqa: E402

tok = Tokenizer.from_file(str(L.TOK_FILE))
ids = L.special_ids(tok)
L.NUM_ID = ids["num"]
text = np.load(L.TEXT_NPY, mmap_mode="r")
parts = L.template_parts(tok)
SPL = HERE.parent / "EXP-102-lm-ladder-stage1" / "splits"
out = {"text_tokens": int(len(text))}
for k in (2, 1):
    for seed, split in ((3864, "seed3804_F"), (3865, "seed3805_G")):
        facts = np.load(SPL / f"{split}.npy").astype(np.int64)
        s = L.Stream(text, facts, parts, tok.token_to_id("Ċ"), ids["eot"], seed, 256, k)
        step, at10k = 0, None
        while s.wraps == 0:
            for _ in range(32):
                s.sequence()
            step += 1
            if step == 10000:
                at10k = s.rounds + s.fact_pos / len(facts)
        r = {"k": k, "seed": seed, "split": split, "n_facts": int(len(facts)), "first_wrap_step": step,
             "arith_share": s.n_arith / s.n_tok, "exposures_per_fact_at_wrap": s.rounds + s.fact_pos / len(facts),
             "exposures_per_fact_at_10000": at10k}
        print(json.dumps(r), flush=True)
        out[f"k{k}_{seed}"] = r
(HERE / "wrap_budget.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
