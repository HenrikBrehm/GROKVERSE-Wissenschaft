"""Pre-registered prediction on the fresh N28 seeds (2200-2229): two regimes of persistence (EXP-062 exploration, session 22).
Registered in lab/experiments/EXP-062-rate-race/README.md BEFORE any N28 result was looked at. Outside the Holm family (a prediction test,
reported with its own sign counts). Run under guarded_run.py AFTER the N28 block has finished; reads only bound runs (confirm_n28 BLOCK).

Per seed s, switch time t in {25, 50} (normal arms), direction X->Y (own = X targets, new = Y targets), final W_E spectra:
  a = log E_own(switch, t + 2000) - log E_own(pure Y, 2000)       retained old energy
  b = log E_new(pure Y, 2000) - log E_new(switch, t + 2000)       missing new energy
  seed value = mean of both directions.
V1 (coexistence at t = 25): a25 - b25 > 0 in >= 24 of 30 seeds.   V2 (exclusion at t = 50): b50 - b25 > 0.5 in >= 24 of 30 seeds.
Verdict: both -> "zwei Regime bestätigt (Vorhersage)"; exactly one -> "teilweise"; none -> "nicht bestätigt"; any missing/unbound run -> "nicht auswertbar".
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools"))
import confirm_n28 as n  # noqa: E402

MAN = LAB / "confirm" / "N28_manifest.json"
NEED, MARGIN = 24, 0.5


def spectra_of(man: dict, s: int, first: str, second: str | None, t: int | None) -> dict[int, np.ndarray] | str:
    cmd = ["x", n.FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", man["device"], "--split-file", str(n.SPL / f"{n.stem(s, first)}.npy")]
    if second:
        cmd += ["--switch-split-file", str(n.SPL / f"{n.stem(s, second)}.npy"), "--switch-step", str(t)]
    d = n.run_dir(cmd)
    if not d.exists():
        return "fehlt"
    if (why := n.BLOCK.unbound(man, d)):
        return f"defekt: {why}"
    sp, st = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy")
    if (why := n.BLOCK.unbound(man, d)):
        return f"defekt after load: {why}"
    return {int(k): sp[i] for i, k in enumerate(st)}


def ab(sw: dict, pure: dict, own: list[int], new: list[int], k_sw: int) -> tuple[float, float]:
    e = lambda spec, T: float(spec[[k - 1 for k in T]].sum())   # noqa: E731
    return (float(np.log(e(sw[k_sw], own)) - np.log(e(pure[2000], own))), float(np.log(e(pure[2000], new)) - np.log(e(sw[k_sw], new))))


def verdict(v1: np.ndarray, v2: np.ndarray, n_planned: int) -> dict:
    if len(v1) != n_planned or len(v2) != n_planned:
        return {"verdict": "nicht auswertbar"}
    k1, k2 = int((v1 > 0).sum()), int((v2 > MARGIN).sum())
    ok1, ok2 = k1 >= NEED, k2 >= NEED
    return {"V1_count": k1, "V2_count": k2, "V1": ok1, "V2": ok2, "V1_mean": float(v1.mean()), "V2_mean": float(v2.mean()),
            "verdict": "zwei Regime bestätigt (Vorhersage)" if ok1 and ok2 else ("teilweise" if ok1 or ok2 else "nicht bestätigt")}


def main() -> None:
    man = json.loads(MAN.read_text(encoding="utf-8"))
    n.BLOCK.check_manifest(MAN, man)
    rows, v1, v2 = [], [], []
    for s in man["seeds"]:
        meta = json.loads((n.SPL / f"n28_seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        pure = {x: spectra_of(man, s, x, None, None) for x in "AB"}
        vals, bad = {}, []
        for t in (25, 50):
            aa, bb = [], []
            for first, second, own, new in (("A", "B", F, G), ("B", "A", G, F)):
                sw = spectra_of(man, s, first, second, t)
                if isinstance(sw, str) or isinstance(pure[second], str):
                    bad.append(f"{first}{second}@{t}: {sw if isinstance(sw, str) else pure[second]}")
                    continue
                a, b = ab(sw, pure[second], own, new, t + 2000)
                aa.append(a)
                bb.append(b)
            if len(aa) == 2:
                vals[t] = (float(np.mean(aa)), float(np.mean(bb)))
        if bad or len(vals) != 2 or not all(np.isfinite(x) for v in vals.values() for x in v):
            rows.append({"seed": s, "valid": False, "reason": "; ".join(bad[:2]) or "non-finite"})
            continue
        rows.append({"seed": s, "valid": True, "a25": vals[25][0], "b25": vals[25][1], "a50": vals[50][0], "b50": vals[50][1]})
        v1.append(vals[25][0] - vals[25][1])
        v2.append(vals[50][1] - vals[25][1])
    out = {"manifest_commit": man["commit"], **verdict(np.array(v1), np.array(v2), len(man["seeds"])), "rows": rows}
    (LAB / "confirm" / "N28_regimes_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    assert verdict(np.ones(29), np.ones(30), 30)["verdict"] == "nicht auswertbar"
    assert verdict(np.ones(30), np.ones(30), 30)["verdict"] == "zwei Regime bestätigt (Vorhersage)"
    assert verdict(np.r_[np.ones(23), -np.ones(7)], np.ones(30), 30)["verdict"] == "teilweise"
    assert verdict(-np.ones(30), np.full(30, 0.4), 30)["verdict"] == "nicht bestätigt"
    sw, pure = {2025: np.array([4.0, 1.0])}, {2000: np.array([1.0, 2.0])}
    a, b = ab(sw, pure, [1], [2], 2025)
    assert abs(a - np.log(4)) < 1e-12 and abs(b - np.log(2)) < 1e-12
    print("[n28_regimes] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
