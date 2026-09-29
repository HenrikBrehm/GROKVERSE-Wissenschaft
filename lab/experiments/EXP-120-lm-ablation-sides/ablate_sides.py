"""EXP-120 (session 54): in the untied language models of EXP-117, is the steered Fourier subspace used on the input side
(number-token rows of the input embedding), on the output side (number-token rows of the untied output layer), or both?
Exploration on seen models (4 runs, 2 seeds), no training. Written before any ablation was computed.

Models: EXP-117 raw/ (untied, K = 19, 6000 steps; seeds 3862/3863 on EXP-102 P1 splits 3802/3803, arms F/G), each evaluated
on the held-out test set it was trained with (EXP-113 tests/seed3802_test.npy resp. seed3803_test.npy).
Ablation as in EXP-118 / LM1-F: X <- X - P_S X on the 113 number-token rows, P_S = projection onto the cos/sin subspace of the
frequency set S over the number index (constant component untouched). Sides: 'in' (emb.weight rows), 'out' (head.weight rows),
'both'. Sets: own targets, the other split's targets, 4 control sets of 5 frequencies from 1..56 without both target sets
(numpy default_rng(SeedSequence([120, split_seed]))).
Measure: held-out fact accuracy (prompt T0, argmax over the 113 number tokens, as in lm_untied.evaluate).
Contrast per run and side: C_side = acc(side, other) - acc(side, own).
Readings (fixed before running, over the 4 runs): 'beide Seiten' if C_in > 0.3 and C_out > 0.3 in all 4; 'nur Eingabe' if
C_in > 0.3 in all 4 and |C_out| < 0.1 in all 4; 'nur Ausgabe' mirrored; 'keine Seite allein' if |C_in| < 0.1 and |C_out| < 0.1
in all 4 while C_both > 0.3 in all 4; else 'unklar'. Check: base accuracy must equal the logged final test accuracy (|diff| < 1e-6).
  python lab/tools/guarded_run.py -- C:/.../.venv-gpu/Scripts/python.exe lab/experiments/EXP-120-lm-ablation-sides/ablate_sides.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-117-lm-untied"))
import lm_untied as L  # noqa: E402

P = 113
SPL = LAB / "experiments/EXP-102-lm-ladder-stage1/splits"
TESTS = LAB / "experiments/EXP-113-lm-ladder-stage2b/tests"
RAW = LAB / "experiments/EXP-117-lm-untied/raw"
RUNS = [(3862, 3802), (3863, 3803)]


def projector(S: list[int]) -> torch.Tensor:
    n = np.arange(P)
    B = np.stack([f(2 * np.pi * k * n / P) for k in S for f in (np.cos, np.sin)], 1)     # 113 x 2|S|
    Q, _ = np.linalg.qr(B)
    return torch.tensor(Q @ Q.T, dtype=torch.float32)


def main() -> None:
    torch.set_num_threads(4)
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(L.TOK_FILE))
    ids = L.special_ids(tok)
    t0 = L.tmpl_prompt(L.template_parts(tok)[0])
    num = torch.tensor(ids["num"])
    rows, out = [], {"runs": {}}
    for seed, split_seed in RUNS:
        targets = json.loads((SPL / f"seed{split_seed}.json").read_text(encoding="utf-8"))["targets"]
        rng = np.random.default_rng(np.random.SeedSequence([120, split_seed]))
        free = [k for k in range(1, 57) if k not in targets["F"] and k not in targets["G"]]
        controls = [sorted(rng.choice(free, 5, replace=False).tolist()) for _ in range(4)]
        out["runs"][str(seed)] = {"targets": targets, "controls": controls}
        test = np.load(TESTS / f"seed{split_seed}_test.npy").astype(np.int64)
        a, b = test // P, test % P
        x = torch.tensor([[ids["eot"]] + t0[0] + [ids["num"][i]] + t0[1] + [ids["num"][j]] + t0[2] for i, j in zip(a, b)])
        c = torch.from_numpy((a + b) % P)
        for arm in "FG":
            d = next(p for p in RAW.iterdir() if p.name.startswith(f"lm2_seed{seed}_seed{split_seed}_{arm}_"))
            res = json.loads((d / "result.json").read_text(encoding="utf-8"))
            assert res["status"] == "completed" and res["config"]["untied"], d
            k = res["config"]
            model = L.GPT(tok.get_vocab_size(), k["ctx"], k["d"], k["layers"], k["heads"])
            model.load_state_dict(torch.load(d / "checkpoint.pt", map_location="cpu", weights_only=False)["model"])
            model.eval()
            W = {"in": model.emb.weight.data, "out": model.head.weight.data}
            X0 = {s: W[s][num].clone() for s in W}

            @torch.no_grad()
            def acc(S: list[int] | None, sides: tuple[str, ...]) -> float:
                for s in sides:
                    W[s][num] = X0[s] if S is None else X0[s] - projector(S) @ X0[s]
                pred = torch.cat([model(x[i:i + 512])[:, -1, num].argmax(1) for i in range(0, len(x), 512)])
                for s in sides:
                    W[s][num] = X0[s]
                return float((pred == c).float().mean())

            own, other = targets[arm], targets["G" if arm == "F" else "F"]
            r = {"seed": seed, "arm": arm, "base": acc(None, ("in",)), "logged": res["curve"][-1][2]}
            r["base_minus_logged"] = r["base"] - r["logged"]
            for name, sides in (("in", ("in",)), ("out", ("out",)), ("both", ("in", "out"))):
                r[f"{name}_own"], r[f"{name}_other"] = acc(own, sides), acc(other, sides)
                r[f"{name}_ctl"] = [acc(S, sides) for S in controls]
                r[f"C_{name}"] = r[f"{name}_other"] - r[f"{name}_own"]
            rows.append(r)
            print(json.dumps(r), flush=True)
    ok = all(abs(r["base_minus_logged"]) < 1e-6 for r in rows)
    ci, co, cb = ([r[f"C_{s}"] for r in rows] for s in ("in", "out", "both"))
    if not ok:
        reading = "nicht auswertbar (Basis weicht vom Log ab)"
    elif all(v > 0.3 for v in ci) and all(v > 0.3 for v in co):
        reading = "beide Seiten"
    elif all(v > 0.3 for v in ci) and all(abs(v) < 0.1 for v in co):
        reading = "nur Eingabe"
    elif all(v > 0.3 for v in co) and all(abs(v) < 0.1 for v in ci):
        reading = "nur Ausgabe"
    elif all(abs(v) < 0.1 for v in ci + co) and all(v > 0.3 for v in cb):
        reading = "keine Seite allein"
    else:
        reading = "unklar"
    out.update({"reading": reading, "rows": rows, "script": "ablate_sides.py"})
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(reading)


if __name__ == "__main__":
    main()
