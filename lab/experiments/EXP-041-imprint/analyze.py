"""EXP-041 analysis (pre-registered, README incl. Nachtrag a after Codex): does a 150-step prefix imprint the frequency
choice when the rest of training uses a different split, in both directions (engineered E -> random R, R -> E)?
Splits of EXP-018 (seeds 20-29, common test set).
Symmetric references (Nachtrag a): Ex = K_E u fold(2 K_E), Rx = K_R u fold(2 K_R), K_X = top-5 of W_E of the pure-X run
of the same init at step 2000 (exposure-matched); frequencies in both removed. d(K) = |K n Ex| - |K n Rx|.
Seed valid: all 4 runs pass the manifest loader, same init checksum and config, |Ex| >= 3 and |Rx| >= 3 after removal
(no direction-specific outcome gate).
P41a (E -> R at 150), confirmatory one-sided: held = d > 0; P(X >= held | Bin(m, 1/2)) < 0.025 -> gepraegt;
  else 'nicht gezeigt'.
P41b (R -> E at 150), two-sided: 2 * min tail < 0.025 -> gepraegt (held = d < 0 dominates) or ueberschrieben (d > 0
  dominates); else gemischt. d = 0 counts for neither side. m < 8 -> nicht auswertbar (both).
Descriptive: K at step 2150 of the pure runs (clock-matched) and stability 2000 -> 2150; direction of the prefix at the
switch (pure runs' top-5 at step 150 against Ex/Rx); test accuracies.
Usage: python analyze.py [--selftest]"""
from __future__ import annotations

import json
import sys
from math import comb
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[0]
SPL = LAB / "EXP-018-split-speed" / "splits"
sys.path.insert(0, str(LAB.parent.parent / "training"))
from grokverse.data import split_hash  # noqa: E402

P, M, G_BUDGET, MIN_SEEDS, ALPHA_EACH = 113, 5, 2000, 8, 0.025
SEEDS = range(20, 30)
PURE_STEPS = 2150                     # pure runs: K at 2000 (exposure-matched) and 2150 (clock-matched)
RUNS = {"R": ("R", None, None), "E": ("E", None, None), "ER150": ("E", "R", 150), "RE150": ("R", "E", 150)}


def fold(k: int) -> int:
    k %= P
    return min(k, P - k)


def tail(k: int, n: int) -> float:
    """P(X >= k), X ~ Bin(n, 1/2)."""
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n


def run_dir(s: int, key: str) -> Path:
    a, b, t = RUNS[key]
    if b is None:
        return HERE / "raw" / f"EXP-018_baseline_seed{s}_thr4_seed{s}_train_{a}"
    return HERE / "raw" / f"EXP-020_baseline_seed{s}_thr4_seed{s}_train_{a}_to_seed{s}_train_{b}_at{t}"


def top_at(d: Path, step: int) -> set[int] | None:
    spec, steps = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()
    if step not in steps:
        return None
    pw = spec[steps.index(step)]
    return {int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:M]}


def load(s: int, key: str) -> tuple[dict | None, str | None]:
    """Manifest loader (Nachtrag a): identity, schema, steps, hashes, switch, config."""
    a, b, t = RUNS[key]
    d = run_dir(s, key)
    try:
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, f"{key}: unreadable ({type(e).__name__})"
    want = PURE_STEPS if t is None else G_BUDGET + t
    if (r.get("status") != "completed" or r.get("seed") != s or r.get("run_id") != d.name
            or r.get("condition") != "baseline" or r.get("m") != M or r.get("max_steps") != want
            or r.get("steps_completed") != want or r.get("stop_after_generalization") != 8000
            or (r.get("warmup") or 0) or float(r.get("lr_scale", 1.0)) != 1.0
            or float(r.get("we_init_scale", 1.0)) != 1.0 or r.get("alternate_every") or r.get("reset_at_switch")):
        return None, f"{key}: manifest"
    K = r.get("final_top_m_freqs")
    if not (isinstance(K, list) and len(K) == M and len(set(K)) == M and all(isinstance(k, int) and 1 <= k <= 56
                                                                             for k in K)):
        return None, f"{key}: frequency list"
    if r.get("split_hash") != split_hash(np.load(SPL / f"seed{s}_train_{a}.npy")):
        return None, f"{key}: split hash"
    if r.get("test_hash") != split_hash(np.load(SPL / f"seed{s}_test.npy")):
        return None, f"{key}: test hash"
    if t is not None:
        sw = r.get("events", {}).get("switch", {})
        new = split_hash(np.load(SPL / f"seed{s}_train_{b}.npy"))
        if r.get("switch_step") != t or sw.get("step") != t or sw.get("new_train_hash") != new or r.get("switch_hash") != new:
            return None, f"{key}: switch not as specified"
    return r, None


def d_value(K: set[int], ex: set[int], rx: set[int]) -> int:
    shared = ex & rx
    return len(K & (ex - shared)) - len(K & (rx - shared))


def verdict_a(held: int, m: int) -> str:
    if m < MIN_SEEDS:
        return "nicht auswertbar"
    return "gepraegt" if tail(held, m) < ALPHA_EACH else "nicht gezeigt"


def verdict_b(held: int, flipped: int, m: int) -> str:
    if m < MIN_SEEDS:
        return "nicht auswertbar"
    if 2 * tail(held, m) < ALPHA_EACH:
        return "gepraegt"
    return "ueberschrieben" if 2 * tail(flipped, m) < ALPHA_EACH else "gemischt"


def config_key(r: dict) -> tuple:
    c = r["config"]
    return (r["init_checksum_shared"], c.get("lr"), c.get("weight_decay"), c.get("beta1"), c.get("beta2"),
            c.get("d_model"), c.get("threads"))


def seed_row(s: int) -> dict:
    runs = {}
    for key in RUNS:
        r, err = load(s, key)
        if err:
            return {"seed": s, "valid": False, "why": err}
        runs[key] = r
    if len({config_key(r) for r in runs.values()}) != 1:
        return {"seed": s, "valid": False, "why": "init/config differs"}
    K = {"R": top_at(run_dir(s, "R"), G_BUDGET), "E": top_at(run_dir(s, "E"), G_BUDGET)}
    if None in K.values():
        return {"seed": s, "valid": False, "why": "pure run lacks spectrum at 2000"}
    K |= {k: set(runs[k]["final_top_m_freqs"]) for k in ("ER150", "RE150")}
    ex = K["E"] | {fold(2 * k) for k in K["E"]}
    rx = K["R"] | {fold(2 * k) for k in K["R"]}
    shared = ex & rx
    row = {"seed": s, "K": {k: sorted(v) for k, v in K.items()}, "d": {k: d_value(v, ex, rx) for k, v in K.items()},
           "test_acc": {k: r["final_acc"]["test"] for k, r in runs.items()},
           "descr": {"K_2150": {x: sorted(runs[x]["final_top_m_freqs"]) for x in ("R", "E")},
                     "stable_2000_2150": {x: set(runs[x]["final_top_m_freqs"]) == K[x] for x in ("R", "E")},
                     "d_prefix_at_150": {x: (None if top_at(run_dir(s, x), 150) is None
                                             else d_value(top_at(run_dir(s, x), 150), ex, rx)) for x in ("R", "E")}}}
    if len(ex - shared) < 3 or len(rx - shared) < 3:
        return row | {"valid": False, "why": "references not discriminable (< 3 exclusive frequencies)"}
    return row | {"valid": True}


def main() -> None:
    rows = [seed_row(s) for s in SEEDS]
    ok = [r for r in rows if r["valid"]]
    m = len(ok)
    ha = sum(r["d"]["ER150"] > 0 for r in ok)
    hb, fb = sum(r["d"]["RE150"] < 0 for r in ok), sum(r["d"]["RE150"] > 0 for r in ok)
    out = {"rows": rows, "n_valid": m,
           "P41a_ER150": {"held": ha, "m": m, "p_one_sided": tail(ha, m) if m else None, "verdict": verdict_a(ha, m)},
           "P41b_RE150": {"held": hb, "flipped": fb, "m": m, "verdict": verdict_b(hb, fb, m)}}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r)


def selftest() -> None:
    assert d_value({1, 2, 3, 4, 5}, {1, 2, 3}, {4, 9}) == 2
    assert d_value({1, 4}, {1, 4}, {4, 9}) == 1                 # shared frequency 4 counts for neither side
    assert verdict_a(7, 7) == "nicht auswertbar"
    assert verdict_a(8, 8) == "gepraegt" and verdict_a(7, 8) == "nicht gezeigt"       # 7/8: p = 0.035
    assert verdict_a(9, 10) == "gepraegt"                                               # p = 0.0107
    assert verdict_b(9, 1, 10) == "gepraegt" and verdict_b(1, 9, 10) == "ueberschrieben"  # 2 * 0.0107
    assert verdict_b(8, 2, 10) == "gemischt"                                            # 2 * 0.0547
    assert verdict_b(5, 5, 10) == "gemischt"
    assert fold(2 * 60) == 7
    assert run_dir(20, "RE150").name == "EXP-020_baseline_seed20_thr4_seed20_train_R_to_seed20_train_E_at150"
    assert run_dir(20, "R").name == "EXP-018_baseline_seed20_thr4_seed20_train_R"
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
