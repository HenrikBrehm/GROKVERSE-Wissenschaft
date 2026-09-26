"""EXP-043: does data-split steering (EXP-016) generalize to add mod 97 and mul mod 113? UNTESTED (written out of window).

Per task and init seed i (70-79): two engineered runs, arms F and G (disjoint target sets), 2000 steps, all on the GPU.
K = top-5 frequencies of W_E at step 2000 in the task's group basis, computed here from the saved W_E snapshots:
  add 97 : rows W_E[a], a = 0..96, real DFT over Z_97, k = 1..48
  mul 113: rows W_E[g^i], i = 0..111 (g = 3), real DFT over Z_112, k = 1..55 (Nyquist k = 56 reported, never in K)
Primary per seed: Delta_i = ov(K_F, F) + ov(K_G, G) - ov(K_F, G) - ov(K_G, F); one-sided sign-flip test over seeds,
Holm over the two tasks. Definition: README.md.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB.parent / "training"))
sys.path.insert(0, str(HERE))
from grokverse.data import split_hash  # noqa: E402
from make_split import group  # noqa: E402

TASKS = (("add", 97), ("mul", 113))
SEEDS = range(70, 80)
M, STEP, ALPHA, MIN_VALID = 5, 2000, 0.05, 8
EXTRA_STEPS = (50, 250, 500, 1000)


def group_power(W: np.ndarray, task: str, p: int) -> tuple[np.ndarray, float | None]:
    """Power per frequency k = 1..(n-1)//2 of the number rows in group order; plus Nyquist power for even n."""
    n, elem = group(task, p)
    X = W[:p] if elem is None else W[elem]                  # [n, d]
    F = np.fft.fft(X, axis=0)
    sq = (np.abs(F) ** 2).sum(axis=1)
    K = (n - 1) // 2
    pw = 2.0 * sq[1:K + 1] / n                              # orthonormal real basis: cos^2 + sin^2 coefficients
    nyq = float(sq[n // 2] / n) if n % 2 == 0 else None
    return pw, nyq


def top(pw: np.ndarray) -> set[int]:
    return {int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:M]}


def fold(x: int, n: int) -> int:
    x %= n
    return min(x, n - x)


def run_dir(task: str, p: int, s: int, arm: str, eps: str = "2.0") -> Path | None:
    hits = sorted((HERE / "raw").glob(f"EXP-043_baseline_seed{s}_thr*_split_{task}{p}_seed{s}_eps{eps}_{arm}_*"))
    if len(hits) != 1 or not (hits[0] / "result.json").exists():        # Codex s12: died before first write -> missing
        return None
    res = json.loads((hits[0] / "result.json").read_text(encoding="utf-8"))
    return hits[0] if res.get("status") == "completed" else None


def snapshot(d: Path, step: int) -> np.ndarray | None:
    steps = np.load(d / "we_snapshot_steps.npy").tolist()
    if step not in steps:
        return None
    W = np.load(d / "we_snapshots.npy")[steps.index(step)].astype(np.float64)
    return W if np.isfinite(W).all() else None          # s13: a diverged (NaN) run is invalid, not a silent K


def row(task: str, p: int, s: int) -> dict:
    r: dict = {"seed": s, "valid": False}
    n = group(task, p)[0]
    T, K, extra = {}, {}, {}
    for arm in "FG":
        stem = f"split_{task}{p}_seed{s}_eps2.0_{arm}"
        T[arm] = set(json.loads((HERE / f"splits/{stem}.json").read_text(encoding="utf-8"))["targets"])
        d = run_dir(task, p, s, arm)
        if d is None:
            r["reason"] = f"arm {arm}: missing, ambiguous or not completed run dir"
            return r
        res = json.loads((d / "result.json").read_text(encoding="utf-8"))
        cfg = res["config"]
        if (res["status"] != "completed" or res["steps_completed"] < STEP or res["seed"] != s
                or cfg["p"] != p or cfg["task"] != task or res.get("device") != "cuda"):
            r["reason"] = f"arm {arm}: status/steps/seed/task/device"
            return r
        if res["split_hash"] != split_hash(np.load(HERE / f"splits/{stem}.npy")):
            r["reason"] = f"arm {arm}: split content hash mismatch"
            return r
        W = snapshot(d, STEP)
        if W is None:
            r["reason"] = f"arm {arm}: no W_E snapshot at {STEP}"
            return r
        pw, nyq = group_power(W, task, p)
        K[arm] = top(pw)
        extra[arm] = {"gen": res["events"].get("generalization_step"), "test_acc": res["final_acc"]["test"],
                      "top5_share": float(np.sort(pw)[-M:].sum() / pw.sum()), "nyquist_rank_above": None if nyq is None
                      else int((pw > nyq).sum()),
                      "ov_own_early": {t: (len(top(group_power(Wt, task, p)[0]) & T[arm]) if (Wt := snapshot(d, t)) is not None
                                           else None) for t in EXTRA_STEPS}}
    ov = {f"{x}{y}": len(K[x] & T[y]) for x in "FG" for y in "FG"}
    nontarget = [(arm, k) for arm in "FG" for k in K[arm] - T[arm]]
    r.update({"valid": True, "F": sorted(T["F"]), "G": sorted(T["G"]), "K_F": sorted(K["F"]), "K_G": sorted(K["G"]),
              **{f"ov_{k}": v for k, v in ov.items()}, "Delta": ov["FF"] + ov["GG"] - ov["FG"] - ov["GF"],
              "n_nontarget": len(nontarget),
              "n_nontarget_harmonic": sum(any(fold(2 * t, n) == k for t in T[arm]) for arm, k in nontarget),
              "arms": extra})
    d = run_dir(task, p, s, "R", eps="0.0")                # secondary: random split (eps 0) against both target sets
    if d is not None and (W := snapshot(d, STEP)) is not None:
        kr = top(group_power(W, task, p)[0])
        r["ov_random_F"], r["ov_random_G"] = len(kr & T["F"]), len(kr & T["G"])
    return r


def one_sided_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def selftest() -> None:
    """Fail-closed check of group_power (run in the window before any EXP-043 run)."""
    rng = np.random.default_rng(0)
    for task, p in TASKS:
        n, elem = group(task, p)
        W = rng.normal(size=(p + 1, 8))
        pos = np.arange(n)
        for k0 in (1, 7, (n - 1) // 2):
            X = np.zeros((p + 1, 8))
            rows = np.arange(p) if elem is None else elem
            X[rows, 0] = 3 * np.cos(2 * np.pi * k0 * pos / n + 0.4)
            pw, _ = group_power(X, task, p)
            assert top(pw) >= {k0} and int(np.argmax(pw)) + 1 == k0, (task, k0)
        pw, nyq = group_power(W, task, p)
        X = W[:p] if elem is None else W[elem]
        dc = (X.mean(axis=0) ** 2).sum() * n
        assert abs(pw.sum() + (nyq or 0.0) + dc - (X ** 2).sum()) < 1e-8, (task, "Parseval")
    print("[exp043] selftest ok", flush=True)


def main() -> None:
    if sys.argv[1:] == ["--selftest"]:
        selftest()
        return
    out: dict = {"tasks": {}}
    for task, p in TASKS:
        rows = [row(task, p, s) for s in SEEDS]
        valid = [r for r in rows if r["valid"]]
        t: dict = {"rows": rows, "n_valid": len(valid)}
        if len(valid) >= MIN_VALID:
            D = np.array([r["Delta"] for r in valid], dtype=float)
            t.update({"Delta_mean": float(D.mean()), "p": one_sided_p(D), "n_positive": int((D > 0).sum()),
                      "ov_matched_mean": float(np.mean([(r["ov_FF"] + r["ov_GG"]) / 2 for r in valid])),
                      "ov_crossed_mean": float(np.mean([(r["ov_FG"] + r["ov_GF"]) / 2 for r in valid])),
                      "share_nontarget_harmonic": sum(r["n_nontarget_harmonic"] for r in valid)
                      / max(1, sum(r["n_nontarget"] for r in valid))})
            rr = [r for r in valid if "ov_random_F" in r]
            if rr:
                t["ov_random_mean"] = float(np.mean([(r["ov_random_F"] + r["ov_random_G"]) / 2 for r in rr]))
        out["tasks"][f"{task}{p}"] = t
    # Holm over the two tasks (only tasks with >= MIN_VALID valid seeds enter)
    ev = sorted(((k, t["p"]) for k, t in out["tasks"].items() if "p" in t), key=lambda x: x[1])
    m = len(TASKS)
    still = True
    for i, (k, pv) in enumerate(ev):
        t = out["tasks"][k]
        sig = still and pv < ALPHA / (m - i)
        still = sig
        t["holm_significant"] = sig
    for k, t in out["tasks"].items():
        t["verdict"] = ("nicht auswertbar" if "p" not in t else "widerspricht" if t["Delta_mean"] <= 0
                        else "steuerbar" if t["holm_significant"] else "richtungsgleich, nicht signifikant")
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for k, t in out["tasks"].items():
        print(k, {x: v for x, v in t.items() if x != "rows"})


if __name__ == "__main__":
    main()
