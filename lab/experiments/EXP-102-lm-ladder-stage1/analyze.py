"""EXP-102 pilot analysis (exploration). Session 44, UNTESTED. Readings fixed here before any run:

Measure: Delta_pow at step 2000 from W_E[:p] (number tokens only; power per k = 2 |DFT_k|^2 / p summed over d, as
EXP-043 group_power for add 113), Delta_pow = log[P_F(T_F)/P_F(T_G)] + log[P_G(T_G)/P_G(T_F)] (confirm_p1.delta_pow).
Per rung r: mean, bootstrap 95 % CI over seeds (10 000 resamples, rng 102), n positive.
  holds      CI lower bound > 0
  breaks     CI upper bound < 0.5 * mean Delta_pow of r0 (the rung loses at least half of the reference effect)
  weakened   paired CI of Delta(r) - Delta(r0) < 0, but not "breaks"
  (else)     "holds, not weaker than r0" or "unclear"
The first rung in the order op, fs, tie, all that "breaks" is the ladder result (rule 20e: itself a finding).
Pair-structure control: paired D = Delta(all) - Delta(allnb); "p(b|a) as a target adds steering" if its CI > 0.
Random split R (descriptive): target share of the seed's F and G targets (10 of 56 frequencies; chance 0.179) for
rungs all and allnb; a clear excess under "all" but not "allnb" would show the extra supervision creating a preference
on its own (not expected on R, where p(b|a) is ~uniform).
Equivalence of r0 with freq_ban.py: compared separately (same seeds, same splits) before the ladder is read.

  python lab/tools/guarded_run.py -- python lab/experiments/EXP-102-lm-ladder-stage1/analyze.py [--selftest]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import design  # noqa: E402

P, STEP, BOOT = 113, 2000, 10_000
FLAGS = {"r0": (0, 0, 0, "answer"), "op": (1, 0, 0, "answer"), "fs": (0, 1, 0, "answer"), "tie": (0, 1, 1, "answer"),
         "all": (0, 1, 0, "all"), "allnb": (0, 1, 0, "all_but_b")}


def power(W: np.ndarray) -> np.ndarray:
    sq = (np.abs(np.fft.fft(W.astype(np.float64), axis=0)) ** 2).sum(1)
    return 2.0 * sq[1:(P - 1) // 2 + 1] / P


def delta_pow(pF, pG, F, G) -> float | None:
    s = lambda pw, S: float(pw[[k - 1 for k in S]].sum())   # noqa: E731
    v = [s(pF, F), s(pF, G), s(pG, F), s(pG, G)]
    return float(np.log(v[0] / v[1]) + np.log(v[3] / v[2])) if all(np.isfinite(x) and x > 0 for x in v) else None


def run_dir(seed: int, split: str, rung: str, root: str = "raw") -> Path:
    op, fs, tie, loss = FLAGS[rung]
    return HERE / root / f"lad_seed{seed}_seed{seed}_{split}_op{op}_fs{fs}_tie{tie}_loss{loss}_B0_steps{STEP}_thr1_cuda"


def load_power(seed: int, split: str, rung: str) -> np.ndarray | str:
    d = run_dir(seed, split, rung)
    if not (d / "result.json").exists():
        return "fehlt"
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    sp = HERE / "splits" / f"seed{seed}_{split}.npy"
    import hashlib
    if r.get("status") != "completed" or r.get("steps_completed") != STEP or \
            r.get("split_sha256") != hashlib.sha256(sp.read_bytes()).hexdigest():
        return "defekt"
    steps = list(np.load(d / "we_snapshot_steps.npy"))
    if STEP not in steps:
        return "defekt"
    W = np.load(d / "we_snapshots.npy")[steps.index(STEP)]
    return power(W) if np.isfinite(W).all() else "defekt"


def ci(x: np.ndarray, rng: np.random.Generator) -> list[float]:
    m = rng.choice(x, size=(BOOT, len(x)), replace=True).mean(1)
    return [float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))]


def analyze() -> dict:
    rng = np.random.default_rng(102)
    D: dict[str, dict[int, float]] = {r: {} for r in design.RUNGS}
    bad, shares = [], {r: [] for r in design.R_RUNGS}
    for s in design.SEEDS:
        T = json.loads((HERE / "splits" / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        for r in design.RUNGS:
            pF, pG = load_power(s, "F", r), load_power(s, "G", r)
            if isinstance(pF, str) or isinstance(pG, str):
                bad.append([s, r, pF if isinstance(pF, str) else pG])
                continue
            d = delta_pow(pF, pG, T["F"], T["G"])
            if d is None:
                bad.append([s, r, "delta_pow undefined"])
            else:
                D[r][s] = d
        for r in design.R_RUNGS:
            pR = load_power(s, "R", r)
            if not isinstance(pR, str):
                shares[r].append(float(pR[[k - 1 for k in T["F"] + T["G"]]].sum() / pR.sum()))
    out: dict = {"n_bad": len(bad), "bad": bad, "rungs": {}}
    ref = np.array(list(D["r0"].values()))
    for r in design.RUNGS:
        x = np.array(list(D[r].values()))
        if len(x) < 2:
            continue
        row = {"n": len(x), "mean": float(x.mean()), "ci95": ci(x, rng), "n_pos": int((x > 0).sum())}
        if r != "r0" and len(ref) >= 2:
            common = sorted(set(D[r]) & set(D["r0"]))
            diff = np.array([D[r][s] - D["r0"][s] for s in common])
            row["diff_vs_r0"] = {"n": len(diff), "mean": float(diff.mean()), "ci95": ci(diff, rng)}
            row["reading"] = ("breaks" if row["ci95"][1] < 0.5 * ref.mean() else
                              "weakened" if row["diff_vs_r0"]["ci95"][1] < 0 else
                              "holds" if row["ci95"][0] > 0 else "unclear")
        else:
            row["reading"] = "holds" if row["ci95"][0] > 0 else "unclear"
        out["rungs"][r] = row
    out["first_break"] = next((r for r in ("op", "fs", "tie", "all") if out["rungs"].get(r, {}).get("reading") == "breaks"), None)
    common = sorted(set(D["all"]) & set(D["allnb"]))
    if len(common) >= 2:
        dd = np.array([D["all"][s] - D["allnb"][s] for s in common])
        c = ci(dd, rng)                                        # review s44: one bootstrap draw for CI and reading
        out["all_minus_allnb"] = {"n": len(dd), "mean": float(dd.mean()), "ci95": c,
                                  "reading": "p(b|a) adds steering" if c[0] > 0 else "no added steering shown"}
    out["R_target_share"] = {r: {"n": len(v), "mean": float(np.mean(v)) if v else None, "chance": 10 / 56} for r, v in shares.items()}
    (HERE / "pilot_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "bad"}, indent=1))
    return out


def selftest() -> None:
    v = np.arange(P)
    W = np.stack([np.cos(2 * np.pi * 3 * v / P), np.sin(2 * np.pi * 3 * v / P)], 1)
    pw = power(W)
    assert abs(pw[2] - P) < 1e-9 and np.abs(np.delete(pw, 2)).max() < 1e-9      # |W|^2 = P, all at k = 3
    assert abs(delta_pow(np.array([4.0, 1.0]), np.array([1.0, 4.0]), [1], [2]) - 2 * np.log(4)) < 1e-12
    assert delta_pow(np.array([0.0, 1.0]), np.array([1.0, 4.0]), [1], [2]) is None
    assert run_dir(3800, "F", "tie").name == "lad_seed3800_seed3800_F_op0_fs1_tie1_lossanswer_B0_steps2000_thr1_cuda"
    print("selftest ok")


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else analyze()
