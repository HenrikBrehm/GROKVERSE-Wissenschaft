"""Session 55, post hoc (reading fixed in JOURNAL S55 cycle 4 before computing): held-out accuracy of the two EXP-121 Rf end models
(checkpoint.pt, step 4000) split by whether the swapped pair (b, a) is in the run's own training split; same prompt/argmax as
EXP-119/commutativity_s54.py. Reading: 'nur Kommutativitaet' if acc_other <= 0.1 in both runs; 'ueber Kommutativitaet hinaus' if
acc_other >= 0.5 in both; else 'teilweise'.
  python lab/tools/guarded_run.py -- C:/.../.venv-gpu/Scripts/python.exe lab/experiments/EXP-121-lm-flat-random-arm/commutativity_s55.py [--device cuda]
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
RUNS = [(3950, 3850), (3951, 3851)]


def main() -> None:
    dev = sys.argv[sys.argv.index("--device") + 1] if "--device" in sys.argv else "cpu"
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(L.TOK_FILE))
    ids = L.special_ids(tok)
    t0 = L.tmpl_prompt(L.template_parts(tok)[0])
    num = torch.tensor(ids["num"], device=dev)
    rows = []
    for seed, s in RUNS:
        test = np.load(HERE / "splits" / f"s{s}_Rf_test.npy").astype(np.int64)
        a, b = test // P, test % P
        x = torch.tensor([[ids["eot"]] + t0[0] + [ids["num"][i]] + t0[1] + [ids["num"][j]] + t0[2] for i, j in zip(a, b)], device=dev)
        c = torch.from_numpy((a + b) % P).to(dev)
        d = next(p for p in (HERE / "raw").iterdir() if p.name.startswith(f"lm2_seed{seed}_s{s}_Rf_"))
        res = json.loads((d / "result.json").read_text(encoding="utf-8"))
        k = res["config"]
        model = L.GPT(tok.get_vocab_size(), k["ctx"], k["d"], k["layers"], k["heads"])
        model.load_state_dict(torch.load(d / "checkpoint.pt", map_location="cpu", weights_only=False)["model"])
        model.to(dev).eval()
        with torch.no_grad():
            pred = torch.cat([model(x[i:i + 512])[:, -1, num].argmax(1) for i in range(0, len(x), 512)])
        ok = (pred == c).cpu().numpy()
        train = set(np.load(HERE / "splits" / f"s{s}_Rf_m500.npy").astype(np.int64).tolist())
        swap_in = np.array([int(bb) * P + int(aa) in train for aa, bb in zip(a, b)])
        r = {"seed": seed, "split": s, "acc": float(ok.mean()), "logged": res["curve"][-1][2], "n_swap_in": int(swap_in.sum()),
             "n_other": int((~swap_in).sum()), "acc_swap_in": float(ok[swap_in].mean()), "acc_other": float(ok[~swap_in].mean())}
        rows.append(r)
        print(json.dumps(r), flush=True)
    if all(r["acc_other"] <= 0.1 for r in rows):
        reading = "nur Kommutativitaet"
    elif all(r["acc_other"] >= 0.5 for r in rows):
        reading = "ueber Kommutativitaet hinaus"
    else:
        reading = "teilweise"
    (HERE / "commutativity_s55.json").write_text(json.dumps({"reading": reading, "rows": rows}, indent=1), encoding="utf-8")
    print(reading)


if __name__ == "__main__":
    main()
