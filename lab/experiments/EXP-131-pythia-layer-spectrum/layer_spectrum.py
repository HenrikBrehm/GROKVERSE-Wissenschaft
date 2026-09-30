"""EXP-131 (session 61, written before any fine-tuned EXP-130 model exists): does the fact selection steer the Fourier
spectrum of the number representation in the INTERMEDIATE layers of a fine-tuned Pythia-160M? (Pre-set follow-up of
EXP-127's reading "bricht": "Zwischenschichten messen, bevor etwas behauptet wird".)

Representation: prompt [eot, " a"] for a = 0..112; hidden state at position 1 (the number token) after every layer
(HF hidden_states: index 0 = embedding output, 1..12 = after each block; the last entry has the final LayerNorm applied).
With causal attention this state depends on a only, so H_l is a 113 x 768 matrix per layer and model.
Per seed s (arms F, G fine-tuned by EXP-130 from the same pretrained weights, saved as fp16 state dicts):
  U_l = H_l(T) - c * H_l(0),  c = <H_l(T), H_l(0)> / <H_l(0), H_l(0)>   (residual change against the pretrained model)
  Delta_pow_l = P1 Delta_pow of U_l (EXP-127 analyze.delta_pow; natural log; > 0 = each arm enriched in its own targets).
Readings (fixed in README before any model exists): gate = EXP-130 base accuracy >= 0.5 for all four models;
  "gesteuert (Zwischenschichten)" if Delta_pow_l > 1 on >= 3 consecutive layers l in 1..12 in both seeds;
  "nicht gesteuert" if |Delta_pow_l| <= 1 for all l in 1..12 in both seeds; else "unklar".
Descriptive: Delta_pow of the raw states H_l(T); top-5 frequencies of U_l; share of the pretrained top-8 input
frequencies {1, 2, 3, 11, 4, 5, 23, 45} in the power of U_l.

  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-131-pythia-layer-spectrum/layer_spectrum.py [--device cpu]
  ... layer_spectrum.py --selftest     (pretrained model only: pipeline check, no reading)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-127-pretrained-lm"))
import ft_pythia as ft  # noqa: E402
from analyze import delta_pow, power, residual  # noqa: E402  (EXP-127 analysis helpers, unchanged)

SEEDS = (4002, 4003)
MODELS = LAB / "experiments/EXP-130-pythia-functional-spectrum/raw/models"
RAW130 = LAB / "experiments/EXP-130-pythia-functional-spectrum/raw"
PRETRAINED_TOP8_IN = [1, 2, 3, 11, 4, 5, 23, 45]


@torch.no_grad()
def layer_states(model, ids: dict, device: str) -> np.ndarray:
    """(n_layers + 1) x 113 x d hidden states at the number position of [eot, a]."""
    x = torch.tensor([[ids["eot"], n] for n in ids["num"]], device=device)
    hs = model.gpt_neox(x, output_hidden_states=True).hidden_states
    return np.stack([h[:, 1].float().cpu().numpy() for h in hs])


def gate_ok() -> tuple[bool, dict]:
    base = {}
    for p in RAW130.glob("*/result.json"):
        r = json.loads(p.read_text(encoding="utf-8"))
        c = r.get("config", {})
        if r.get("status") == "completed" and c.get("steps") == 4000 and "sweep" in r.get("ablation", {}):
            base[f"{c['seed']}_{c['arm']}"] = r["ablation"]["base"]
    need = [f"{s}_{a}" for s in SEEDS for a in "FG"]
    return all(k in base and base[k] >= 0.5 for k in need), base


def reading(dp: dict) -> str:
    def consecutive(v: list) -> int:
        best = run = 0
        for x in v:
            run = run + 1 if (x is not None and x > 1) else 0
            best = max(best, run)
        return best
    if any(dp[s] is None for s in dp) or any(x is None for s in dp for x in dp[s][1:]):
        return "nicht auswertbar (nicht endlich)"
    if all(consecutive(dp[s][1:]) >= 3 for s in dp):
        return "gesteuert (Zwischenschichten)"
    if all(abs(x) <= 1 for s in dp for x in dp[s][1:]):
        return "nicht gesteuert"
    return "unklar"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    tok, model = ft.load_model(a.device)
    model.eval()
    ids = ft.token_ids(tok)
    pre_sd = {k: v.clone() for k, v in model.state_dict().items()}
    H0 = layer_states(model, ids, a.device)
    top = lambda pw: [int(k) + 1 for k in np.argsort(-pw)[:5]]   # noqa: E731
    if a.selftest:
        print("layers:", H0.shape, "top-5 per layer (pretrained):", [top(power(h)) for h in H0])
        n = np.arange(ft.P)
        W = np.random.default_rng(0).normal(size=(ft.P, 8))
        W2 = 0.9 * W + np.stack([np.cos(2 * np.pi * 17 * n / ft.P)] * 8, 1)
        assert top(power(residual(W2, W)))[0] == 17
        print("selftest ok")
        return
    ok, base = gate_ok()
    out: dict = {"gate": ok, "base_exp130": base, "seeds": {}}
    dp_all = {}
    for s in SEEDS:
        tj = json.loads((LAB / f"confirm/lm1_splits/seed{s}.json").read_text(encoding="utf-8"))["targets"]
        H = {}
        for arm in "FG":
            path = MODELS / f"model_split{s}_{arm}.pt"
            if not path.exists():
                raise SystemExit(f"missing model {path}")
            sd = torch.load(path, map_location=a.device)
            model.load_state_dict({k: v.float() for k, v in sd.items()})
            H[arm] = layer_states(model, ids, a.device)
        model.load_state_dict(pre_sd)
        rows = []
        for l in range(H0.shape[0]):
            U = {arm: residual(H[arm][l], H0[l]) for arm in "FG"}
            pU = {arm: power(U[arm]) for arm in "FG"}
            pR = {arm: power(H[arm][l]) for arm in "FG"}
            rows.append({"layer": l, "dpow_change": delta_pow(pU["F"], pU["G"], tj["F"], tj["G"]),
                         "dpow_raw": delta_pow(pR["F"], pR["G"], tj["F"], tj["G"]),
                         "top5_change": {arm: top(pU[arm]) for arm in "FG"},
                         "pretrained_share_change": {arm: float(pU[arm][[k - 1 for k in PRETRAINED_TOP8_IN]].sum() / pU[arm].sum())
                                                     for arm in "FG"}})
        dp_all[s] = [r["dpow_change"] for r in rows]
        out["seeds"][str(s)] = {"targets": tj, "layers": rows}
    out["reading"] = reading(dp_all) if ok else "nicht auswertbar (Tor)"
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for s in SEEDS:
        print(s, "dpow_change per layer:", [None if x is None else round(x, 2) for x in dp_all[s]])
    print("reading:", out["reading"])


if __name__ == "__main__":
    main()
