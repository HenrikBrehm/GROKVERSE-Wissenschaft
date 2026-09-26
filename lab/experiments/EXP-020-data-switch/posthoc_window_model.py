"""Post hoc (session 15, exploratory): an integration-window model for the persistence pi.

Model W (one parameter T*): every training step s in 1..T* contributes equally to the final F/G mix, later steps contribute nothing;
pi = (# F steps among 1..T*) / T*. Model E (one parameter tau): step s contributes exp(-s / tau). Both fitted per seed and on the seed
mean to the EXP-020 end values pi(t), t = 10, 25, 50, 150 (posthoc_beta_persistence.json), then used to predict the EXP-037
alternation arms (block k of A steps on F for odd k, G for even k, steps 1..200; afterwards G), which were NOT used for fitting.
Null "only the first F block counts": pi(A) interpolated from the EXP-020 curve. Pure numpy on stored numbers; no training.
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TS = (10, 25, 50, 150)


def f_mask(schedule: str, n: int) -> np.ndarray:
    s = np.arange(1, n + 1)
    if schedule.startswith("switch"):
        return s <= int(schedule[6:])
    a = int(schedule[3:])                       # "alt5", "alt25": block k = (s - 1) // a + 1, F if k odd
    return ((s - 1) // a) % 2 == 0


def pred(model: str, par: float, schedule: str) -> float:
    n = 5000
    s = np.arange(1, n + 1)
    w = (s <= par).astype(float) if model == "W" else np.exp(-s / par)
    if model == "W" and par % 1:               # fractional window end: partial weight on the last step
        w[int(par)] = par % 1
    return float((w * f_mask(schedule, n)).sum() / w.sum())


def fit(model: str, pis: dict[int, float]) -> float:
    grid = np.linspace(10, 300, 2901)
    err = [sum((pred(model, g, f"switch{t}") - p) ** 2 for t, p in pis.items()) for g in grid]
    return float(grid[int(np.argmin(err))])


def main() -> None:
    base = json.loads((HERE / "posthoc_beta_persistence.json").read_text(encoding="utf-8"))["switch"]
    obs37 = json.loads((HERE / "posthoc_pi_other.json").read_text(encoding="utf-8"))["EXP-037"]
    seeds = ("30", "31", "32")                   # EXP-037 seeds; fit on the same seeds' EXP-020 curves
    curve_t = np.array((0,) + TS)
    out: dict = {"fit": {}, "pred": {}}
    for key in seeds + ("mean",):
        pis = {t: (float(np.mean([base[str(t)]["pi"][s] for s in base[str(t)]["pi"]])) if key == "mean"
                   else base[str(t)]["pi"][key]) for t in TS}
        par = {m: fit(m, pis) for m in "WE"}
        rmse_fit = {m: float(np.sqrt(np.mean([(pred(m, par[m], f"switch{t}") - pis[t]) ** 2 for t in TS]))) for m in "WE"}
        out["fit"][key] = {"par": par, "rmse_fit": rmse_fit}
        if key == "mean":
            continue
        curve = np.array([0.0] + [pis[t] for t in TS])
        for arm, sch in (("at200_alt25", "alt25"), ("at200_alt5", "alt5")):
            o = obs37[f"seed{key}_{arm}"]
            null = float(np.interp(int(sch[3:]), curve_t, curve))
            out["pred"][f"seed{key}_{arm}"] = {"obs": o, "W": pred("W", par["W"], sch), "E": pred("E", par["E"], sch),
                                               "null_first_block": null}
    for m in ("W", "E", "null_first_block"):
        e = [v[m] - v["obs"] for v in out["pred"].values()]
        out.setdefault("rmse_exp037", {})[m] = float(np.sqrt(np.mean(np.square(e))))
        out.setdefault("mean_err_exp037", {})[m] = float(np.mean(e))
    (HERE / "posthoc_window_model.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out["fit"], indent=0))
    for k, v in out["pred"].items():
        print(k, {a: round(b, 3) for a, b in v.items()})
    print("RMSE EXP-037:", {a: round(b, 3) for a, b in out["rmse_exp037"].items()},
          "mean error:", {a: round(b, 3) for a, b in out["mean_err_exp037"].items()})


if __name__ == "__main__":
    main()
