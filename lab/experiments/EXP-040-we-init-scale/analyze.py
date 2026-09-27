"""EXP-040 analysis (pre-registered, README): EXP-020 protocol with W_E multiplied by s right after init (all arms of a
cell, including the t = 0 "only G" reference, which is therefore an own run). Same decision logic as EXP-039 (imported):
H40 (amplitude threshold: lock-in when the data-driven W_E amplitude reaches the init amplitude) -> s = 0.5 behaves like
c = 2 (interval (12, 25]), s = 2 like c = 0.5 ((50, 100]); pure Lambda clock -> (25, 50] for both s ('step' label of
EXP-039 = 'unchanged' here). Unit = seed with both scales; >= 3 complete seeds; all 'h40' -> H40 gestuetzt; all
'unchanged' -> Init-Skala ohne Einfluss; else unklar.
Usage: python analyze.py [--selftest]"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[0]
sys.path.insert(0, str(LAB / "EXP-039-lr-clock"))
from analyze import classify  # noqa: E402  (EXP-039)


def seed_class(a: str, b: str) -> str:
    """Nachtrag d (session 23, before any EXP-040 run): EXP-039's seed_class only knows its own labels (lambda/step), so the import
    turned every EXP-040 seed into 'unclear' (selftest failed closed). Registered rule (README): a seed is h40 / unchanged only if
    both scales agree, else unclear."""
    return a if a == b and a in ("h40", "unchanged") else "unclear"

SEEDS = (30, 32, 34, 31)
EQUIV = {0.5: 2.0, 2.0: 0.5}          # s -> lr scale c with the same predicted interval under H40
GRIDS = {0.5: (10, 12, 25, 50), 2.0: (25, 50, 100, 150)}
LABEL = {"lambda": "h40", "step": "unchanged", "unclear": "unclear"}
MIN_SEEDS = 3


def verdict(classes: list[str]) -> str:
    if len(classes) < MIN_SEEDS:
        return "nicht auswertbar"
    if all(c == "h40" for c in classes):
        return "H40-Muster gestuetzt (Festlegung verschiebt sich mit der W_E-Init-Skala wie vorhergesagt; Assoziation)"
    return "Init-Skala ohne Einfluss" if all(c == "unchanged" for c in classes) else "unklar"


def load_mod(s_: float):
    spec = importlib.util.spec_from_file_location(f"exp020_s{s_}", LAB / "EXP-020-data-switch" / "analyze.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.SWITCH = GRIDS[s_]
    m.GRID = (0.0, *map(float, GRIDS[s_]), math.inf)
    orig = m.run_dir
    m.run_dir = lambda s, t: HERE / "raw" / (orig(s, t).name + f"_wes{s_:g}")   # own t = 0 run as well
    return m


def provenance(m, s: int) -> tuple:
    """Codex Nachtrag a: plain-init checksum + optimizer config + split/test hashes of the only-F run (shared by both s)."""
    r = json.loads((m.run_dir(s, math.inf) / "result.json").read_text(encoding="utf-8"))
    cf = r["config"]
    return (r["init_checksum_shared"], cf.get("lr"), cf.get("weight_decay"), cf.get("beta1"), cf.get("beta2"),
            cf.get("d_model"), r["split_hash"], r.get("test_hash"))


def target_displacement(m, s: int) -> dict | None:
    """Descriptive (Nachtrag a): per F target k, |coef_k(t) - coef_k(0)| / median_j |coef_j(0)| in the only-F run,
    from the stored W_E[:p] snapshots (coef = Fourier coefficients, [cos_k; sin_k] x d_model)."""
    d = m.run_dir(s, math.inf)
    try:
        snaps, steps = np.load(d / "we_snapshots.npy"), np.load(d / "we_snapshot_steps.npy").tolist()
    except OSError:
        return None
    sys.path.insert(0, str(LAB / "EXP-001-freq-ban"))
    from freq_ban import fourier_basis
    p = snaps.shape[1]
    B = fourier_basis(p)
    tg = json.loads((LAB / "EXP-020-data-switch" / f"splits/seed{s}.json").read_text(encoding="utf-8"))["targets"]["F"]
    c = [B.T @ w.astype(np.float64) for w in snaps]
    amp0 = [np.linalg.norm(c[0][2 * k - 1:2 * k + 1]) for k in range(1, (p - 1) // 2 + 1)]
    ref = float(np.median(amp0))
    return {str(st): round(float(np.mean([np.linalg.norm(c[i][2 * k - 1:2 * k + 1] - c[0][2 * k - 1:2 * k + 1])
                                          for k in tg])) / ref, 3) for i, st in enumerate(steps)}


def invariance(cells: list[dict]) -> dict | None:
    """Nachtrag b (descriptive, fixed before any run): over all complete, monotone cells of EXP-039 and EXP-040 with a
    finite interval, compare the spread of Lambda(hi) with the spread of R(hi) (target displacement / median init
    amplitude in the only-F run at step hi). H40 expects R(hi) to vary less than Lambda(hi) (coefficient of variation)."""
    lam, rr = [], []
    for c in cells:
        if c.get("lambda_hi") is None or c.get("R_hi") is None:
            continue
        lam.append(c["lambda_hi"])
        rr.append(c["R_hi"])
    if len(lam) < 4:
        return None
    cv = lambda x: float(np.std(x) / np.mean(x))  # noqa: E731
    return {"n": len(lam), "cv_lambda_hi": round(cv(lam), 3), "cv_R_hi": round(cv(rr), 3),
            "n_R_hi_in_0.5_2": sum(0.5 <= r <= 2.0 for r in rr),      # Nachtrag c: quantitative H40 expects R(hi) ~ 1
            "R_less_variable": cv(rr) < cv(lam), "lambda_hi": lam, "R_hi": rr}


def invariance_cells() -> list[dict]:
    """Collect (Lambda(hi), R(hi)) for EXP-039 (c) and EXP-040 (s) cells; relative amplitude uses the scaled init."""
    sys.path.insert(0, str(LAB / "EXP-039-lr-clock"))
    import analyze as a39  # EXP-039 module (same file name; path inserted first)
    out = []
    for kind, grids, mod in (("c", a39.GRIDS, a39.load_mod), ("s", GRIDS, load_mod)):
        for x in grids:
            m = mod(x)
            for s in SEEDS:
                try:
                    r = m.row(s)
                    if not (r["valid"] and r["monotone"] and r["hi"] != math.inf):
                        continue
                    td = target_displacement(m, s)
                    if td is None or str(int(r["hi"])) not in td:
                        continue
                    lam_hi = r["hi"] * (x if kind == "c" else 1.0)
                    out.append({"kind": kind, "x": x, "seed": s, "hi": r["hi"], "lambda_hi": lam_hi,
                                "R_hi": td[str(int(r["hi"]))]})
                except (OSError, KeyError, ValueError):
                    continue
    return out


def meta_ok(m, s_: float, s: int) -> str | None:
    ref = None
    for t in m.GRID:
        f = m.run_dir(s, t) / "result.json"
        r = json.loads(f.read_text(encoding="utf-8"))
        if float(r.get("we_init_scale", 1.0)) != s_ or float(r.get("lr_scale", 1.0)) != 1.0 or (r.get("warmup") or 0):
            return f"scale flags {f.parent.name}"
        cf = r["config"]
        key = (cf.get("lr"), cf.get("weight_decay"), cf.get("beta1"), cf.get("beta2"), r["init_checksum_shared"])
        if ref is None:
            ref = key
        elif key != ref:
            return f"config/init differs {f.parent.name}"
    return None


def cell(m, s_: float, s: int) -> dict:
    r = m.row(s)
    out = {"seed": s, "s": s_, **{k: r.get(k) for k in ("valid", "d", "K", "lo", "hi", "monotone", "gen_F", "reason")}}
    reason = r.get("reason") or ""
    if not r["valid"] and "construction did not steer" not in reason:
        return out | {"complete": False, "why": reason or "invalid run set"}
    why = meta_ok(m, s_, s)
    if why:
        return out | {"complete": False, "why": why}
    if not r["valid"]:
        return out | {"complete": True, "class": "unclear", "why": "endpoints d(0) < 0 < d(inf) not met"}
    if not r["monotone"] or not (r["gen_F"] and r["hi"] < r["gen_F"]):
        return out | {"complete": True, "class": "unclear", "why": "non-monotone or crossing not before gen_F"}
    disp = {str(t): json.loads((m.run_dir(s, t) / "result.json").read_text(encoding="utf-8"))["events"]
            .get("displacement_at_switch") for t in GRIDS[s_]}
    return out | {"complete": True, "class": LABEL[classify(EQUIV[s_], r["lo"], r["hi"])],
                  "displacement_at_switch": disp}


def main() -> None:
    rows = []
    for s_ in GRIDS:
        m = load_mod(s_)
        for s in SEEDS:
            try:
                rows.append(cell(m, s_, s))
            except (OSError, KeyError, ValueError) as e:
                rows.append({"seed": s, "s": s_, "complete": False, "why": f"{type(e).__name__}: {e}"})
    by = {(r["seed"], r["s"]): r for r in rows}
    mods = {s_: load_mod(s_) for s_ in GRIDS}
    seeds = {}
    for s in SEEDS:
        if not (by[(s, 0.5)]["complete"] and by[(s, 2.0)]["complete"]):
            continue
        if provenance(mods[0.5], s) != provenance(mods[2.0], s):     # both scales must share init/config/split
            by[(s, 0.5)]["why_seed"] = "provenance differs between scales (seed not evaluable)"
            continue
        seeds[s] = seed_class(by[(s, 0.5)]["class"], by[(s, 2.0)]["class"])
        for s_ in GRIDS:
            by[(s, s_)]["target_displacement_rel"] = target_displacement(mods[s_], s)
    out = {"rows": rows, "seed_classes": seeds, "n_seeds": len(seeds), "verdict": verdict(list(seeds.values()))}
    try:
        out["invariance_descriptive"] = invariance(invariance_cells())
    except Exception as e:  # descriptive only; must not block the verdict
        out["invariance_descriptive"] = f"failed: {type(e).__name__}: {e}"
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r)


def selftest() -> None:
    assert LABEL[classify(EQUIV[0.5], 12, 25)] == "h40" and LABEL[classify(EQUIV[0.5], 25, 50)] == "unchanged"
    assert LABEL[classify(EQUIV[2.0], 50, 100)] == "h40" and LABEL[classify(EQUIV[2.0], 25, 50)] == "unchanged"
    assert LABEL[classify(EQUIV[0.5], 10, 12)] == "unclear"
    assert seed_class("h40", "h40") == "h40" and seed_class("h40", "unchanged") == "unclear"
    assert verdict(["h40"] * 3).startswith("H40") and verdict(["h40"] * 2) == "nicht auswertbar"
    assert verdict(["unchanged"] * 3) == "Init-Skala ohne Einfluss" and verdict(["h40", "h40", "unclear"]) == "unklar"
    m = load_mod(0.5)
    assert m.GRID == (0.0, 10.0, 12.0, 25.0, 50.0, math.inf)
    assert m.run_dir(30, 0).name == "EXP-018_baseline_seed30_thr4_seed30_train_G_wes0.5"
    assert m.run_dir(30, 25).name.endswith("_at25_wes0.5") and m.run_dir(30, math.inf).name.endswith("train_F_wes0.5")
    inv = invariance([{"lambda_hi": v, "R_hi": 1.0 + 0.01 * i} for i, v in enumerate((25, 50, 12.5, 100))])
    assert inv["R_less_variable"] and inv["n"] == 4 and invariance([{"lambda_hi": 1, "R_hi": 1}]) is None
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
