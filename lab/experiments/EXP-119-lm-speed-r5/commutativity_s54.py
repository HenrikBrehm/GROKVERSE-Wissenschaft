"""Session 54, post hoc exploration (reading fixed in JOURNAL S54 cycle 10 before computing): is the ~0.3 plateau of the random
split R in EXP-119 explained by commutativity? Held-out accuracy of the final models (checkpoint.pt, step 6000) split by whether
the swapped pair (b, a) is in the run's own training split. Prompt T0, argmax over the 113 number tokens (as lm_stage2.evaluate).
Reading: 'Kommutativitaet erklaert das Plateau' if in both R runs acc(swap in train) >= 0.8 and acc(else) <= 0.1;
'nicht Kommutativitaet' if the two accuracies differ by < 0.2 in both R runs; else 'teilweise'.
  python lab/tools/guarded_run.py -- C:/.../.venv-gpu/Scripts/python.exe lab/experiments/EXP-119-lm-speed-r5/commutativity_s54.py [--device cuda]
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
RUNS = [(3866, 3806), (3867, 3807)]


def main() -> None:
    dev = sys.argv[sys.argv.index("--device") + 1] if "--device" in sys.argv else "cpu"
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(L.TOK_FILE))
    ids = L.special_ids(tok)
    t0 = L.tmpl_prompt(L.template_parts(tok)[0])
    num = torch.tensor(ids["num"], device=dev)
    rows = []
    for seed, split_seed in RUNS:
        test = np.load(HERE / "tests" / f"seed{split_seed}_test.npy").astype(np.int64)
        a, b = test // P, test % P
        x = torch.tensor([[ids["eot"]] + t0[0] + [ids["num"][i]] + t0[1] + [ids["num"][j]] + t0[2] for i, j in zip(a, b)], device=dev)
        c = torch.from_numpy((a + b) % P).to(dev)
        for arm in "FGR":
            d = next(p for p in (HERE / "raw").iterdir() if p.name.startswith(f"lm2_seed{seed}_seed{split_seed}_{arm}_"))
            res = json.loads((d / "result.json").read_text(encoding="utf-8"))
            k = res["config"]
            model = L.GPT(tok.get_vocab_size(), k["ctx"], k["d"], k["layers"], k["heads"])
            model.load_state_dict(torch.load(d / "checkpoint.pt", map_location="cpu", weights_only=False)["model"])
            model.to(dev).eval()
            with torch.no_grad():
                pred = torch.cat([model(x[i:i + 512])[:, -1, num].argmax(1) for i in range(0, len(x), 512)])
            ok = (pred == c).cpu().numpy()
            train = set(np.load(SPL / f"seed{split_seed}_{arm}.npy").astype(np.int64).tolist())
            swap_in = np.array([int(bb) * P + int(aa) in train for aa, bb in zip(a, b)])
            r = {"seed": seed, "arm": arm, "acc": float(ok.mean()), "logged": res["curve"][-1][2],
                 "n_swap_in": int(swap_in.sum()), "n_other": int((~swap_in).sum()),
                 "acc_swap_in": float(ok[swap_in].mean()) if swap_in.any() else None,
                 "acc_other": float(ok[~swap_in].mean()) if (~swap_in).any() else None}
            rows.append(r)
            print(json.dumps(r), flush=True)
    R = [r for r in rows if r["arm"] == "R"]
    if all(r["acc_swap_in"] >= 0.8 and r["acc_other"] <= 0.1 for r in R):
        reading = "Kommutativitaet erklaert das Plateau"
    elif all(abs(r["acc_swap_in"] - r["acc_other"]) < 0.2 for r in R):
        reading = "nicht Kommutativitaet"
    else:
        reading = "teilweise"
    (HERE / "commutativity_s54.json").write_text(json.dumps({"reading": reading, "rows": rows}, indent=1), encoding="utf-8")
    print(reading)


if __name__ == "__main__":
    main()
