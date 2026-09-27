"""C1 analysis (registration lab/confirm/C1_REGISTRATION.md, session 28). Written BEFORE any R1 run; must not change measure,
unit, test or thresholds of the registration.

Reads the R1 runs through the frozen R1 loader (confirm_r1.power: binding, split bytes, hyperparameters, finite spectrum).
Per arm: Spearman over the 5 targets between the centred coherent mask spectrum M0c of the split and the W_E power at step 2000.
Unit = seed (mean of F and G). Primary: pooled over all R1 seeds, one-sided sign-flip test mean > 0 (200 000 draws), 95 %
bootstrap CI over seeds (10 000); confirmed = p < 0.05 and CI lower bound >= 0.10; not evaluable if < 60 seeds with two valid arms.
Descriptive: per cell means, M0 and step-0 predictors, share "weakest learned target = lowest M0c".

  python lab/confirm/C1_analyze.py --selftest              (window only: reproduces the P1 exploration on stored P1 runs)
  python lab/confirm/C1_analyze.py lab/confirm/R1_manifest.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "confirm"))
import confirm_splits as cs  # noqa: E402
from P1_posthoc_within import m0c_add  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

P, ALPHA, MIN_EFFECT, MIN_SEEDS, N_FLIP, N_BOOT = 113, 0.05, 0.10, 60, 200_000, 10_000
OUT = LAB / "confirm" / "C1_summary.json"


def spearman5(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman over 5 values without ties (continuous spectra): 1 - 6 sum d^2 / (n (n^2 - 1))."""
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(1.0 - 6.0 * ((rx - ry) ** 2).sum() / (5 * 24))


def arm_values(idx: np.ndarray, T: list[int], pw: np.ndarray, pw0: np.ndarray | None) -> dict:
    sel = [k - 1 for k in T]
    mc, m0 = m0c_add(idx, P)[sel], cs.m0(idx, "add", P)[sel]
    y = pw[sel]
    return {"rho_M0c": spearman5(mc, y), "rho_M0": spearman5(m0, y),
            "rho_init": None if pw0 is None else spearman5(pw0[sel], y), "weakest_is_lowest_M0c": bool(np.argmin(mc) == np.argmin(y))}


def primary(d: np.ndarray, rng: np.random.Generator) -> dict:
    if len(d) < MIN_SEEDS:
        return {"n": len(d), "verdict": "nicht auswertbar"}
    signs = rng.choice((-1.0, 1.0), size=(N_FLIP, len(d)))
    p = float(((signs * np.abs(d)).mean(1) >= d.mean()).mean())      # one-sided, H0: symmetric around 0
    b = rng.choice(d, size=(N_BOOT, len(d))).mean(1)
    ci = [float(np.quantile(b, 0.025)), float(np.quantile(b, 0.975))]
    ok = p < ALPHA and ci[0] >= MIN_EFFECT
    return {"n": len(d), "mean": float(d.mean()), "sd": float(d.std(ddof=1)), "n_positive": int((d > 0).sum()), "p": p, "ci95": ci,
            "verdict": "bestätigt" if ok else "nicht bestätigt"}


def step0_power(d: Path, s: int, man: dict, split: Path) -> np.ndarray | None:
    sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
    from analyze import group_power
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=man["steps"], split_file=split, snapshots_at=(0,)))
    return group_power(L.snapshot(0).astype(np.float64), "add", P)[0] if L.status == "ok" else None


def analyze(manifest: Path) -> None:
    import confirm_r1 as r1
    man = json.loads(manifest.read_text(encoding="utf-8"))
    r1.BLOCK.check_manifest(manifest, man)
    r1.check_design(man)
    rows, dropped = [], []
    for c in r1.CELLS:
        for s in man["seeds"][c]:
            if (m := r1.split_mismatch(man, c, s)):
                dropped.append({"cell": c, "seed": s, "reason": m})
                continue
            arms = {}
            for a in "FG":
                run = r1.power(man, c, s, a)
                if isinstance(run, str):
                    break
                split = r1.SPL / f"{r1.stem(c, s, a)}.npy"
                T = json.loads((r1.SPL / f"{r1.stem(c, s, a)}.json").read_text(encoding="utf-8"))["targets"]
                cmd = ["x", r1.FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", man["device"], "--split-file", str(split)]
                for k, v in r1.CELLS[c].items():
                    cmd += [r1.FLAG[k], repr(v)]
                arms[a] = arm_values(np.load(split), T, run["pw"], step0_power(r1.run_dir(cmd), s, man, split))
            if len(arms) != 2:
                dropped.append({"cell": c, "seed": s, "reason": f"arm invalid: {run}"})
                continue
            rows.append({"cell": c, "seed": s, **{f"{k}_{a}": v for a in "FG" for k, v in arms[a].items()},
                         "unit": (arms["F"]["rho_M0c"] + arms["G"]["rho_M0c"]) / 2})
    rng = np.random.default_rng(2026_09_28_1)
    d = np.array([r["unit"] for r in rows])
    desc = {c: float(np.mean([r["unit"] for r in rows if r["cell"] == c])) for c in r1.CELLS if any(r["cell"] == c for r in rows)}
    for k in ("rho_M0", "rho_init"):
        v = [r[f"{k}_{a}"] for r in rows for a in "FG" if r[f"{k}_{a}"] is not None]
        desc[f"mean_{k}_per_arm"] = float(np.mean(v)) if v else None
    desc["weakest_is_lowest_M0c"] = float(np.mean([r[f"weakest_is_lowest_M0c_{a}"] for r in rows for a in "FG"])) if rows else None
    out = {"registration": "lab/confirm/C1_REGISTRATION.md", "manifest_commit": man["commit"], "primary": primary(d, rng),
           "descriptive": desc, "dropped": dropped, "rows": rows}
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    """(1) spearman5 against numpy ranks; (2) primary(): an effect far above threshold confirms, zero effect does not, too few
    seeds -> not evaluable; (3) on the stored P1 add-113 runs the unit mean reproduces the exploration (0.438, 50 seeds)."""
    x = np.array([3.0, 1.0, 4.0, 1.5, 9.0])
    assert abs(spearman5(x, x) - 1) < 1e-12 and abs(spearman5(x, -x) + 1) < 1e-12
    rng = np.random.default_rng(0)
    assert primary(rng.normal(0.4, 0.3, 90), rng)["verdict"] == "bestätigt"
    assert primary(rng.normal(0.0, 0.3, 90), rng)["verdict"] == "nicht bestätigt"
    assert primary(rng.normal(0.4, 0.3, 59), rng)["verdict"] == "nicht auswertbar"
    import confirm_p1 as c
    man = json.loads((LAB / "confirm/P1_manifest.json").read_text(encoding="utf-8"))
    t = {"task": "add", "p": P}
    u = []
    for s in man["seeds"]:
        r = []
        for a in "FG":
            st = c.stem(man, t, s, a)
            T = json.loads((c.SPLITS / f"{st}.json").read_text(encoding="utf-8"))["targets"]
            r.append(arm_values(np.load(c.SPLITS / f"{st}.npy"), T, c.power_at(man, t, s, a), None)["rho_M0c"])
        u.append(np.mean(r))
    assert len(u) == 50 and abs(np.mean(u) - 0.438) < 0.0015, np.mean(u)
    print("C1 selftest ok", round(float(np.mean(u)), 4))


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif len(sys.argv) == 2:
        analyze(Path(sys.argv[1]))
    else:
        raise SystemExit(__doc__)
