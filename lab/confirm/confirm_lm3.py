"""LM3 confirmation block (session 56): does the choice of arithmetic facts steer the number-token embeddings of the small LM
when arithmetic sentences are only a few percent of the tokens? Registration: lab/confirm/LM3_REGISTRATION.md (readings fixed there
and here). Same code path as confirm_lm1.py (LM1: 19 facts per sequence, about 79 % arithmetic tokens); changed: K = 2 arithmetic
sentences per sequence (about 8.7 % arithmetic tokens, as the EXP-116 pilot), STEPS, GATE_N, fresh seeds, bootstrap rng.

Setup (frozen): lm_stage2.py (EXP-105, TinyStories + arithmetic sentences, 13.9 M parameters, tied embeddings), K = 2, loss on text
and answer tokens only (--loss answer), STEPS steps (no text wrap), GPU. Fresh split seeds 4010-4019 (engineered F/G pair + held-out
test set from EXP-102 design.build, i.e. the P1/EXP-053 construction); model seed = split seed + 100.

  python lab/confirm/confirm_lm3.py --build       # splits and test sets -> lab/confirm/lm3_splits (never overwrites)
  python lab/confirm/confirm_lm3.py --jobs        # job lines for the GPU daemon (stdout)
  python lab/confirm/confirm_lm3.py --manifest --commit <id>   # code hashes -> LM3_manifest.json
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/confirm/confirm_lm3.py --analyze

Analysis (frozen, run only after all 20 runs finished): as confirm_lm1.py (binding incl. no text wrap, gate, H1 Delta_pow at the
last step > MIN_EFFECT with bootstrap CI and exact sign-flip p, mirrored test, defects, secondary s_learn/s_steer), with the gate
GATE_N of 20 runs reaching held-out accuracy >= 0.5 at the end.
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

SEEDS = tuple(range(4010, 4020))
MODEL_OFFSET, K, STEPS, LOSS = 100, 2, 15000, "answer"   # STEPS: LM3_REGISTRATION
SPL, RAW = HERE / "lm3_splits", HERE / "lm3_raw"
TRAINER = LAB / "experiments/EXP-105-lm-ladder-stage2/lm_stage2.py"
CODE = [TRAINER, LAB / "experiments/EXP-105-lm-ladder-stage2/analyze_pilot.py", LAB / "experiments/EXP-102-lm-ladder-stage1/analyze.py",
        LAB / "experiments/EXP-102-lm-ladder-stage1/design.py", LAB / "experiments/EXP-053-p3-overlap-design/overlap_split.py",
        Path(__file__).resolve(), HERE / "confirm_lm3f.py"]
FROZEN = {"steps": STEPS, "batch": 32, "ctx": 256, "d": 384, "layers": 6, "heads": 6, "lr": 6e-4, "warmup": 500, "wd": 0.1,
          "arith_facts": K, "device": "cuda", "loss": LOSS}
MIN_EFFECT, GATE_ACC, GATE_N = 1.0, 0.5, 16   # GATE_N: LM3_REGISTRATION
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
    print(f"[lm3] wrote splits for {len(SEEDS)} seeds")


def jobs() -> list[str]:
    return [f"{PY} {rel(TRAINER)} --seed {s + MODEL_OFFSET} --split-file {rel(SPL)}/seed{s}_{x}.npy --test-file {rel(SPL)}/seed{s}_test.npy "
            f"--steps {STEPS} --arith-facts {K} --loss {LOSS} --device cuda --out-root {rel(RAW)}" for s in SEEDS for x in "FG"]


def manifest(commit: str) -> None:
    assert commit, "--manifest needs --commit"
    smoke = json.loads(next((HERE / "lm3_smoke").glob("lm2_seed4110_seed4010_F_steps250_*/result.json")).read_text(encoding="utf-8"))
    run_constants = {k: smoke["config"][k] for k in ("tokenizer_sha256", "text_tokens", "templates")}
    m = {"block": "LM3", "commit": commit, "seeds": list(SEEDS), "model_offset": MODEL_OFFSET, "frozen": FROZEN, "loss": LOSS,
         "registration": ["lab/confirm/LM3_REGISTRATION.md"], "code_sha256": {rel(p): sha(p) for p in CODE},
         "split_sha256": {f.name: sha(f) for f in sorted(SPL.glob("seed*"))}, "run_constants": run_constants}
    with open(HERE / "LM3_manifest.json", "x", encoding="utf-8") as f:
        json.dump(m, f, indent=1)
    print("[lm3] manifest written")


def check_binding(m: dict, r: dict, s: int, arm: str) -> list[str]:
    c, bad = r["config"], []
    if c["script_sha256"] != m["code_sha256"][rel(TRAINER)]:
        bad.append("trainer hash")
    if c["split_sha256"] != m["split_sha256"][f"seed{s}_{arm}.npy"] or c["test_sha256"] != m["split_sha256"][f"seed{s}_test.npy"]:
        bad.append("split/test hash")
    if sha(SPL / f"seed{s}.json") != m["split_sha256"][f"seed{s}.json"]:
        bad.append("target metadata hash")
    bad += [f"run constant {k}" for k, v in m["run_constants"].items() if c.get(k) != (list(v) if isinstance(v, (list, tuple)) else v)]
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
    m = json.loads((HERE / "LM3_manifest.json").read_text(encoding="utf-8"))
    for p in CODE:
        assert sha(p) == m["code_sha256"][rel(p)], f"code changed since the freeze: {rel(p)}"
    rows, defect, accs = [], [], []
    expected = {f"lm2_seed{s + MODEL_OFFSET}_seed{s}_{x}_steps{STEPS}_" for s in SEEDS for x in "FG"}
    stray = [d.name for d in RAW.iterdir() if not any(d.name.startswith(e) for e in expected)] if RAW.exists() else []
    if stray:
        defect.append({"seed": None, "why": f"unexpected run directories: {stray}"})
    for s in SEEDS:
        try:
            rF, rG = AP.load(RAW, s + MODEL_OFFSET, SPL / f"seed{s}_F.npy"), AP.load(RAW, s + MODEL_OFFSET, SPL / f"seed{s}_G.npy")
            bad = check_binding(m, rF["res"], s, "F") + check_binding(m, rG["res"], s, "G")
            cF, cG = dict(rF["res"]["config"]), dict(rG["res"]["config"])
            cF.pop("split_sha256"), cG.pop("split_sha256")
            if cF != cG:
                bad.append("F and G configs differ beyond the split")
            TF, TG = AP.targets(SPL / f"seed{s}_F.npy"), AP.targets(SPL / f"seed{s}_G.npy")
            steps = [x for x in rF["steps"] if x in rG["P"]]
            if steps[-1] != STEPS:
                bad.append(f"last common snapshot {steps[-1]}")
            dp = {x: A.delta_pow(rF["P"][x], rG["P"][x], TF, TG) for x in steps}
            if dp[steps[-1]] is None or not np.isfinite(dp[steps[-1]]):
                bad.append("Delta_pow not finite")
        except (AssertionError, FileNotFoundError, KeyError, StopIteration, ValueError) as e:
            defect.append({"seed": s, "why": f"missing, incomplete or unreadable: {e!r}"})
            continue
        if bad:
            defect.append({"seed": s, "why": bad})
            continue
        trF = {int(c[0]): c[1] for c in rF["res"]["curve"]}
        trG = {int(c[0]): c[1] for c in rG["res"]["curve"]}
        s_learn = next((x for x in steps if trF.get(x, 0) >= 0.1 and trG.get(x, 0) >= 0.1), None)
        s_steer = next((x for x in steps if dp[x] is not None and dp[x] > MIN_EFFECT), None)
        acc = [rF["res"]["curve"][-1][2], rG["res"]["curve"][-1][2]]
        accs += acc
        rows.append({"seed": s, "dpow_end": dp[STEPS], "test_acc": acc, "s_learn": s_learn, "s_steer": s_steer,
                     "gen": [rF["res"]["events"].get("generalization_step"), rG["res"]["events"].get("generalization_step")]})
    out: dict = {"block": "LM3", "manifest_commit": m["commit"], "n_valid": len(rows), "defect": defect, "rows": rows}
    if defect or len(rows) < len(SEEDS):
        out["verdict"] = "nicht auswertbar (defekt/fehlt)"
    elif sum(a >= GATE_ACC for a in accs) < GATE_N:
        out["verdict"] = "nicht auswertbar (Budget)"
    else:
        x = np.array([r["dpow_end"] for r in rows])
        rng = np.random.default_rng(4021)
        bm = rng.choice(x, (10000, len(x)), replace=True).mean(1)
        lo, hi = float(np.quantile(bm, 0.025)), float(np.quantile(bm, 0.975))
        p = perm_p(x, MIN_EFFECT)
        p_low = perm_p(-x, -MIN_EFFECT)                                   # mirrored: mean < 1
        out["H1"] = {"mean": float(x.mean()), "ci95": [lo, hi], "p_perm_vs_min_effect": p, "p_perm_below_min_effect": p_low,
                     "n_positive": int((x > 0).sum()), "n_above_min": int((x > MIN_EFFECT).sum())}
        out["verdict"] = ("bestätigt" if lo > MIN_EFFECT and p < 0.05 else
                          "unter Mindesteffekt" if hi < MIN_EFFECT and p_low < 0.05 else "unklar")
    out["gate_n_acc_ge_0.5"] = int(sum(a >= GATE_ACC for a in accs))
    (HERE / "LM3_summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
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
        print("#! workers=3 job_minutes=600 min_minutes=5 crash_minutes=10 gpu_gb=3.5")
        print("\n".join(jobs()))
    if a.manifest:
        manifest(a.commit)
    if a.analyze:
        analyze()


if __name__ == "__main__":
    main()
