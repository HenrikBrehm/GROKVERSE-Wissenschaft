"""EXP-112 check '10k' (session 48, written before the runs): is 'lmnbB schwaecher' only a delay? Rungs r0B and lmnbB,
B 256, seeds 3800-3809, F/G, 10 000 steps (raw_10k). Readings at 10 000 (bootstrap 10 000, rng 1121):
  'nur verzoegert'   >= 16/20 lmnbB runs generalized and paired CI of lmnbB - r0B contains 0 or lies above 0
  'bleibt schwaecher' paired CI upper bound < 0
  else 'unklar'
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-112-lm-ladder-minibatch/analyze_10k.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "EXP-102-lm-ladder-stage1"
sys.path.insert(0, str(SRC))
import analyze as A  # noqa: E402

FLAGS = {"r0B": "op0_fs0_tie0_lossanswer", "lmnbB": "op1_fs1_tie1_lossall_but_b"}
STEPS, SEEDS = 10000, range(3800, 3810)


def load(s: int, x: str, rung: str) -> tuple[dict, int | None]:
    d = HERE / "raw_10k" / f"lad_seed{s}_seed{s}_{x}_{FLAGS[rung]}_B256_steps{STEPS}_thr1_cuda"
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    assert r["status"] == "completed" and r["steps_completed"] == STEPS and r["batch_size"] == 256, d
    W, S = np.load(d / "we_snapshots.npy"), [int(v) for v in np.load(d / "we_snapshot_steps.npy")]
    assert np.isfinite(W).all(), d
    return {t: A.power(W[S.index(t)]) for t in (5000, 10000)}, r["events"].get("generalization_step")


def main() -> None:
    rng, D, gen = np.random.default_rng(1121), {r: {5000: [], 10000: []} for r in FLAGS}, {r: [] for r in FLAGS}
    for s in SEEDS:
        T = json.loads((SRC / "splits" / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        for r in FLAGS:
            (pF, gF), (pG, gG) = load(s, "F", r), load(s, "G", r)
            gen[r] += [gF, gG]
            for t in (5000, 10000):
                D[r][t].append(A.delta_pow(pF[t], pG[t], T["F"], T["G"]))
    ci = lambda v: [float(np.quantile(m, q)) for m in [v[rng.integers(0, len(v), (A.BOOT, len(v)))].mean(1)] for q in (0.025, 0.975)]   # noqa: E731
    out = {r: {"generalized": sum(g is not None for g in gen[r]), **{str(t): {"mean": float(np.mean(D[r][t])), "ci95": ci(np.array(D[r][t]))}
                                                                    for t in (5000, 10000)}} for r in FLAGS}
    d = np.array(D["lmnbB"][10000]) - np.array(D["r0B"][10000])
    c = ci(d)
    out["lmnbB_minus_r0B_10k"] = {"mean": float(d.mean()), "ci95": c, "n_neg": int((d < 0).sum())}
    out["reading"] = ("bleibt schwaecher" if c[1] < 0 else "nur verzoegert" if out["lmnbB"]["generalized"] >= 16 else "unklar")
    (HERE / "summary_10k.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
