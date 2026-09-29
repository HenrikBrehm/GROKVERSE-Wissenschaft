"""EXP-112 analysis (exploration; session 48, written before any EXP-112 run; readings also in README).
Measure as EXP-102 analyze.py: Delta_pow from W_E[:p] (number tokens), same power, bootstrap 10 000 (rng 112).
Primary step 5000, descriptive 2000. Per rung: mean, 95 % CI over seeds, n positive; generalized runs (events).
Readings per rung r in (lmB, lmnbB) at step 5000, reference r0B (same batch 256, same seeds):
  'bricht'      CI upper bound < 0.5 * mean Delta_pow(r0B)
  'schwaecher'  paired CI of Delta(r) - Delta(r0B) < 0, but not 'bricht'
  'haelt'       CI lower bound > 0 (and neither of the above)
  else 'unklar'
Stage-1 ladder result (rule 20e): K2 'haelt im LM-Format unter Minibatch', if lmB 'haelt' (not weaker); the answer to
'does next-token loss without the b target cost steering under minibatch' is the lmnbB reading.
Descriptive: r0B against the full-batch r0 of EXP-102 at step 2000 (paired by seed).
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-112-lm-ladder-minibatch/analyze.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "EXP-102-lm-ladder-stage1"
sys.path.insert(0, str(SRC))
import analyze as A  # noqa: E402

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp112_design", HERE / "design.py")   # not 'design': A cached EXP-102's
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)
assert D.REL.endswith("EXP-112-lm-ladder-minibatch")

FLAGS = {"r0B": "op0_fs0_tie0_lossanswer", "lmB": "op1_fs1_tie1_lossanswer", "lmnbB": "op1_fs1_tie1_lossall_but_b"}
STEPS = (2000, 5000)


def load(seed: int, split: str, rung: str) -> dict | str:
    d = HERE / "raw" / f"lad_seed{seed}_seed{seed}_{split}_{FLAGS[rung]}_B{D.BATCH}_steps{D.STEPS}_thr1_cuda"
    if not (d / "result.json").exists():
        return "fehlt"
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    sp = SRC / "splits" / f"seed{seed}_{split}.npy"
    if (r.get("status") != "completed" or r.get("steps_completed") != D.STEPS or r.get("batch_size") != D.BATCH
            or r.get("split_sha256") != hashlib.sha256(sp.read_bytes()).hexdigest()):
        return "defekt"
    W, S = np.load(d / "we_snapshots.npy"), [int(x) for x in np.load(d / "we_snapshot_steps.npy")]
    if not np.isfinite(W).all() or any(t not in S for t in STEPS):
        return "defekt"
    return {"P": {t: A.power(W[S.index(t)]) for t in STEPS}, "gen": r["events"].get("generalization_step")}


def boot(x: np.ndarray, rng: np.random.Generator) -> list[float]:
    m = x[rng.integers(0, len(x), (A.BOOT, len(x)))].mean(1)
    return [float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))]


def main() -> None:
    rng = np.random.default_rng(112)
    dp = {r: {t: {} for t in STEPS} for r in FLAGS}
    gen, bad = {r: [] for r in FLAGS}, []
    for s in D.SEEDS:
        T = json.loads((SRC / "splits" / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        for r in FLAGS:
            x = {sp: load(s, sp, r) for sp in "FG"}
            if any(isinstance(v, str) for v in x.values()):
                bad.append([s, r, [v if isinstance(v, str) else "ok" for v in x.values()]])
                continue
            gen[r] += [x[sp]["gen"] for sp in "FG"]
            for t in STEPS:
                v = A.delta_pow(x["F"]["P"][t], x["G"]["P"][t], T["F"], T["G"])
                if v is None:
                    bad.append([s, r, f"delta_pow undefined at {t}"])
                else:
                    dp[r][t][s] = v
    out: dict = {"n_bad": len(bad), "bad": bad, "rungs": {}}
    ref = dp["r0B"][5000]
    for r in FLAGS:
        row: dict = {"generalized": sum(g is not None for g in gen[r]), "runs": len(gen[r]),
                     "gen_median": float(np.median([g for g in gen[r] if g is not None])) if any(g is not None for g in gen[r]) else None}
        for t in STEPS:
            v = np.array(list(dp[r][t].values()))
            if len(v) >= 2:
                row[str(t)] = {"n": len(v), "mean": float(v.mean()), "ci95": boot(v, rng), "n_pos": int((v > 0).sum())}
        if r != "r0B" and "5000" in row and len(ref) >= 2:
            common = sorted(set(dp[r][5000]) & set(ref))
            d = np.array([dp[r][5000][s] - ref[s] for s in common])
            c = boot(d, rng)
            row["diff_vs_r0B_5000"] = {"n": len(d), "mean": float(d.mean()), "ci95": c}
            ci = row["5000"]["ci95"]
            row["reading"] = ("bricht" if ci[1] < 0.5 * np.mean(list(ref.values())) else "schwaecher" if c[1] < 0
                              else "haelt" if ci[0] > 0 else "unklar")
        out["rungs"][r] = row
    fb = {}
    for s in D.SEEDS:
        pF, pG = A.load_power(s, "F", "r0"), A.load_power(s, "G", "r0")
        if s in dp["r0B"][2000] and not isinstance(pF, str) and not isinstance(pG, str):
            T = json.loads((SRC / "splits" / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
            fb[s] = dp["r0B"][2000][s] - A.delta_pow(pF, pG, T["F"], T["G"])
    if len(fb) >= 2:
        v = np.array(list(fb.values()))
        out["r0B_minus_fullbatch_r0_at_2000"] = {"n": len(v), "mean": float(v.mean()), "ci95": boot(v, rng)}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
