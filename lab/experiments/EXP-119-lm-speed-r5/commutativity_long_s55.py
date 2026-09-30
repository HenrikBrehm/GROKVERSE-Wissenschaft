"""EXP-119 addendum 2 (session 55, written before the run; readings in README "Nachtrag 2"): does the commutativity plateau of the
random split R (seed 3866, seed3806_R) hold to 16 000 steps? Reads raw_long/<run>/result.json and checkpoint.pt (step 16 000).
Technical check: held-out accuracy at step 6000 within +-0.05 of the original run (0.333), else descriptive only.
Reading: 'spaetes Grokking' if held-out accuracy reaches 0.5 by 16 000; 'Plateau haelt' if it is < 0.4 at 16 000 and the accuracy
on held-out facts without a trained mirror is <= 0.1; else 'unklar'. Mirror split, prompt and argmax as commutativity_s54.py.
  python lab/tools/guarded_run.py -- C:/.../.venv-gpu/Scripts/python.exe lab/experiments/EXP-119-lm-speed-r5/commutativity_long_s55.py [--device cuda]
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
SEED, SPLIT = 3866, 3806
SPL = LAB / "experiments/EXP-102-lm-ladder-stage1/splits"


def main() -> None:
    dev = sys.argv[sys.argv.index("--device") + 1] if "--device" in sys.argv else "cpu"
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(L.TOK_FILE))
    ids = L.special_ids(tok)
    t0 = L.tmpl_prompt(L.template_parts(tok)[0])
    num = torch.tensor(ids["num"], device=dev)
    d = next(p for p in (HERE / "raw_long").iterdir() if p.name.startswith(f"lm2_seed{SEED}_seed{SPLIT}_R_steps16000_"))
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    if res.get("status") != "completed":
        raise SystemExit(f"run not completed: {res.get('status')}")
    curve = {int(c[0]): c for c in res["curve"]}
    at6000 = curve[6000][2]
    test = np.load(HERE / "tests" / f"seed{SPLIT}_test.npy").astype(np.int64)
    a, b = test // P, test % P
    x = torch.tensor([[ids["eot"]] + t0[0] + [ids["num"][i]] + t0[1] + [ids["num"][j]] + t0[2] for i, j in zip(a, b)], device=dev)
    c = torch.from_numpy((a + b) % P).to(dev)
    k = res["config"]
    model = L.GPT(tok.get_vocab_size(), k["ctx"], k["d"], k["layers"], k["heads"])
    model.load_state_dict(torch.load(d / "checkpoint.pt", map_location="cpu", weights_only=False)["model"])
    model.to(dev).eval()
    with torch.no_grad():
        pred = torch.cat([model(x[i:i + 512])[:, -1, num].argmax(1) for i in range(0, len(x), 512)])
    ok = (pred == c).cpu().numpy()
    train = set(np.load(SPL / f"seed{SPLIT}_R.npy").astype(np.int64).tolist())
    swap_in = np.array([int(bb) * P + int(aa) in train for aa, bb in zip(a, b)])
    first05 = next((int(s) for s, *_r in res["curve"] if _r[1] >= 0.5), None)
    out = {"run": d.name, "test_at_6000": at6000, "technical_ok": abs(at6000 - 0.333) <= 0.05, "final_test": res["curve"][-1][2],
           "logged_equals_eval": abs(float(ok.mean()) - res["curve"][-1][2]) < 1e-6, "first_step_test_ge_0.5": first05,
           "acc_swap_in": float(ok[swap_in].mean()), "acc_other": float(ok[~swap_in].mean()),
           "curve_test_every_1000": [(int(s), round(cc[2], 3)) for s, *_x in res["curve"] for cc in [curve[int(s)]] if int(s) % 1000 == 0]}
    if first05 is not None:
        out["reading"] = "spaetes Grokking"
    elif out["final_test"] < 0.4 and out["acc_other"] <= 0.1:
        out["reading"] = "Plateau haelt"
    else:
        out["reading"] = "unklar"
    if not out["technical_ok"]:
        out["reading"] += " (nur beschreibend: Kurve bei 6000 weicht ab)"
    (HERE / "commutativity_long_s55.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
