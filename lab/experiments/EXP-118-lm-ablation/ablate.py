"""EXP-118 (session 51): do the steered frequencies carry the facts in the small language model? Exploration on seen models, no
training. Written before any ablation was computed.

Models: completed F/G pairs of seed 3862 (EXP-102 P1 splits of seed 3802): EXP-114 raw_k19 (K = 19, 4000 steps) and EXP-113
raw_answer (K = 8, 16 000 steps); common held-out test set EXP-113 tests/seed3802_test.npy. Tied embeddings: the 113 number-token
rows X of emb.weight are both input and output vectors, so an ablation acts on both sides.
Ablation: X <- X - P_S X, P_S = projection onto the Fourier subspace (cos/sin over the number index n = 0..112) of the frequency
set S; the constant component is untouched. Sets: own targets of the run's split, the other split's targets, and 4 control sets
of 5 frequencies drawn from 1..56 without both target sets (numpy default_rng(118)).
Measure: held-out fact accuracy (prompt T0 without the answer, argmax over the 113 number tokens, as in lm_stage2.evaluate).
Contrast per run: C = acc(ablate other) - acc(ablate own); also acc(ablate own) against the mean control.
Readings (fixed before running; 4 runs): 'Ziele funktional' if C > 0.3 in all 4 runs and acc(ablate own) < mean control - 0.3
in all 4; 'nicht funktional' if |C| < 0.1 in all 4; else 'unklar'. Exploration (1 seed, 2 configurations).
  python lab/tools/guarded_run.py -- C:/.../.venv-gpu/Scripts/python.exe lab/experiments/EXP-118-lm-ablation/ablate.py
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
TEST = LAB / "experiments/EXP-113-lm-ladder-stage2b/tests/seed3802_test.npy"
RUNS = {"K19": LAB / "experiments/EXP-114-lm-dilution-pilot/raw_k19", "K8": LAB / "experiments/EXP-113-lm-ladder-stage2b/raw_answer"}


def projector(S: list[int]) -> torch.Tensor:
    n = np.arange(P)
    B = np.stack([f(2 * np.pi * k * n / P) for k in S for f in (np.cos, np.sin)], 1)     # 113 x 2|S|
    Q, _ = np.linalg.qr(B)
    return torch.tensor(Q @ Q.T, dtype=torch.float32)


def main() -> None:
    torch.set_num_threads(2)
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(L.TOK_FILE))
    ids = L.special_ids(tok)
    t0 = L.tmpl_prompt(L.template_parts(tok)[0])
    targets = json.loads((SPL / "seed3802.json").read_text(encoding="utf-8"))["targets"]
    rng = np.random.default_rng(118)
    free = [k for k in range(1, 57) if k not in targets["F"] and k not in targets["G"]]
    controls = [sorted(rng.choice(free, 5, replace=False).tolist()) for _ in range(4)]
    test = np.load(TEST).astype(np.int64)
    a, b = test // P, test % P
    x = torch.tensor([[ids["eot"]] + t0[0] + [ids["num"][i]] + t0[1] + [ids["num"][j]] + t0[2] for i, j in zip(a, b)])
    c = torch.from_numpy((a + b) % P)
    num = torch.tensor(ids["num"])
    rows, out = [], {"controls": controls, "targets": targets}
    for cfg, root in RUNS.items():
        for arm in "FG":
            d = next(p for p in root.iterdir() if p.name.startswith(f"lm2_seed3862_seed3802_{arm}_"))
            res = json.loads((d / "result.json").read_text(encoding="utf-8"))
            assert res["status"] == "completed", d
            k = res["config"]
            model = L.GPT(tok.get_vocab_size(), k["ctx"], k["d"], k["layers"], k["heads"])
            model.load_state_dict(torch.load(d / "checkpoint.pt", map_location="cpu", weights_only=False)["model"])
            model.eval()
            X0 = model.emb.weight.data[num].clone()

            @torch.no_grad()
            def acc(S: list[int] | None) -> float:
                model.emb.weight.data[num] = X0 if S is None else X0 - projector(S) @ X0
                pred = torch.cat([model(x[i:i + 512])[:, -1, num].argmax(1) for i in range(0, len(x), 512)])
                model.emb.weight.data[num] = X0
                return float((pred == c).float().mean())

            own, other = targets[arm], targets["G" if arm == "F" else "F"]
            r = {"cfg": cfg, "arm": arm, "base": acc(None), "own": acc(own), "other": acc(other), "controls": [acc(S) for S in controls]}
            r["C"] = r["other"] - r["own"]
            r["own_vs_control"] = float(np.mean(r["controls"])) - r["own"]
            rows.append(r)
            print(json.dumps(r), flush=True)
    fun = all(r["C"] > 0.3 and r["own_vs_control"] > 0.3 for r in rows)
    non = all(abs(r["C"]) < 0.1 for r in rows)
    out.update({"reading": "Ziele funktional" if fun else "nicht funktional" if non else "unklar", "rows": rows})
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(out["reading"])


if __name__ == "__main__":
    main()
