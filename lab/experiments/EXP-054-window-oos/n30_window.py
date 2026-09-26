"""EXP-054 (session 15, frozen before any EXP-036 run; analysis only, reads the EXP-036 runs; EXP-036 verdicts unchanged): N30 out of sample.

The EXP-036 runs reuse the EXP-020 splits with NEW inits (130-134, 230, 231; unseen) and store dense spectra (5 ... 200). Two frozen checks of
the post-hoc window picture from EXP-020/037 (T* = 69 fitted there, not refitted here):
  A (window transfers): mean pi_end over valid pairs within 0.12 of min(1, t / 69) = 0.145 / 0.362 / 0.725 at t = 10 / 25 / 50, all three.
  B (mix set early): per switch run, settle step = first stored step s > t with |pi(s') - pi_end| <= 0.1 for every stored s' >= s up to 2000
    (pi(s) normalised with the pure runs of the same init at step s; only steps with D_F - D_G >= 1). Median settle step for t = 25 and 50
    <= 150 -> 'frueh gesetzt'; > 200 -> 'spaeter gesetzt'; else 'dazwischen'.
pi as in EXP-020/posthoc_beta_persistence.py (log-log slope on M0 of F resp. G). >= 5 valid pairs, else 'nicht auswertbar'.
UNTESTED (window closed). Usage: python n30_window.py [--selftest]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
E20 = HERE.parent / "EXP-020-data-switch"
RAW36 = HERE.parent / "EXP-036-init-conflict" / "raw"
sys.path.insert(0, str(E20))
sys.path.insert(0, str(HERE.parent / "EXP-043-generalize-steering"))
from conflict_freqs import load_run  # noqa: E402
from make_split import mask_power  # noqa: E402

PAIRS = ((30, 130), (31, 131), (32, 132), (33, 133), (34, 134), (30, 230), (31, 231))
TS, T_STAR, TOL_A, TOL_B, MIN_DEN, MIN_PAIRS = (10, 25, 50), 69.0, 0.12, 0.1, 1.0, 5
STEPS = (15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 250, 500, 750, 1000, 1250, 1500, 1750, 2000)


def beta(m0: np.ndarray, pw: np.ndarray) -> float:
    return float(np.polyfit(np.log(m0), np.log(pw), 1)[0])


def settle(traj: dict[int, float], end: float) -> int | None:
    ok = None
    for s in sorted(traj, reverse=True):
        if abs(traj[s] - end) > TOL_B:
            break
        ok = s
    return ok


def read_A(means: dict[int, float]) -> str:
    dev = {t: means[t] - min(1.0, t / T_STAR) for t in TS}
    return ("Fenster uebertragbar" if all(abs(d) <= TOL_A for d in dev.values()) else "Fenster nicht uebertragbar") + f", dev {dev}"


def read_B(med: float | None) -> str:
    if med is None:
        return "nicht auswertbar"
    return "frueh gesetzt" if med <= 150 else ("spaeter gesetzt" if med > 200 else "dazwischen")


def pair(s: int, init: int) -> dict:
    M = {a: mask_power(np.load(E20 / f"splits/seed{s}_train_{a}.npy"), "add", 113) for a in "FG"}
    D = lambda pw: beta(M["F"], pw) - beta(M["G"], pw)  # noqa: E731
    pure = {}
    for a in "FG":
        r, err = load_run(RAW36, init, s, a, None, 2000, STEPS)
        if err:
            raise ValueError(err)
        pure[a] = r["spec"]
    out = {}
    for t in TS:
        st = tuple(x for x in STEPS if x > t)
        r, err = load_run(RAW36, init, s, "FG", t, None, st + (t + 2000,))
        if err:
            raise ValueError(err)
        dF, dG = D(pure["F"][2000]), D(pure["G"][2000])
        end = (D(r["spec"][t + 2000]) - dG) / (dF - dG)
        traj = {}
        for x in st:
            f, g = D(pure["F"][x]), D(pure["G"][x])
            if f - g >= MIN_DEN:
                traj[x] = (D(r["spec"][x]) - g) / (f - g)
        if not all(np.isfinite([end, *traj.values()])):
            raise ValueError(f"non-finite pi pair ({s},{init}) t {t}")
        out[t] = {"pi_end": end, "traj": traj, "settle": settle(traj, end)}
    return out


def main() -> None:
    rows = {}
    for s, i in PAIRS:
        try:
            rows[f"{s}_{i}"] = pair(s, i)
        except (OSError, KeyError, ValueError) as ex:
            rows[f"{s}_{i}"] = {"missing_or_broken": f"{type(ex).__name__}: {ex}"}
    valid = [r for r in rows.values() if "missing_or_broken" not in r]
    res = {"rows": rows, "n_valid": len(valid)}
    if len(valid) < MIN_PAIRS:
        res["A"] = res["B"] = "nicht auswertbar"
    else:
        means = {t: float(np.mean([r[t]["pi_end"] for r in valid])) for t in TS}
        sets = [r[t]["settle"] for r in valid for t in (25, 50)]
        med = float(np.median([x if x is not None else 10 ** 6 for x in sets]))
        res.update({"mean_pi_end": means, "A": read_A(means), "median_settle_25_50": med, "B": read_B(med)})
    (HERE / "summary_n30_window.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print(res.get("mean_pi_end"), res["A"], res.get("median_settle_25_50"), res["B"])


def selftest() -> None:
    assert settle({100: 0.5, 150: 0.38, 200: 0.36}, 0.37) == 150 and settle({100: 0.5}, 0.1) is None
    assert read_A({10: 0.15, 25: 0.38, 50: 0.72}).startswith("Fenster uebertragbar")
    assert read_A({10: 0.15, 25: 0.1, 50: 0.72}).startswith("Fenster nicht")
    assert read_B(150) == "frueh gesetzt" and read_B(250) == "spaeter gesetzt" and read_B(175) == "dazwischen"
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
