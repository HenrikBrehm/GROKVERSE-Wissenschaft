"""Session 56, post hoc exploration (reading fixed in JOURNAL S56 cycle 6 before computing): with the loss on every position
(EXP-113 arm 'all', K = 8), the engineered F/G models memorized the training facts but held-out accuracy stayed at about
0.1-0.35. Is this the commutativity plateau of the random split in EXP-119 (held-out facts right exactly where the mirrored fact
(b, a) was trained)? Same measurement as EXP-119 commutativity_s54.py (final checkpoint, prompt T0, argmax over the 113 number
tokens), for all 8 EXP-113 models (arms 'all' and 'answer').
Reading (arm 'all', 4 models): 'Kommutativitaets-Plateau' if acc(swap in train) >= 0.8 and acc(else) <= 0.1 in >= 3 of 4;
'nicht Kommutativitaet' if the two accuracies differ by < 0.2 in >= 3 of 4; else 'teilweise'.
  python lab/tools/guarded_run.py -- C:/.../.venv-gpu/Scripts/python.exe lab/experiments/EXP-113-lm-ladder-stage2b/commutativity_s56.py [--device cuda]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-105-lm-ladder-stage2"))
import lm_stage2 as L  # noqa: E402

P = 113
SPL = LAB / "experiments/EXP-102-lm-ladder-stage1/splits"
RUNS = [(3862, 3802), (3863, 3803)]


def main() -> None:
    dev = sys.argv[sys.argv.index("--device") + 1] if "--device" in sys.argv else "cpu"
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(L.TOK_FILE))
    ids = L.special_ids(tok)
    t0 = L.tmpl_prompt(L.template_parts(tok)[0])
    num = torch.tensor(ids["num"], device=dev)
    rows = []
    for loss in ("all", "answer"):
        for seed, split_seed in RUNS:
            test = np.load(HERE / "tests" / f"seed{split_seed}_test.npy").astype(np.int64)
            a, b = test // P, test % P
            x = torch.tensor([[ids["eot"]] + t0[0] + [ids["num"][i]] + t0[1] + [ids["num"][j]] + t0[2] for i, j in zip(a, b)],
                             device=dev)
            c = torch.from_numpy((a + b) % P).to(dev)
            for arm in "FG":
                ds = [p for p in (HERE / f"raw_{loss}").iterdir() if p.name.startswith(f"lm2_seed{seed}_seed{split_seed}_{arm}_")]
                assert len(ds) == 1, ds
                res = json.loads((ds[0] / "result.json").read_text(encoding="utf-8"))
                assert res["status"] == "completed" and res["config"].get("loss", "all") == loss  # trainer omits the key for the default "all", ds[0]
                k = res["config"]
                model = L.GPT(tok.get_vocab_size(), k["ctx"], k["d"], k["layers"], k["heads"])
                ck = torch.load(ds[0] / "checkpoint.pt", map_location="cpu", weights_only=False)
                assert ck["step"] == res["steps_completed"], (ds[0], ck["step"])
                model.load_state_dict(ck["model"])
                model.to(dev).eval()
                with torch.no_grad():
                    pred = torch.cat([model(x[i:i + 512])[:, -1, num].argmax(1) for i in range(0, len(x), 512)])
                ok = (pred == c).cpu().numpy()
                train = set(np.load(SPL / f"seed{split_seed}_{arm}.npy").astype(np.int64).tolist())
                swap_in = np.array([int(bb) * P + int(aa) in train for aa, bb in zip(a, b)])
                r = {"loss": loss, "seed": seed, "arm": arm, "step": ck["step"], "acc": float(ok.mean()), "logged": res["curve"][-1][2],
                     "train_logged": res["curve"][-1][1], "n_swap_in": int(swap_in.sum()), "n_other": int((~swap_in).sum()),
                     "acc_swap_in": float(ok[swap_in].mean()) if swap_in.any() else None,
                     "acc_other": float(ok[~swap_in].mean()) if (~swap_in).any() else None}
                rows.append(r)
                print(json.dumps(r), flush=True)
    A = [r for r in rows if r["loss"] == "all"]
    if sum(r["acc_swap_in"] >= 0.8 and r["acc_other"] <= 0.1 for r in A) >= 3:
        reading = "Kommutativitaets-Plateau"
    elif sum(abs(r["acc_swap_in"] - r["acc_other"]) < 0.2 for r in A) >= 3:
        reading = "nicht Kommutativitaet"
    else:
        reading = "teilweise"
    (HERE / "commutativity_s56.json").write_text(json.dumps({"reading": reading, "rows": rows}, indent=1), encoding="utf-8")
    print(reading)


if __name__ == "__main__":
    main()
