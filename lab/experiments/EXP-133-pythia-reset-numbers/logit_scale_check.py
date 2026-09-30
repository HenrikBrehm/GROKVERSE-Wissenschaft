"""EXP-133 pre-run diagnostic (session 62): answer-position logits over the 113 number tokens, pretrained vs reset rows.
The CPU smoke showed loss 830 after 2 steps; this checks whether the reset output rows give huge initial logits."""
import sys
from pathlib import Path
import numpy as np, torch, torch.nn.functional as F
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "EXP-127-pretrained-lm"))
import ft_pythia as ft
import ft_reset as fr
torch.set_num_threads(2)
test = np.load("lab/confirm/lm1_splits/seed4000_test.npy")[:64]
for name, reset in (("pretrained", False), ("reset", True)):
    tok, m = fr._orig_load("cpu")
    ids = ft.token_ids(tok)
    if reset:
        fr.reset_rows(m, ids["num"], 4000)
    x, c = ft.prompts(test, ids)
    with torch.no_grad():
        h = m.gpt_neox(x).last_hidden_state[:, -1]
        lg = m.get_output_embeddings()(h)
        lnum = lg[:, ids["num"]]
        loss = F.cross_entropy(lg, torch.tensor(ids["num"])[c])
    print(f"{name}: |h| {h.norm(dim=1).mean():.1f}  number-logit sd {lnum.std(dim=1).mean():.2f}  "
          f"max|logit| num {lnum.abs().max():.1f} all {lg.abs().max():.1f}  CE {loss:.2f}", flush=True)
