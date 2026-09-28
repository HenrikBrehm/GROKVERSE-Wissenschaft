"""EXP-091 (small pilot for R9 H3): at c = 2 (lr x 2 for t = 15 steps, Lambda = 30), does rescaling the pre-switch betas to
windows equal in Lambda (beta' = 1 - 2(1 - beta) = 0.8/0.96) raise lock-in? Definition: README.md (fixed before any run).

Seeds 3260-3269 with the EXP-089 splits; pure runs and the standard curve (t = 25/33/45) come from EXP-089 (same seeds,
splits, device). New runs: (2, 15) and (2, 15, beta') in both directions -> 40 GPU runs.

  python lab/experiments/EXP-091-beta-window-c2/run.py --jobs      # job lines
  python lab/experiments/EXP-091-beta-window-c2/run.py --selftest
  python lab/experiments/EXP-091-beta-window-c2/run.py             # analysis (under guarded_run.py)
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
E89 = LAB / "experiments/EXP-089-lambda-fixed-steps"
sys.path.insert(0, str(LAB / "tools"))
from result_loader import Expect, find_run, load_run  # noqa: E402

_s = importlib.util.spec_from_file_location("exp089", E89 / "analyze.py")
X = importlib.util.module_from_spec(_s)
sys.path.insert(0, str(E89))
_s.loader.exec_module(X)
A, D89 = X.A, X.D

SEEDS, T, C, PSB, BUDGET = tuple(range(3260, 3270)), 15, 2.0, (0.8, 0.96), 2000
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()
REL, SPLR = "lab/experiments/EXP-091-beta-window-c2", "lab/experiments/EXP-089-lambda-fixed-steps/splits"
N_BOOT = 10_000


def jobs() -> list[str]:
    out = []
    for s in SEEDS:
        a, b = (f"{SPLR}/{D89.stem(s, x)}.npy" for x in "AB")
        base = (f"{PY} lab/experiments/EXP-001-freq-ban/freq_ban.py --seed {s} --condition baseline --threads 1 --device cuda "
                f"--test-file {SPLR}/seed{s}_test.npy --out-root {REL}/raw --lr-scale {C:g}")
        for extra in ("", f" --pre-switch-betas {PSB[0]},{PSB[1]}"):
            for first, second in ((a, b), (b, a)):
                out.append(f"{base} --steps {T + BUDGET} --split-file {first} --switch-split-file {second} --switch-step {T} "
                           f"--spectra-at {T},{T + 250},{T + BUDGET}{extra}")
    return out


def load(s: int, kind: str, psb: bool) -> np.ndarray | str:
    first, second = kind[0], kind[1]
    steps = T + BUDGET
    pat = (f"EXP-0*_baseline_seed{s}_thr*_{D89.stem(s, first)}_to_{D89.stem(s, second)}_at{T}_lrs{C:g}"
           + (f"_psb{PSB[0]!r}_{PSB[1]!r}" if psb else "") + "_devcuda")
    L = load_run(find_run(HERE / "raw", pat),
                 Expect(seed=s, device="cuda", max_steps=steps, split_file=E89 / "splits" / f"{D89.stem(s, first)}.npy",
                        test_file=E89 / "splits" / f"seed{s}_test.npy", switch_file=E89 / "splits" / f"{D89.stem(s, second)}.npy",
                        config={"p": 113, "task": "add", "lr_scale": C, "pre_switch_betas": list(PSB) if psb else None,
                                "beta1": 0.9, "beta2": 0.98}, snapshots_at=(steps,)))
    if L.status != "ok":
        return f"{kind}{'_psb' if psb else ''}: {L.status}: {L.reason}"
    if psb and L.res.get("events", {}).get("pre_switch_betas", {}).get("check") is not True:
        return f"{kind}_psb: beta switch not recorded"
    return A._a43.group_power(L.snapshot(steps), "add", 113)[0]


def boot_ci(d: np.ndarray, seed: int = 91) -> list[float]:
    rng = np.random.default_rng(seed)
    m = d[rng.integers(0, len(d), size=(N_BOOT, len(d)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def main() -> None:
    rows = []
    for s in SEEDS:
        meta = json.loads((E89 / "splits" / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        r89 = X.seed_row(s)
        new = {(k, ps): load(s, k, ps) for k in ("AB", "BA") for ps in (False, True)}
        bad = [v for v in new.values() if isinstance(v, str)] + ([] if r89["valid"] else [r89.get("reason", "EXP-089 row invalid")])
        if bad:
            rows.append({"seed": s, "valid": False, "reason": "; ".join(bad[:3])})
            continue
        LA, LB = A.logratio(X.load(s, "A"), F, G), A.logratio(X.load(s, "B"), F, G)
        r = {"seed": s, "valid": True, **{k: v for k, v in r89.items() if k.startswith("pi_")}}
        for ps, name in ((False, "pi_c2"), (True, "pi_c2b")):
            L = {"A": LA, "B": LB, "AB": A.logratio(new[("AB", ps)], F, G), "BA": A.logratio(new[("BA", ps)], F, G)}
            r[name] = A.pi_of(L)["pi"]
        rows.append(r)
    ok = [r for r in rows if r["valid"]]
    col = lambda k: np.array([r[k] for r in ok])   # noqa: E731
    out = {"n_valid": len(ok)}
    if len(ok) >= 2:
        e2 = col("pi_c2b") - col("pi_c2")
        curve = [float(col(f"pi_n{t}").mean()) for t in (25, 33, 45)]
        out.update({"e2_mean": float(e2.mean()), "e2_sd": float(e2.std(ddof=1)), "e2_ci95": boot_ci(e2), "e2_pos": int((e2 > 0).sum()),
                    "pi_means": {k: float(col(k).mean()) for k in ("pi_n25", "pi_n33", "pi_n45", "pi_c2", "pi_c2b")},
                    "t_eq": {k: X.t_equiv(float(col(k).mean()), curve) for k in ("pi_c2", "pi_c2b")},
                    "reading": ("H-beta-Richtung" if boot_ci(e2)[0] > 0 else "gegen H-beta" if boot_ci(e2)[1] < 0 else "unklar")})
    out["rows"] = rows
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    j = jobs()
    assert len(j) == 40 and sum("--pre-switch-betas 0.8,0.96" in x for x in j) == 20 and all("--lr-scale 2 " in x for x in j)
    assert abs(boot_ci(np.full(10, 0.1))[0] - 0.1) < 1e-12
    print("[exp091] selftest ok", flush=True)


if __name__ == "__main__":
    {"--jobs": lambda: print("\n".join(jobs())), "--selftest": selftest}.get((sys.argv[1:] or [""])[0], main)()
