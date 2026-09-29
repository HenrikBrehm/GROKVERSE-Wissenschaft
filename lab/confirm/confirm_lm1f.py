"""LM1-F (session 51): functional add-on to the frozen block LM1 (registration LM1F_REGISTRATION.md). Ablates, from the 113
number-token rows of the tied embedding of each completed LM1 model (step 6000, checkpoint.pt), the Fourier subspace of (a) the
run's own targets, (b) the other split's targets, (c) 4 control sets; measures held-out fact accuracy on the seed's common test
set (prompt T0, argmax over the number tokens, as lm_stage2.evaluate). No training.
Per run C = acc(other) - acc(own); per seed Cbar = mean of F and G.
H1F: mean Cbar over the 10 seeds > 0.1: 'bestaetigt' if the lower bound of the 95 % percentile bootstrap CI (10 000 draws,
default_rng(4011), resampling seeds) is > 0.1 AND the exact one-sided sign-permutation test of (Cbar - 0.1) over all 2^10 sign
vectors gives p < 0.05; 'unter Mindesteffekt' if the upper CI bound is < 0.1 and the mirrored test gives p < 0.05; else
'unklar'. Evaluated only if LM1 itself is evaluable (its gate: held-out >= 0.5 in >= 16/20 runs) and all 20 runs are complete;
otherwise 'nicht auswertbar'. Secondary (descriptive): per run acc(base), acc(own), mean acc(controls); number of seeds with
Cbar > 0.
  python lab/tools/guarded_run.py -- C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe \
      lab/confirm/confirm_lm1f.py [--selftest]
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
SPL, RAW = HERE / "lm1_splits", HERE / "lm1_raw"
SEEDS, MODEL_OFFSET, STEPS, P = range(4000, 4010), 100, 6000, 113
MIN_EFFECT, GATE_ACC, GATE_N = 0.1, 0.5, 16


def projector(S: list[int]) -> np.ndarray:
    n = np.arange(P)
    B = np.stack([f(2 * np.pi * k * n / P) for k in S for f in (np.cos, np.sin)], 1)
    Q, _ = np.linalg.qr(B)
    return Q @ Q.T


def controls(seed: int, T: dict) -> list[list[int]]:
    rng = np.random.default_rng(np.random.SeedSequence([4011, seed]))
    free = [k for k in range(1, 57) if k not in T["F"] and k not in T["G"]]
    return [sorted(rng.choice(free, 5, replace=False).tolist()) for _ in range(4)]


def test_h1(cbar: np.ndarray) -> dict:
    rng = np.random.default_rng(4011)
    boot = cbar[rng.integers(0, len(cbar), (10_000, len(cbar)))].mean(1)
    lo, hi = (float(x) for x in np.percentile(boot, [2.5, 97.5]))
    d = cbar - MIN_EFFECT
    signs = np.array(list(itertools.product([1, -1], repeat=len(d))))
    means = (signs * np.abs(d)).mean(1)
    p_up = float((means >= d.mean() - 1e-12).mean())
    p_down = float((means <= d.mean() + 1e-12).mean())
    reading = ("bestaetigt" if lo > MIN_EFFECT and p_up < 0.05 else
               "unter Mindesteffekt" if hi < MIN_EFFECT and p_down < 0.05 else "unklar")
    return {"mean": float(cbar.mean()), "ci95": [lo, hi], "p_one_sided": p_up, "p_mirrored": p_down, "reading": reading}


def evaluate_run(L, tok, ids, t0, d: Path, test: np.ndarray, sets: dict) -> dict:
    import torch
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    assert res["status"] == "completed" and res["steps_completed"] == STEPS, d
    k = res["config"]
    model = L.GPT(tok.get_vocab_size(), k["ctx"], k["d"], k["layers"], k["heads"])
    model.load_state_dict(torch.load(d / "checkpoint.pt", map_location="cpu", weights_only=False)["model"])
    model.eval()
    num = torch.tensor(ids["num"])
    X0 = model.emb.weight.data[num].clone()
    a, b = test // P, test % P
    x = torch.tensor([[ids["eot"]] + t0[0] + [ids["num"][i]] + t0[1] + [ids["num"][j]] + t0[2] for i, j in zip(a, b)])
    c = torch.from_numpy((a + b) % P)
    out = {"test_acc_logged": res["curve"][-1][2]}
    with torch.no_grad():
        for name, S in sets.items():
            model.emb.weight.data[num] = X0 if S is None else X0 - torch.tensor(projector(S), dtype=torch.float32) @ X0
            pred = torch.cat([model(x[i:i + 512])[:, -1, num].argmax(1) for i in range(0, len(x), 512)])
            out[name] = float((pred == c).float().mean())
    return out


def main() -> None:
    import torch
    torch.set_num_threads(4)
    sys.path.insert(0, str(LAB / "experiments/EXP-105-lm-ladder-stage2"))
    import lm_stage2 as L
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(L.TOK_FILE))
    ids = L.special_ids(tok)
    t0 = L.tmpl_prompt(L.template_parts(tok)[0])
    rows, missing = [], []
    for s in SEEDS:
        T = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        test = np.load(SPL / f"seed{s}_test.npy").astype(np.int64)
        ctl = controls(s, T)
        for arm in "FG":
            ds = list(RAW.glob(f"lm2_seed{s + MODEL_OFFSET}_seed{s}_{arm}_steps{STEPS}_*"))
            if len(ds) != 1 or not (ds[0] / "result.json").exists() or not (ds[0] / "checkpoint.pt").exists():
                missing.append(f"{s}{arm}")
                continue
            other = T["G" if arm == "F" else "F"]
            sets = {"base": None, "own": T[arm], "other": other, **{f"ctl{i}": S for i, S in enumerate(ctl)}}
            r = {"seed": s, "arm": arm, **evaluate_run(L, tok, ids, t0, ds[0], test, sets)}
            r["C"] = r["other"] - r["own"]
            r["ctl_mean"] = float(np.mean([r[f"ctl{i}"] for i in range(4)]))
            rows.append(r)
            print(json.dumps(r), flush=True)
    out = {"rows": rows, "missing": missing}
    gate = sum(r["test_acc_logged"] >= GATE_ACC for r in rows)
    if missing or gate < GATE_N:
        out["reading"] = "nicht auswertbar" + (" (fehlt)" if missing else " (LM1-Tor)")
    else:
        cbar = np.array([np.mean([r["C"] for r in rows if r["seed"] == s]) for s in SEEDS])
        out.update({"cbar": cbar.tolist(), "n_seeds_cbar_pos": int((cbar > 0).sum()), **test_h1(cbar)})
    (HERE / "LM1F_summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    """Statistics only (no models): ten values 0.9 -> bestaetigt, p = 1/1024; values around 0.1 -> unklar; projector idempotent."""
    r = test_h1(np.full(10, 0.9))
    assert r["reading"] == "bestaetigt" and abs(r["p_one_sided"] - 1 / 1024) < 1e-12, r
    r = test_h1(np.array([0.05, 0.15] * 5))
    assert r["reading"] == "unklar", r
    r = test_h1(np.full(10, -0.2))
    assert r["reading"] == "unter Mindesteffekt", r
    Pm = projector([3, 7])
    assert np.allclose(Pm @ Pm, Pm) and abs(np.trace(Pm) - 4) < 1e-9
    T = {"F": [1, 2, 3, 4, 5], "G": [6, 7, 8, 9, 10]}
    c = controls(4000, T)
    assert all(not set(S) & set(T["F"] + T["G"]) for S in c) and c == controls(4000, T)
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
