"""LM1 confirmation block (session 50): does the choice of arithmetic facts steer the number-token embeddings of a small LM
trained from scratch, when the facts are learned? Registration: lab/confirm/LM1_REGISTRATION.md (readings fixed there and here).

Setup (frozen): lm_stage2.py (EXP-105, TinyStories + arithmetic sentences, 14 M parameters, tied embeddings), 19 arithmetic
sentences per sequence (about 79 % arithmetic tokens), loss on text and answer tokens only (--loss answer), 6000 steps, GPU.
Fresh split seeds 4000-4009 (engineered F/G pair + held-out test set from EXP-102 design.build, i.e. the P1/EXP-053 construction);
model seed = split seed + 100 (F and G of a seed share init, text, templates and insert positions; only the facts differ).

  python lab/confirm/confirm_lm1.py --build       # splits and test sets -> lab/confirm/lm1_splits (never overwrites)
  python lab/confirm/confirm_lm1.py --jobs        # job lines for the GPU daemon (stdout)
  python lab/confirm/confirm_lm1.py --manifest    # code hashes -> LM1_manifest.json (needs --commit)
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/confirm/confirm_lm1.py --analyze

Analysis (frozen, run only after all 20 runs finished):
  binding  every run's result.json must carry the manifest's lm_stage2.py sha256, the split and test sha256 of its seed, the
           frozen hyperparameters, status 'completed' and 6000 steps; W_E snapshots finite. A run failing this is 'defekt'.
  gate     held-out fact accuracy >= 0.5 at the end in >= 16 of 20 runs, else 'nicht auswertbar (Budget)'.
  H1       Delta_pow (P1 definition on the 113 number-token rows) at step 6000, mean over the 10 seeds;
           95 % percentile bootstrap CI (10 000 resamples, rng 4001) and one-sided sign-flip permutation p (exact, 2^10).
           'bestaetigt' if CI lower bound > 1 (registered minimum effect, as P1) and p < 0.05;
           'widerlegt (bricht)' if CI upper bound < 1; else 'unklar'. Family = {H1} (Holm trivial).
  secondary (descriptive, no verdict): held-out accuracy per run, seeds with Delta_pow > 0, per pair s_learn / s_steer
           (H-folgt of EXP-113: first snapshot with train facts >= 0.1 in F and G vs first snapshot with Delta_pow > 1).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
sys.path.insert(0, str(LAB / "experiments/EXP-105-lm-ladder-stage2"))
import analyze_pilot as AP  # noqa: E402  (loader: completed, steps, finite snapshots; Delta_pow via EXP-102 analyze)
sys.path.insert(0, str(LAB / "experiments/EXP-102-lm-ladder-stage1"))
import analyze as A  # noqa: E402
import design  # noqa: E402

SEEDS = tuple(range(4000, 4010))
MODEL_OFFSET, K, STEPS, LOSS = 100, 19, 6000, "answer"
SPL, RAW = HERE / "lm1_splits", HERE / "lm1_raw"
TRAINER = LAB / "experiments/EXP-105-lm-ladder-stage2/lm_stage2.py"
CODE = [TRAINER, LAB / "experiments/EXP-105-lm-ladder-stage2/analyze_pilot.py", LAB / "experiments/EXP-102-lm-ladder-stage1/analyze.py",
        LAB / "experiments/EXP-102-lm-ladder-stage1/design.py", LAB / "experiments/EXP-053-p3-overlap-design/overlap_split.py",
        Path(__file__).resolve()]
FROZEN = {"steps": STEPS, "batch": 32, "ctx": 256, "d": 384, "layers": 6, "heads": 6, "lr": 6e-4, "warmup": 500, "wd": 0.1,
          "arith_facts": K, "device": "cuda", "loss": LOSS}
MIN_EFFECT, GATE_ACC, GATE_N = 1.0, 0.5, 16
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rel(p: Path) -> str:
    return p.resolve().relative_to(LAB.parent).as_posix()


def build() -> None:
    SPL.mkdir(exist_ok=True)
    import overlap_split as ov  # noqa: E402  (on the path via design)
    for s in SEEDS:
        d, (F, G) = design.build(s), ov.targets(s)
        for arm, key in (("F", "A"), ("G", "B"), ("test", "test")):
            with open(SPL / f"seed{s}_{arm}.npy", "xb") as f:
                np.save(f, np.asarray(d[key]).astype(np.int64))
        assert not np.intersect1d(d["A"], d["test"]).size and not np.intersect1d(d["B"], d["test"]).size
        with open(SPL / f"seed{s}.json", "x", encoding="utf-8") as f:
            json.dump({"seed": s, "targets": {"F": F, "G": G}}, f, indent=1)
    print(f"[lm1] wrote splits for {len(SEEDS)} seeds")


def jobs() -> list[str]:
    return [f"{PY} {rel(TRAINER)} --seed {s + MODEL_OFFSET} --split-file {rel(SPL)}/seed{s}_{x}.npy --test-file {rel(SPL)}/seed{s}_test.npy "
            f"--steps {STEPS} --arith-facts {K} --loss {LOSS} --device cuda --out-root {rel(RAW)}" for s in SEEDS for x in "FG"]


def manifest(commit: str) -> None:
    m = {"block": "LM1", "commit": commit, "seeds": list(SEEDS), "model_offset": MODEL_OFFSET, "frozen": FROZEN, "loss": LOSS,
         "registration": ["lab/confirm/LM1_REGISTRATION.md"], "code_sha256": {rel(p): sha(p) for p in CODE},
         "split_sha256": {f.name: sha(f) for f in sorted(SPL.glob("seed*.npy"))}}
    with open(HERE / "LM1_manifest.json", "x", encoding="utf-8") as f:
        json.dump(m, f, indent=1)
    print("[lm1] manifest written")


def check_binding(m: dict, r: dict, s: int, arm: str) -> list[str]:
    c, bad = r["config"], []
    if c["script_sha256"] != m["code_sha256"][rel(TRAINER)]:
        bad.append("trainer hash")
    if c["split_sha256"] != m["split_sha256"][f"seed{s}_{arm}.npy"] or c["test_sha256"] != m["split_sha256"][f"seed{s}_test.npy"]:
        bad.append("split/test hash")
    if c["seed"] != s + MODEL_OFFSET:
        bad.append("model seed")
    bad += [f"config {k}" for k, v in FROZEN.items() if c.get(k) != v]
    if r.get("text_wraps", 0):
        bad.append("text wrapped")
    return bad


def perm_p(x: np.ndarray, mu: float) -> float:
    d = x - mu
    n = len(d)
    signs = ((np.arange(2 ** n)[:, None] >> np.arange(n)) & 1) * 2 - 1
    return float(((signs * np.abs(d)).mean(1) >= d.mean() - 1e-12).mean())


def analyze() -> None:
    m = json.loads((HERE / "LM1_manifest.json").read_text(encoding="utf-8"))
    for p in CODE:
        assert sha(p) == m["code_sha256"][rel(p)], f"code changed since the freeze: {rel(p)}"
    rows, defect, accs = [], [], []
    for s in SEEDS:
        try:
            rF, rG = AP.load(RAW, s + MODEL_OFFSET, SPL / f"seed{s}_F.npy"), AP.load(RAW, s + MODEL_OFFSET, SPL / f"seed{s}_G.npy")
        except (AssertionError, FileNotFoundError, KeyError) as e:
            defect.append({"seed": s, "why": f"missing or incomplete: {e!r}"})
            continue
        bad = check_binding(m, rF["res"], s, "F") + check_binding(m, rG["res"], s, "G")
        if bad:
            defect.append({"seed": s, "why": bad})
            continue
        TF, TG = AP.targets(SPL / f"seed{s}_F.npy"), AP.targets(SPL / f"seed{s}_G.npy")
        steps = [x for x in rF["steps"] if x in rG["P"]]
        assert steps[-1] == STEPS
        dp = {x: A.delta_pow(rF["P"][x], rG["P"][x], TF, TG) for x in steps}
        trF = {int(c[0]): c[1] for c in rF["res"]["curve"]}
        trG = {int(c[0]): c[1] for c in rG["res"]["curve"]}
        s_learn = next((x for x in steps if trF.get(x, 0) >= 0.1 and trG.get(x, 0) >= 0.1), None)
        s_steer = next((x for x in steps if dp[x] > MIN_EFFECT), None)
        acc = [rF["res"]["curve"][-1][2], rG["res"]["curve"][-1][2]]
        accs += acc
        rows.append({"seed": s, "dpow_end": dp[STEPS], "test_acc": acc, "s_learn": s_learn, "s_steer": s_steer,
                     "gen": [rF["res"]["events"].get("generalization_step"), rG["res"]["events"].get("generalization_step")]})
    out: dict = {"block": "LM1", "manifest_commit": m["commit"], "n_valid": len(rows), "defect": defect, "rows": rows}
    if defect or len(rows) < len(SEEDS):
        out["verdict"] = "nicht auswertbar (defekt/fehlt)"
    elif sum(a >= GATE_ACC for a in accs) < GATE_N:
        out["verdict"] = "nicht auswertbar (Budget)"
    else:
        x = np.array([r["dpow_end"] for r in rows])
        rng = np.random.default_rng(4001)
        bm = rng.choice(x, (10000, len(x)), replace=True).mean(1)
        lo, hi = float(np.quantile(bm, 0.025)), float(np.quantile(bm, 0.975))
        p = perm_p(x, MIN_EFFECT)
        out["H1"] = {"mean": float(x.mean()), "ci95": [lo, hi], "p_perm_vs_min_effect": p, "n_positive": int((x > 0).sum()),
                     "n_above_min": int((x > MIN_EFFECT).sum())}
        out["verdict"] = "bestätigt" if lo > MIN_EFFECT and p < 0.05 else "widerlegt (bricht)" if hi < MIN_EFFECT else "unklar"
    out["gate_n_acc_ge_0.5"] = int(sum(a >= GATE_ACC for a in accs))
    (HERE / "LM1_summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--jobs", action="store_true")
    ap.add_argument("--manifest", action="store_true")
    ap.add_argument("--commit")
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.build:
        build()
    if a.jobs:
        print("#! workers=4 job_minutes=240 min_minutes=5 crash_minutes=10")
        print("\n".join(jobs()))
    if a.manifest:
        manifest(a.commit)
    if a.analyze:
        analyze()


if __name__ == "__main__":
    main()
