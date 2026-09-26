"""EXP-010: does the final frequency set follow swapped init coefficients? (UNTESTED)

Read-only analysis. Baselines: EXP-003d raw_d (freq_ban.py baseline, seeds 10-19, stop-after-gen 25).
Swaps: raw/ (freq_ban.py init_swap). Definition and decision rule: README.md.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import sys

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-001-freq-ban"))
import freq_ban as fb  # noqa: E402
BASE = LAB / "experiments/EXP-003-early-prediction/raw_d/EXP-001_baseline_t2000_m5_seed{s}_thr4"
SWAP = HERE / "raw/EXP-010_init_swap_t2000_m5_seed{s}_thr4"
SEEDS = range(10, 20)
M, N_FREQ = 5, 56
ALPHA, MIN_VALID = 0.05, 8
N_MC, MC_SEED = 100_000, 0


def load(d: Path) -> tuple[dict, np.ndarray, list[int]]:
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    return res, np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()


def _top(power, m: int = M) -> set[int]:
    return set(fb.top_frequencies(np.asarray(power), m))


def _check(base: dict, swap: dict, seed: int, event_key: str, base_spec, base_steps) -> str | None:
    """Fail-closed validity of a pair (Nachtrag a, 2026-09-26, after Codex review, before results)."""
    if base["status"] != "completed" or swap["status"] != "completed":
        return f"status base={base['status']} swap={swap['status']}"
    if (base["seed"], swap["seed"]) != (seed, seed):
        return "seed metadata"
    if base["condition"] != "baseline" or swap["condition"] != event_key:
        return "condition metadata"
    for key in ("m", "max_steps", "stop_after_generalization", "config", "versions", "split_hash"):
        if base.get(key) != swap.get(key):
            return f"{key} differs"
    ev = swap["events"].get(event_key)
    if ev is None:
        return "intervention event missing"
    if not np.allclose(base_spec[base_steps.index(0)], ev["power_before"], rtol=1e-5):
        return "baseline init spectrum != swap power_before"
    expected = [list(t) for t in fb.swap_pairs(np.asarray(ev["power_before"]), M, seed + fb.SWAP_SALT)]
    if [list(t) for t in ev["pairs"]] != expected:
        return "pairs differ from the pre-registered construction"
    after = np.asarray(ev["power_before"]).copy()
    for k, j in ev["pairs"]:
        after[[k - 1, j - 1]] = after[[j - 1, k - 1]]
    if not np.allclose(after, ev["power_after"], rtol=1e-5):
        return "power_after is not the swapped spectrum"
    if base["events"].get("generalization_step") is None or swap["events"].get("generalization_step") is None:
        return "an arm did not cross (capped run)"
    return None


def pair(seed: int, swap_tmpl: Path = SWAP, event_key: str = "init_swap") -> dict:
    row: dict = {"seed": seed, "valid": False}
    try:
        base, base_spec, base_steps = load(Path(str(BASE).format(s=seed)))
        swap, swap_spec, swap_steps = load(Path(str(swap_tmpl).format(s=seed)))
    except FileNotFoundError as e:
        row["reason"] = f"missing: {e.filename}"
        return row
    reason = _check(base, swap, seed, event_key, base_spec, base_steps)
    if reason:
        row["reason"] = reason
        return row
    ev = swap["events"][event_key]
    T = {k for k, _ in ev["pairs"]}
    S = {j for _, j in ev["pairs"]}
    kb, ks = set(base["final_top_m_freqs"]), set(swap["final_top_m_freqs"])
    d = (len(ks & S) - len(ks & T)) - (len(kb & S) - len(kb & T))
    gb, gs = base["events"]["generalization_step"], swap["events"]["generalization_step"]
    # secondary (Nachtrag a): K at a common training step = last stored spectrum step <= min(gen)
    common = max(t for t in base_steps if t <= min(gb, gs) and t in swap_steps)
    cb, cs = _top(base_spec[base_steps.index(common)]), _top(swap_spec[swap_steps.index(common)])
    init_rank = np.argsort(np.argsort(-np.asarray(ev["power_before"]), kind="stable"), kind="stable")
    row.update({"valid": True, "T": sorted(T), "S": sorted(S), "K_base": sorted(kb),
                "K_swap": sorted(ks), "d": d, "gen_base": gb, "gen_swap": gs,
                # co-primary since Nachtrag a (2026-09-26, before any result): d = gain_S + loss_T
                "gain_S": len(ks & S) - len(kb & S), "loss_T": len(kb & T) - len(ks & T),
                "common_step": common,
                "d_common": (len(cs & S) - len(cs & T)) - (len(cb & S) - len(cb & T)),
                "delta_gen": gs - gb,
                "rbar0_base": float((init_rank[[k - 1 for k in kb]] / (N_FREQ - 1)).mean())})
    return row


def sign_flip_p(d: np.ndarray) -> float:
    obs = d.mean()
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= obs - 1e-12).mean())


def main() -> None:
    rows = [pair(s) for s in SEEDS]
    valid = [r for r in rows if r["valid"]]
    out: dict = {"rows": rows, "n_valid": len(valid)}
    if len(valid) < MIN_VALID:
        out["verdict"] = "nicht auswertbar"
    else:
        d = np.array([r["d"] for r in valid], dtype=float)
        g = np.array([r["gain_S"] for r in valid], dtype=float)
        p, p_gain = sign_flip_p(d), sign_flip_p(g)
        dc = np.array([r["d_common"] for r in valid], dtype=float)
        out.update({"d_mean": float(d.mean()), "p": p,
                    "gain_S_mean": float(g.mean()), "p_gain_S": p_gain,
                    "loss_T_mean": float(np.mean([r["loss_T"] for r in valid])),
                    "d_common_mean": float(dc.mean()), "p_d_common": sign_flip_p(dc),
                    # Nachtrag a: "steuerbar" needs d AND the gain of S (co-primary)
                    "verdict": "widerspricht" if d.mean() <= 0 else
                    ("steuerbar" if p < ALPHA and g.mean() > 0 and p_gain < ALPHA else
                     ("Störung ohne nachweisbare Umlenkung" if p < ALPHA else
                      "richtungsgleich, nicht signifikant"))})
        rng = np.random.default_rng(MC_SEED)
        picks = rng.random((N_MC, len(valid), N_FREQ)).argsort(axis=2)[:, :, :M]
        null = (picks / (N_FREQ - 1)).mean(axis=(1, 2))
        rbar = float(np.mean([r["rbar0_base"] for r in valid]))
        p9 = float((np.sum(null <= rbar) + 1) / (N_MC + 1))
        out["exp009_replication"] = {"rbar0": rbar, "p": p9,
                                     "verdict": "repliziert" if p9 < ALPHA else "nicht repliziert"}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
