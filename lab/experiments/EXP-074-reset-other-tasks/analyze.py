"""EXP-074 (pilot): does the reset pattern of K4d/K4e (attention and value path matter, MLP and pattern less) hold at add 97 and mul 113?
Definition: README.md (fixed before any run). EXP-044 protocol (seeds 80-89, F -> G at t = 50, 2000 steps on G, ~38 % shared pairs).
pi = (L(switch) - L(only G)) / (L(only F) - L(only G)), L = log[P(F targets) / P(G targets)] of the final W_E power in the group basis
(EXP-044 pi_persistence). Pure F/G runs from EXP-044. dpi_X = pi_normal - pi_rsX per seed. Run under guarded_run.py (imports torch).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
_spec = importlib.util.spec_from_file_location("exp044_analyze", LAB / "experiments/EXP-044-generalize-lockin/analyze.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)
E44 = LAB / "experiments/EXP-044-generalize-lockin"
PARTS, T, MIN_VALID, MIN_SEP, MIN_PI_NORMAL = ("attn", "vo", "qk", "mlp"), 50, 8, 1.0, 0.5


def final_power(task: str, p: int, s: int, arm: str | None) -> np.ndarray | str:
    st = E44 / f"splits/{task}{p}_seed{s}"
    if arm in ("F", "G"):                                    # pure runs of EXP-044
        d, steps, sw = A.find(task, p, s, arm), 2000, None
        split = f"{st}_train_{arm}.npy"
    else:
        suf = "" if arm == "normal" else f"_rs{arm}"
        d = A.find_run(HERE / "raw", f"EXP-044_baseline_seed{s}_thr1_{task}{p}_seed{s}_train_F_to_{task}{p}_seed{s}_train_G_at{T}_{task}{p}{suf}_devcuda")   # freq_ban order: task suffix, then _rs<part>, then _dev
        steps, sw, split = T + 2000, f"{st}_train_G.npy", f"{st}_train_F.npy"
    L = A.load_run(d, A.Expect(seed=s, device="cuda", max_steps=steps, split_file=split, test_file=f"{st}_test.npy", switch_file=sw,
                               config={"p": p, "task": task}, snapshots_at=(steps,)))
    if L.status != "ok":
        return f"{task}{p} {arm}: {L.status}: {L.reason}"
    if arm not in ("F", "G", "normal"):
        ev = L.res.get("events", {}).get("reset_at_switch", {})
        if ev.get("which") != arm or ev.get("check") is not True:
            return f"{task}{p} {arm}: reset not recorded"
    return A.group_power(L.snapshot(steps), task, p)[0]


def reading(dpi: dict[str, np.ndarray]) -> str:
    """Pre-registered (README): pattern generalises / does not / unclear, per task."""
    med = {x: float(np.median(v)) for x, v in dpi.items()}
    if med["attn"] >= 0.4 and (dpi["attn"] > 0.3).sum() >= 8 and med["vo"] >= 0.3 and med["mlp"] < 0.3 and med["qk"] < med["vo"]:
        return "Reset-Muster verallgemeinert"
    if med["attn"] < 0.2:
        return "nicht verallgemeinert (Attention-Reset wirkt kaum)"
    return "unklar"


def main() -> None:
    out: dict = {}
    for task, p in A.TASKS:
        rows = []
        for s in A.SEEDS:
            meta = json.loads((E44 / f"splits/{task}{p}_seed{s}.json").read_text(encoding="utf-8"))
            F, G = meta["targets"]["F"], meta["targets"]["G"]
            lr = lambda pw: float(np.log(pw[[k - 1 for k in F]].sum() / pw[[k - 1 for k in G]].sum()))   # noqa: E731
            pw = {k: final_power(task, p, s, k) for k in ("F", "G", "normal") + PARTS}
            bad = [v for v in pw.values() if isinstance(v, str)]
            if bad:
                rows.append({"seed": s, "valid": False, "reason": "; ".join(bad[:3])})
                continue
            lf, lg = lr(pw["F"]), lr(pw["G"])
            pi = {k: (lr(pw[k]) - lg) / (lf - lg) for k in ("normal",) + PARTS}
            ok = lf - lg >= MIN_SEP and pi["normal"] >= MIN_PI_NORMAL
            rows.append({"seed": s, "valid": ok, "sep": lf - lg, "pi": pi, **({} if ok else {"reason": "separation or pi_normal too small"})})
        v = [r for r in rows if r["valid"]]
        res: dict = {"n_valid": len(v), "rows": rows}
        if len(v) >= MIN_VALID:
            dpi = {x: np.array([r["pi"]["normal"] - r["pi"][x] for r in v]) for x in PARTS}
            res |= {"median_pi": {k: float(np.median([r["pi"][k] for r in v])) for k in ("normal",) + PARTS},
                    "median_dpi": {x: float(np.median(d)) for x, d in dpi.items()},
                    "n_dpi_gt_0.3": {x: int((d > 0.3).sum()) for x, d in dpi.items()}, "reading": reading(dpi)}
        else:
            res["reading"] = "nicht auswertbar"
        out[f"{task}{p}"] = res
        print(task, p, json.dumps({k: w for k, w in res.items() if k != "rows"}), flush=True)
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


def selftest() -> None:
    ok = {"attn": np.full(10, 0.8), "vo": np.full(10, 0.5), "qk": np.full(10, 0.1), "mlp": np.full(10, 0.1)}
    assert reading(ok) == "Reset-Muster verallgemeinert"
    assert reading({**ok, "attn": np.full(10, 0.1)}).startswith("nicht")
    assert reading({**ok, "mlp": np.full(10, 0.5)}) == "unklar"
    assert reading({**ok, "qk": np.full(10, 0.6)}) == "unklar"
    print("[exp074] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
