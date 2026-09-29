"""EXP-118 Nachtrag 1 (session 51): the same ablation as ablate.py at the four EXP-115 models (flat number counts, EXP-104
splits m = 500, seeds 3850/3851, model seeds 3950/3951, 4000 steps). Written before any ablation of these models.
Question: EXP-115 showed Delta_pow falling after a peak at step 2500 (to 4.35 / 0.96 at 4000). Do the targets still carry the
held-out facts at step 4000, i.e. is the falling energy still functional? Targets and 'other' targets from the split metadata
(targets / other_targets); 4 control sets per seed from 1..56 without both target sets (default_rng(118 + seed)); test sets
s385x_test.npy. Readings per seed (fixed before running), with C = acc(other) - acc(own) per run:
  'funktional'       C > 0.3 in both runs of the seed,
  'nicht funktional' |C| < 0.1 in both runs,
  else 'unklar'.
Descriptive: whether the seed with the weak final Delta_pow (3951, 0.96) is less functional than 3950 (4.35). Exploration.
  python lab/tools/guarded_run.py -- C:/.../.venv-gpu/Scripts/python.exe lab/experiments/EXP-118-lm-ablation/ablate_flat.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(LAB / "experiments/EXP-105-lm-ladder-stage2"))
import lm_stage2 as L  # noqa: E402
from ablate import P, projector  # noqa: E402

SPL = LAB / "experiments/EXP-104-flat-marginal-splits/splits"
RAW = LAB / "experiments/EXP-115-lm-flat-marginals/raw"


def main() -> None:
    torch.set_num_threads(4)
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(L.TOK_FILE))
    ids = L.special_ids(tok)
    t0 = L.tmpl_prompt(L.template_parts(tok)[0])
    num = torch.tensor(ids["num"])
    rows, per_seed = [], {}
    for s in (3850, 3851):
        meta = {a: json.loads((SPL / f"s{s}_{a}_m500.json").read_text(encoding="utf-8")) for a in "FG"}
        both = set(meta["F"]["targets"]) | set(meta["G"]["targets"])
        rng = np.random.default_rng(118 + s)
        controls = [sorted(rng.choice([k for k in range(1, 57) if k not in both], 5, replace=False).tolist()) for _ in range(4)]
        test = np.load(SPL / f"s{s}_test.npy").astype(np.int64)
        a, b = test // P, test % P
        x = torch.tensor([[ids["eot"]] + t0[0] + [ids["num"][i]] + t0[1] + [ids["num"][j]] + t0[2] for i, j in zip(a, b)])
        c = torch.from_numpy((a + b) % P)
        for arm in "FG":
            d = next(RAW.glob(f"lm2_seed{s + 100}_s{s}_{arm}_m500_steps4000_*"))
            res = json.loads((d / "result.json").read_text(encoding="utf-8"))
            assert res["status"] == "completed", d
            k = res["config"]
            model = L.GPT(tok.get_vocab_size(), k["ctx"], k["d"], k["layers"], k["heads"])
            ck = torch.load(d / "checkpoint.pt", map_location="cpu", weights_only=False)
            assert ck["step"] == 4000 and ck["config_hash"] == res["config_hash"], d
            model.load_state_dict(ck["model"])
            model.eval()
            X0 = model.emb.weight.data[num].clone()

            @torch.no_grad()
            def acc(S: list[int] | None) -> float:
                model.emb.weight.data[num] = X0 if S is None else X0 - projector(S) @ X0
                pred = torch.cat([model(x[i:i + 512])[:, -1, num].argmax(1) for i in range(0, len(x), 512)])
                model.emb.weight.data[num] = X0
                return float((pred == c).float().mean())

            r = {"seed": s, "arm": arm, "base": acc(None), "own": acc(meta[arm]["targets"]), "other": acc(meta[arm]["other_targets"]),
                 "controls": [acc(S) for S in controls]}
            r["C"] = r["other"] - r["own"]
            rows.append(r)
            print(json.dumps(r), flush=True)
        cs = [r["C"] for r in rows if r["seed"] == s]
        per_seed[s] = "funktional" if all(v > 0.3 for v in cs) else "nicht funktional" if all(abs(v) < 0.1 for v in cs) else "unklar"
    out = {"readings": per_seed, "rows": rows}
    (HERE / "summary_flat.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(per_seed))


if __name__ == "__main__":
    main()
