# LM3 copy (session 56) of the independently written LM1_independent_recompute.py: only paths, STEPS (15 000), the bootstrap
# rng (4021, as registered) and the manifest name changed; seeds and frozen hyperparameters come from LM3_manifest.json.
# Original LM1 docstring follows (its step and seed numbers read as 15 000 and 4010-4019 here).
"""LM1 independent re-computation (read-only; written without reading confirm_lm1.py).

Sources: lab/confirm/LM1_REGISTRATION.md (Fassung 1), lab/confirm/LM1_manifest.json, lab/confirm/lm1_splits/seed*.json,
the trainer lab/experiments/EXP-105-lm-ladder-stage2/lm_stage2.py (what it saves), and the P1 Delta_pow definition
(EXP-103 analyze.delta / EXP-102 analyze.power), re-implemented here.

Rules implemented (registration line numbers):
  L15  seeds 4000-4009, model seed = split seed + 100; F and G per seed.
  L17  Delta_pow (P1) on the 113 number-token rows of the tied embedding at step 6000:
       power_k = (2/P) * sum_dims |DFT_rows(W)_k|^2, k = 1..56;
       Delta = log(S_F(F)/S_F(G)) + log(S_G(G)/S_G(F)), S_arm(T) = sum of power_k over k in target set T.
  L19  gate: held-out fact accuracy (last curve row, column test_fact_acc, step 6000) >= 0.5 in >= 16 of 20 runs,
       else "nicht auswertbar (Budget)".
  L21  H1: mean over all 10 seeds; 95 % percentile bootstrap CI (10 000 draws, rng 4001); one-sided exact sign-
       permutation test of (Delta - 1) with all 2^10 sign vectors; "bestätigt" if CI low > 1 and p < 0.05;
       "unter Mindesteffekt" if CI high < 1 and mirrored p < 0.05; else "unklar".
  L23  binding: trainer hash (manifest), split/test hashes of the seed (manifest + file), model seed, frozen
       hyperparameters, smoke run constants (tokenizer hash, text length, templates), status completed at 6000 steps,
       finite snapshots, text_wraps == 0; F/G configs equal except split_sha256; raw folder holds only the 20
       expected run folders. Error status or violated binding -> "defekt" -> "nicht auswertbar (defekt/fehlt)".
       A run without result.json is "fehlt" (to be restarted before evaluation) -> no reading.

AMBIGUITIES (most literal choice taken):
  A1 L21 bootstrap mechanics not specified: np.random.default_rng(4001), indices rng.integers(0, 10, (10000, 10)),
     percentiles np.percentile(..., [2.5, 97.5]) with default linear interpolation.
  A2 L21 "über 1" / "unter 1" read as strict (low > 1, high < 1); permutation p counts sign vectors with mean >=
     observed (resp. <= for the mirrored test), identity included, p = count / 1024.
  A3 L19 "am Ende" = last curve row (step 6000) of each run; ">= 0.5" inclusive as written.
  A4 L23 missing result.json: registration says restart first; this script therefore gives no reading while any run
     is missing ("unvollständig"); if the analysis were final, the registered label is "nicht auswertbar (defekt/fehlt)".
  A5 L23 "nur die 20 erwarteten Laufordner": expected names rebuilt from the trainer's run-id rule
     (lm2_seed{M}_seed{S}_{F|G}_steps6000_{config hash}); any other entry in lm1_raw (files included) is a violation.
  A6 L23 smoke constants taken from lm1_smoke/*/result.json config (tokenizer_sha256, text_tokens, templates).
  A7 L17/L21 a non-finite or non-positive target power sum makes Delta undefined -> treated as "defekt".
  A8 Order: binding/missing first, then gate, then H1 (L19 says gate failure -> no statement about K2).
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW, SPLITS, SMOKE = HERE / "lm3_raw", HERE / "lm3_splits", HERE / "lm3_smoke"
TRAINER = "lab/experiments/EXP-105-lm-ladder-stage2/lm_stage2.py"
P, STEPS, N_BOOT, BOOT_RNG, THR = 113, 15000, 10_000, 4021, 1.0
GATE_ACC, GATE_MIN = 0.5, 16


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def spectrum(W: np.ndarray) -> np.ndarray:
    """Power per frequency k = 1..(P-1)/2 of the P x d number-token rows (DFT along the token axis)."""
    X = np.fft.fft(W.astype(np.float64), axis=0)
    return 2.0 * (np.abs(X) ** 2).sum(axis=1)[1:(P - 1) // 2 + 1] / P


def delta_pow(pF: np.ndarray, pG: np.ndarray, TF: list[int], TG: list[int]) -> float | None:
    S = lambda pw, T: float(sum(pw[k - 1] for k in T))   # noqa: E731
    a, b, c, d = S(pF, TF), S(pF, TG), S(pG, TG), S(pG, TF)
    if not all(np.isfinite(x) and x > 0 for x in (a, b, c, d)):
        return None
    return float(np.log(a / b) + np.log(c / d))


def expected_cfg(man: dict, smoke: dict, seed: int, arm: str) -> dict:
    fz = man["frozen"]
    cfg = {"seed": seed + man["model_offset"], "split_sha256": man["split_sha256"][f"seed{seed}_{arm}.npy"],
           "test_sha256": man["split_sha256"][f"seed{seed}_test.npy"],
           "steps": fz["steps"], "batch": fz["batch"], "ctx": fz["ctx"], "d": fz["d"], "layers": fz["layers"],
           "heads": fz["heads"], "lr": fz["lr"], "warmup": fz["warmup"], "wd": fz["wd"], "arith_facts": fz["arith_facts"],
           "templates": smoke["templates"], "tokenizer_sha256": smoke["tokenizer_sha256"], "text_tokens": smoke["text_tokens"],
           "script_sha256": man["code_sha256"][TRAINER], "device": fz["device"], "loss": fz["loss"]}
    return cfg


def run_name(cfg: dict, seed: int, arm: str) -> str:
    chash = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:16]
    return f"lm2_seed{cfg['seed']}_seed{seed}_{arm}_steps{cfg['steps']}_{chash}"


def load_run(d: Path, cfg: dict) -> dict:
    """Returns {'state': 'ok'|'fehlt'|'defekt', ...}."""
    if not d.is_dir() or not (d / "result.json").exists():
        return {"state": "fehlt", "why": "no result.json"}
    try:
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
        why = []
        if r.get("status") != "completed":
            why.append(f"status {r.get('status')}")
        if r.get("steps_completed") != STEPS:
            why.append(f"steps_completed {r.get('steps_completed')}")
        rc = r.get("config", {})
        why += [f"config {k}" for k in cfg if rc.get(k) != cfg[k]]
        why += [f"config extra {k}" for k in rc if k not in cfg]
        if r.get("text_wraps") != 0:
            why.append(f"text_wraps {r.get('text_wraps')}")
        cols = r["curve_cols"]
        last = r["curve"][-1]
        if last[0] != STEPS:
            why.append(f"last curve step {last[0]}")
        acc = float(last[cols.index("test_fact_acc")])
        W = np.load(d / "we_snapshots.npy")
        st = [int(x) for x in np.load(d / "we_snapshot_steps.npy")]
        if not np.isfinite(W).all():
            why.append("non-finite snapshots")
        if STEPS not in st:
            why.append(f"no snapshot at {STEPS}")
        if W.ndim != 3 or W.shape[1] != P:
            why.append(f"snapshot shape {W.shape}")
        if why:
            return {"state": "defekt", "why": why}
        return {"state": "ok", "acc": acc, "cfg": rc, "power": spectrum(W[st.index(STEPS)])}
    except Exception as e:                                               # unreadable/corrupt files -> defekt
        return {"state": "defekt", "why": [f"{type(e).__name__}: {e}"]}


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
    eps = 1e-12
    return float((m >= obs - eps).mean()), float((m <= obs + eps).mean())


def main() -> None:
    man = json.loads((HERE / "LM3_manifest.json").read_text(encoding="utf-8"))
    smoke_dirs = sorted(d for d in SMOKE.iterdir() if (d / "result.json").exists())
    smoke = json.loads((smoke_dirs[0] / "result.json").read_text(encoding="utf-8"))["config"]
    problems = []
    if sha(ROOT / TRAINER) != man["code_sha256"][TRAINER]:
        problems.append("trainer file hash differs from manifest")
    seeds, per_seed, runs, expected = man["seeds"], [], {}, set()
    for s in seeds:
        meta_file = SPLITS / f"seed{s}.json"
        for f in (f"seed{s}.json", f"seed{s}_F.npy", f"seed{s}_G.npy", f"seed{s}_test.npy"):
            if sha(SPLITS / f) != man["split_sha256"][f]:
                problems.append(f"split file {f} hash differs from manifest")
        T = json.loads(meta_file.read_text(encoding="utf-8"))["targets"]
        row = {"seed": s}
        for arm in "FG":
            cfg = expected_cfg(man, smoke, s, arm)
            name = run_name(cfg, s, arm)
            expected.add(name)
            runs[(s, arm)] = load_run(RAW / name, cfg)
            ru = runs[(s, arm)]
            row[f"{arm}_state"] = ru["state"]
            if ru["state"] == "ok":
                row[f"{arm}_heldout_acc"] = ru["acc"]
            elif ru["state"] == "defekt":
                row[f"{arm}_why"] = ru["why"]
        rF, rG = runs[(s, "F")], runs[(s, "G")]
        if rF["state"] == "ok" and rG["state"] == "ok":
            diff = [k for k in set(rF["cfg"]) | set(rG["cfg"]) if k != "split_sha256" and rF["cfg"].get(k) != rG["cfg"].get(k)]
            dp = delta_pow(rF["power"], rG["power"], T["F"], T["G"])
            if diff or dp is None:
                row["pair_defekt"] = diff or ["Delta_pow undefined"]
            row["delta_pow"] = dp
        per_seed.append(row)
    extra = sorted(p.name for p in RAW.iterdir() if p.name not in expected) if RAW.exists() else []
    if extra:
        problems.append(f"unexpected entries in lm3_raw: {extra}")

    states = [r["state"] for r in runs.values()]
    n_def = states.count("defekt") + sum("pair_defekt" in r for r in per_seed)
    n_miss = states.count("fehlt")
    accs = [r["acc"] for r in runs.values() if r["state"] == "ok"]
    n_pass = sum(a >= GATE_ACC for a in accs)
    out = {"per_seed": per_seed, "n_runs_ok": states.count("ok"), "n_missing": n_miss, "n_defekt": n_def,
           "missing": [f"{s}{a}" for (s, a), r in runs.items() if r["state"] == "fehlt"],
           "binding_problems": problems, "gate": {"n_acc_ge_0.5": n_pass, "n_known": len(accs), "need": GATE_MIN}}
    if problems or n_def:
        out["reading"] = "nicht auswertbar (defekt/fehlt)"
    elif n_miss:
        out["reading"] = None
        out["status"] = ("unvollständig: fehlende Läufe werden laut L23 vor der Auswertung neu gestartet; "
                         "endgültig fehlend -> 'nicht auswertbar (defekt/fehlt)'")
    elif n_pass < GATE_MIN:
        out["gate"]["passed"] = False
        out["reading"] = "nicht auswertbar (Budget)"
    else:
        out["gate"]["passed"] = True
        x = np.array([r["delta_pow"] for r in per_seed], dtype=np.float64)
        lo, hi = bootstrap_ci(x)
        p_up, p_down = sign_perm(x)
        out.update({"mean_delta_pow": float(x.mean()), "ci95_percentile": [lo, hi], "p_sign_perm_gt1": p_up,
                    "p_sign_perm_lt1_mirrored": p_down, "n_seeds_delta_gt0": int((x > 0).sum())})
        out["reading"] = ("bestätigt" if lo > THR and p_up < 0.05 else
                          "unter Mindesteffekt" if hi < THR and p_down < 0.05 else "unklar")
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
