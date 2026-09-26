"""EXP-022 (design after Nachtrag a): can a single-frequency split force a single-frequency solution? (UNTESTED on real runs)

All arms (S1, D1, S5) run exactly STEPS = 6000 steps and save model_final.pt. Measures at step 6000:
  K_func  = study rule 'nanda' (Fourier norm of W_L = W_out @ W_U over neurons, threshold 0.25 of max) on the saved model
  acc     = train acc, test acc on T*; keep_f1 = T* acc with W_E[:p] projected onto {DC, f1}; drop_f1 = T* acc without f1
  n_eff   = participation ratio of the W_E power spectrum at step 6000 (descriptive only)
Joint success of a seed ("Ein-Frequenz-Lösung"): K_func(S1) == {f1}, train acc >= 0.99, T* acc >= 0.95, keep_f1 >= 0.90.
Primary (README Nachtrag a): count of seeds with joint success in S1, and |K_func(S1)| < |K_func(D1)| paired.
Runs carry exp_id EXP-018 by the trainer's naming (--split-file + --test-file). Inference only; run via guarded_run.py.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB.parent / "training"))
sys.path.insert(0, str(LAB / "experiments/EXP-001-freq-ban"))
import freq_ban as fb  # noqa: E402
from grokverse.analysis.key_frequencies import neuron_logit_map, select_from_arrays  # noqa: E402
from grokverse.config import get_config  # noqa: E402
from grokverse.data import make_dataset, split_hash  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.train import evaluate  # noqa: E402

SEEDS, ARMS, STEPS, P = range(40, 45), ("S1", "D1", "S5"), 6000, 113
B = fb.fourier_basis(P)


def protocol_error(res: dict, s: int, d: Path) -> str | None:
    want = {"exp_id": "EXP-018", "condition": "baseline", "seed": s, "max_steps": STEPS,
            "stop_after_generalization": 8000, "steps_completed": STEPS, "status": "completed"}
    for k, v in want.items():
        if res.get(k) != v:
            return f"{k}={res.get(k)!r}, expected {v!r}"
    if res["config"].get("eval_every_test") != 25:
        return "eval cadence"
    if int(np.load(d / "spectra_steps.npy")[-1]) != STEPS:
        return "last spectrum not at step 6000"
    if not (d / "model_final.pt").exists():
        return "model_final.pt missing"
    return None


def measure(s: int, arm: str, f1: int) -> tuple[dict | None, str | None]:
    d = HERE / f"raw/EXP-018_baseline_seed{s}_thr4_seed{s}_train_{arm}"
    if not (d / "result.json").exists():
        return None, "missing"
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    err = protocol_error(res, s, d)
    if err:
        return None, err
    tr, te = np.load(HERE / f"splits/seed{s}_train_{arm}.npy"), np.load(HERE / f"splits/seed{s}_test.npy")
    if res["split_hash"] != split_hash(tr) or res.get("test_hash") != split_hash(te):
        return None, "hash"
    cfg = get_config("arch25k", seed=s)
    model = build_model(cfg)
    state = torch.load(d / "model_final.pt", map_location="cpu")
    model.load_state_dict(state)
    data = make_dataset(cfg)
    X, Y = data["all_x"], data["all_y"]
    tr_t, te_t = torch.from_numpy(tr.astype(np.int64)), torch.from_numpy(te.astype(np.int64))
    acc_tr = evaluate(model, X[tr_t], Y[tr_t], P)[1]
    acc_te = evaluate(model, X[te_t], Y[te_t], P)[1]
    W0 = model.W_E.detach().clone()

    def test_acc_with(proj: np.ndarray) -> float:
        with torch.no_grad():
            model.W_E[:P] = torch.tensor(proj, dtype=W0.dtype) @ W0[:P]
        a = evaluate(model, X[te_t], Y[te_t], P)[1]
        with torch.no_grad():
            model.W_E.copy_(W0)
        return a

    keep = B[:, [0, *fb.freq_columns([f1])]]
    keep_f1 = test_acc_with(keep @ keep.T)
    drop_f1 = test_acc_with(fb.ban_projector(B, [f1]))
    st = {k: v.numpy() for k, v in state.items()}
    kf = select_from_arrays("nanda", P, W_L=neuron_logit_map(st, cfg))["key_frequencies"]
    pw = np.load(d / "spectra.npy")[-1]
    return {"K_func": [int(k) for k in kf], "n_func": len(kf), "acc_train": acc_tr, "acc_test": acc_te,
            "keep_f1_test_acc": keep_f1, "drop_f1_test_acc": drop_f1,
            "n_eff_WE": float(pw.sum() ** 2 / (pw ** 2).sum()), "WE_top1": int(np.argmax(pw)) + 1}, None


def main() -> None:
    rows = []
    for s in SEEDS:
        f1 = json.loads((HERE / f"splits/seed{s}.json").read_text(encoding="utf-8"))["f1"]
        r: dict = {"seed": s, "f1": f1}
        for arm in ARMS:
            x, err = measure(s, arm, f1)
            if err:
                r["reason"] = f"{arm}: {err}"
                break
            r[arm] = x
        r["valid"] = "reason" not in r
        if r["valid"]:
            a = r["S1"]
            r["joint_success_S1"] = (a["K_func"] == [f1] and a["acc_train"] >= 0.99 and a["acc_test"] >= 0.95
                                     and a["keep_f1_test_acc"] >= 0.90)
            r["D1_single"] = r["D1"]["n_func"] == 1
            r["S1_fewer_than_D1"] = a["n_func"] < r["D1"]["n_func"]
            r["S1_within1_of_S5"] = abs(a["n_func"] - r["S5"]["n_func"]) <= 1
        rows.append(r)
    valid = [r for r in rows if r["valid"]]
    out: dict = {"rows": rows, "n_valid": len(valid)}
    if len(valid) < 4:
        out["verdict"] = "nicht auswertbar"
    else:
        js = sum(r["joint_success_S1"] for r in valid)
        fewer = sum(r["S1_fewer_than_D1"] for r in valid)
        d1s = sum(r["D1_single"] for r in valid)
        out.update({"joint_success_S1": js, "S1_fewer_than_D1": fewer, "D1_single": d1s,
                    "p_sign_fewer": sum(math.comb(len(valid), j) for j in range(fewer, len(valid) + 1)) / 2 ** len(valid),
                    "S1_within1_of_S5": sum(r["S1_within1_of_S5"] for r in valid)})
        if js >= 4 and d1s == 0 and fewer == len(valid):
            out["verdict"] = "erzwingbar"
        elif fewer == len(valid):
            out["verdict"] = "teilweise (weniger Frequenzen, aber keine vollständige Ein-Frequenz-Lösung)"
        else:
            out["verdict"] = "nicht erzwingbar"
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
