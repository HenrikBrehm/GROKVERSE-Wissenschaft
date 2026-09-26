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

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[0]
sys.path.insert(0, str(LAB / "EXP-039-lr-clock"))
from analyze import classify, seed_class  # noqa: E402  (EXP-039)

SEEDS = (30, 32, 34, 31)
EQUIV = {0.5: 2.0, 2.0: 0.5}          # s -> lr scale c with the same predicted interval under H40
GRIDS = {0.5: (10, 12, 25, 50), 2.0: (25, 50, 100, 150)}
LABEL = {"lambda": "h40", "step": "unchanged", "unclear": "unclear"}
MIN_SEEDS = 3


def verdict(classes: list[str]) -> str:
    if len(classes) < MIN_SEEDS:
        return "nicht auswertbar"
    if all(c == "h40" for c in classes):
        return "H40 gestuetzt (Festlegung haengt an der Init-Amplitude von W_E)"
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
    seeds = {s: seed_class(by[(s, 0.5)]["class"], by[(s, 2.0)]["class"]) for s in SEEDS
             if by[(s, 0.5)]["complete"] and by[(s, 2.0)]["complete"]}
    out = {"rows": rows, "seed_classes": seeds, "n_seeds": len(seeds), "verdict": verdict(list(seeds.values()))}
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
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
