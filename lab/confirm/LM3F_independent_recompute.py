# LM3-F copy (session 56) of the independently written LM1F_independent_recompute.py: only paths, STEPS (15 000), seeds
# 4010-4019, the rngs (4031, as in confirm_lm3f.py), LM3_summary.json and the output name changed. The LM1 docstring below
# reads with these values; the gate GATE_MIN stays 16 as registered for LM3.
"""LM1-F independent re-computation (read-only; written without reading confirm_lm1f.py).

Sources: lab/confirm/LM1F_REGISTRATION.md (Fassung 1), LM1F_manifest.json, LM1_REGISTRATION.md, LM1_summary.json,
lab/confirm/lm1_splits/seed*.json|*_test.npy, the trainer lab/experiments/EXP-105-lm-ladder-stage2/lm_stage2.py (model class,
tokenizer, T0 prompt, argmax over the 113 number tokens), the spectrum axis of LM1_independent_recompute.py.

Rules implemented (registration line numbers):
  L15  seeds 4000-4009, arms F/G, model seed = seed + 100, checkpoint.pt at the run end (step 6000); no training.
  L17  ablation: rows of the 113 number tokens in the tied embedding, X <- X - B B^T X, B = orthonormal cos/sin columns
       over the number index n (cos(2 pi k n / 113), sin(2 pi k n / 113)) for every k of the set; constant (k = 0)
       untouched; same k as np.fft.fft(W, axis=0)[k] used by spectrum(). Sets: own targets, other split's targets,
       4 control sets (5 frequencies from 1..56 without both target sets, SeedSequence([4011, seed])).
       Accuracy on seed{S}_test.npy: prompt [eot] + T0 up to the answer, argmax over the 113 number tokens at the last
       position (as the trainer's evaluate). C = acc(other) - acc(own); C_bar = mean(C_F, C_G).
  L19  H1F: mean C_bar over 10 seeds > 0.1; 95 % percentile bootstrap (10 000 draws over seeds, rng 4011); one-sided
       exact sign permutation of (C_bar - 0.1) over 2^10 sign vectors; "bestätigt" / "unter Mindesteffekt" / "unklar".
  L21  evaluable only if all 20 runs are complete (result.json + checkpoint.pt), LM1 gate passed (logged held-out acc
       >= 0.5 in >= 16/20) and LM1 accepted the runs (LM1_summary.json: 10 valid seeds, no defect); else
       "nicht auswertbar". L33: checkpoint bound to step 6000 and the run's config hash, else "defekt".
  L23  secondary: acc(base), acc(own), control mean per run; seeds with C_bar > 0; control mean - acc(own);
       control quantity acc(base) - logged held-out accuracy.

AMBIGUITIES (choice taken):
  A1 L17 control draw mechanics: rng = default_rng(SeedSequence([4011, seed])); pool = sorted(1..56 minus F and G
     targets); 4 sets drawn one after another with rng.choice(pool, 5, replace=False) (sets may overlap each other);
     one draw per seed, shared by F and G. The frozen code may draw differently -> control accuracies may differ;
     H1F does not use them.
  A2 L19 bootstrap: default_rng(4011).integers(0, 10, (10000, 10)), np.percentile(..., [2.5, 97.5]) (linear).
  A3 L19 strict ">" / "<" for CI bounds; p = share of the 1024 sign vectors with mean >= observed (mirrored: <=),
     identity included, tolerance 1e-12.
  A4 Evaluation in float32 on the chosen device, batches of 1024 prompts (trainer). The ablation is computed in float64
     and cast back to the embedding dtype.
  A5 With --seeds (subset) no verdict is given ("Teilmenge (Smoke), keine Lesart").
"""
from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW, SPLITS = HERE / "lm3_raw", HERE / "lm3_splits"
TRAINER = ROOT / "lab/experiments/EXP-105-lm-ladder-stage2/lm_stage2.py"
P, STEPS, MODEL_OFFSET = 113, 15000, 100
N_BOOT, BOOT_RNG, THR, CTRL_RNG, N_CTRL = 10_000, 4031, 0.1, 4031, 4
GATE_ACC, GATE_MIN = 0.5, 16
ALL_SEEDS = list(range(4010, 4020))


def load_trainer():
    spec = importlib.util.spec_from_file_location("lm_stage2_for_lm1f", TRAINER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fourier_basis(freqs: list[int]) -> np.ndarray:
    """P x 2|S| orthonormal columns cos/sin(2 pi k n / P) for k in S (k = 1..56, so both columns are non-zero)."""
    n = np.arange(P, dtype=np.float64)
    cols = []
    for k in freqs:
        assert 1 <= k <= (P - 1) // 2, k
        cols += [np.cos(2 * np.pi * k * n / P), np.sin(2 * np.pi * k * n / P)]
    B = np.stack(cols, axis=1)
    B /= np.linalg.norm(B, axis=0, keepdims=True)
    assert np.allclose(B.T @ B, np.eye(B.shape[1]), atol=1e-10), "basis not orthonormal"
    return B


def ablate(W: np.ndarray, freqs: list[int]) -> np.ndarray:
    B = fourier_basis(freqs)
    return W - B @ (B.T @ W)


def control_sets(seed: int, tF: list[int], tG: list[int]) -> list[list[int]]:
    rng = np.random.default_rng(np.random.SeedSequence([CTRL_RNG, seed]))
    pool = np.array([k for k in range(1, (P - 1) // 2 + 1) if k not in set(tF) | set(tG)])
    return [sorted(int(x) for x in rng.choice(pool, 5, replace=False)) for _ in range(N_CTRL)]


def find_run(seed: int, arm: str) -> Path | None:
    hits = sorted(RAW.glob(f"lm2_seed{seed + MODEL_OFFSET}_seed{seed}_{arm}_steps{STEPS}_*"))
    return hits[0] if len(hits) == 1 else None


class Evaluator:
    """Held-out accuracy of one checkpoint under different number-row ablations."""

    def __init__(self, tr, run_dir: Path, test: np.ndarray, dev: torch.device):
        res = json.loads((run_dir / "result.json").read_text(encoding="utf-8"))
        s = torch.load(run_dir / "checkpoint.pt", map_location="cpu", weights_only=False)
        why = []
        if res.get("status") != "completed" or res.get("steps_completed") != STEPS:
            why.append(f"result status {res.get('status')} steps {res.get('steps_completed')}")
        if s.get("step") != STEPS:
            why.append(f"checkpoint step {s.get('step')}")
        if s.get("config_hash") != res.get("config_hash"):
            why.append("checkpoint config hash differs from result.json")
        self.why = why
        cfg = res["config"]
        cols = res["curve_cols"]
        self.logged_acc = float(res["curve"][-1][cols.index("test_fact_acc")])
        from tokenizers import Tokenizer
        tok = Tokenizer.from_file(str(tr.TOK_FILE))
        ids = tr.special_ids(tok)
        self.num = ids["num"]
        state = s["model"]
        vocab = state["emb.weight"].shape[0]
        self.model = tr.GPT(vocab, cfg["ctx"], cfg["d"], cfg["layers"], cfg["heads"])
        self.model.load_state_dict(state)
        self.model.to(dev).eval()
        self.W0 = self.model.emb.weight.detach()[self.num].cpu().double().numpy()
        t0 = tr.template_parts(tok)[0][:3]                               # T0 up to the answer
        a, b = test // P, test % P
        self.x = torch.tensor([[ids["eot"]] + t0[0] + [self.num[i]] + t0[1] + [self.num[j]] + t0[2]
                               for i, j in zip(a, b)], device=dev)
        self.c = torch.from_numpy((a + b) % P).to(dev)
        self.num_t = torch.tensor(self.num, device=dev)

    @torch.no_grad()
    def acc(self, freqs: list[int] | None) -> float:
        emb = self.model.emb.weight
        W = self.W0 if freqs is None else ablate(self.W0, freqs)
        emb[self.num_t] = torch.from_numpy(W).to(emb.dtype).to(emb.device)
        hit = 0
        for i in range(0, len(self.x), 1024):
            out = self.model(self.x[i:i + 1024])[:, -1, self.num_t].argmax(1)
            hit += int((out == self.c[i:i + 1024]).sum().item())
        emb[self.num_t] = torch.from_numpy(self.W0).to(emb.dtype).to(emb.device)   # restore original rows
        return hit / len(self.x)


def bootstrap_ci(x: np.ndarray) -> tuple[float, float]:
    rng = np.random.default_rng(BOOT_RNG)
    means = x[rng.integers(0, len(x), (N_BOOT, len(x)))].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(lo), float(hi)


def sign_perm(x: np.ndarray) -> tuple[float, float]:
    d = x - THR
    obs = d.mean()
    signs = np.array(list(itertools.product((1.0, -1.0), repeat=len(d))))
    m = (signs * d).mean(axis=1)
    return float((m >= obs - 1e-12).mean()), float((m <= obs + 1e-12).mean())


def h1f(cbar: np.ndarray) -> dict:
    lo, hi = bootstrap_ci(cbar)
    p_up, p_down = sign_perm(cbar)
    verdict = ("bestätigt" if lo > THR and p_up < 0.05 else
               "unter Mindesteffekt" if hi < THR and p_down < 0.05 else "unklar")
    return {"n_seeds": int(len(cbar)), "mean_cbar": float(cbar.mean()), "ci95_percentile": [lo, hi],
            "p_sign_perm_gt_0.1": p_up, "p_sign_perm_lt_0.1_mirrored": p_down,
            "n_seeds_cbar_gt0": int((cbar > 0).sum()), "verdict": verdict}


def evaluate_run(tr, seed: int, arm: str, T: dict, ctrls: list[list[int]], test: np.ndarray, dev) -> dict:
    t0 = time.perf_counter()
    d = find_run(seed, arm)
    if d is None or not (d / "result.json").exists() or not (d / "checkpoint.pt").exists():
        return {"seed": seed, "arm": arm, "state": "fehlt"}
    ev = Evaluator(tr, d, test, dev)
    if ev.why:
        return {"seed": seed, "arm": arm, "state": "defekt", "why": ev.why, "run": d.name}
    other = "G" if arm == "F" else "F"
    r = {"seed": seed, "arm": arm, "state": "ok", "run": d.name, "n_test": int(len(test)),
         "acc_logged": ev.logged_acc, "acc_base": ev.acc(None), "acc_own": ev.acc(T[arm]), "acc_other": ev.acc(T[other]),
         "acc_controls": [ev.acc(c) for c in ctrls], "controls": ctrls}
    r["C"] = r["acc_other"] - r["acc_own"]
    r["control_mean"] = float(np.mean(r["acc_controls"]))
    r["control_mean_minus_own"] = r["control_mean"] - r["acc_own"]
    r["base_minus_logged"] = r["acc_base"] - r["acc_logged"]
    r["seconds"] = time.perf_counter() - t0
    return r


def lm1_acceptance() -> list[str]:
    p = HERE / "LM3_summary.json"
    if not p.exists():
        return ["LM1_summary.json missing"]
    s = json.loads(p.read_text(encoding="utf-8"))
    probs = []
    if s.get("n_valid") != 10 or s.get("defect"):
        probs.append(f"LM1 n_valid {s.get('n_valid')} defect {s.get('defect')}")
    return probs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--seeds", type=int, nargs="*")
    ap.add_argument("--out", default=str(HERE / "LM3F_independent_summary.json"))
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    dev = torch.device(a.device)
    seeds = a.seeds or ALL_SEEDS
    tr = load_trainer()
    runs, per_seed = [], []
    for s in seeds:
        T = json.loads((SPLITS / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        test = np.load(SPLITS / f"seed{s}_test.npy").astype(np.int64)
        ctrls = control_sets(s, T["F"], T["G"])
        row = {"seed": s, "targets": T, "controls": ctrls}
        cs = []
        for arm in "FG":
            try:
                r = evaluate_run(tr, s, arm, T, ctrls, test, dev)
            except Exception as e:                                       # per-run failure -> defekt, summary still written
                r = {"seed": s, "arm": arm, "state": "defekt", "why": [f"{type(e).__name__}: {e}"]}
            runs.append(r)
            print(json.dumps(r, ensure_ascii=False), flush=True)
            if r["state"] == "ok":
                cs.append(r["C"])
        row["C_bar"] = float(np.mean(cs)) if len(cs) == 2 else None
        per_seed.append(row)
    ok = [r for r in runs if r["state"] == "ok"]
    gate_n = sum(r["acc_logged"] >= GATE_ACC for r in ok)
    problems = lm1_acceptance()
    out = {"block": "LM3F (independent)", "seeds": seeds, "runs": runs, "per_seed": per_seed,
           "gate_n_logged_acc_ge_0.5": int(gate_n), "lm1_acceptance_problems": problems}
    if a.seeds and sorted(seeds) != ALL_SEEDS:
        out["H1F"] = {"verdict": None, "note": "Teilmenge (Smoke), keine Lesart"}
    elif len(ok) != 20 or problems or gate_n < GATE_MIN:
        out["H1F"] = {"verdict": "nicht auswertbar", "n_runs_ok": len(ok), "gate": int(gate_n)}
    else:
        out["H1F"] = h1f(np.array([r["C_bar"] for r in per_seed], dtype=np.float64))
    Path(a.out).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"H1F": out["H1F"]}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
