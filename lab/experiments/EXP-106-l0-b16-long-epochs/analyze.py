"""EXP-106 analysis (exploration; session 46, written BEFORE any EXP-106 run). README.md. Global python, under the guard:
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-106-l0-b16-long-epochs/analyze.py [--selftest]

Per seed and arm, through the shared loader (seed, device cuda, max_steps 30 000, split/test hashes, p 113 / add / weight
decay 0.1; recorded batch_size and order; minibatch event), final W_E group power (EXP-043 basis):
  dpow(arm)  = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)]   (P1 definition, confirm_p1.delta_pow_checked)
  o(run)     = share of the group power on O = {11, 12, 22, 23, 34, 45}; peak(run) = strongest frequency
  t_gen(run) = first step with test accuracy >= 0.95 (trainer transitions, primary thresholds)
Readings, fixed HERE before the runs (bootstrap over seeds, 10 000, rng 100, as EXP-100):
  K2-B16     'Menge steuert bei B = 16'  dpow_end(iid16w) CI lower > 0;  'kaum'  CI upper < 1;  else 'gemischt'
  Konflikt   EXP-100 conflict_reading (Fassung 2) for stride16w against iid16w, identical rules:
             order_acts = R-alone 'wirkt' OR CI lower of o(stride16w) - o(iid16w) on F/G > 0; not order_acts -> 'nicht pruefbar';
             'Menge gewinnt' dpow_end(stride16w) CI lower > 0 and stride peak outside O in >= 75 % of the runs;
             'Reihenfolge gewinnt' stride peak in O in >= 75 % and dpow_end(stride16w) CI lower <= 0; else 'beide wirken'.
  Zeit       descriptive: paired log2 t_gen(stride16w) / t_gen(iid16w) over the F/G runs where both generalise, mean and CI
             (the B16 probe v3 showed ~ +0.3 log2 on R, 3/3 seeds, seen); count of runs that never generalise per arm.
  Referenz   descriptive: dpow_end(fbw) and its CI (K2 at weight decay 0.1, full batch, same 30 000 steps).
Valid seed: fbw, iid16w and stride16w on F and G all load 'ok' with finite dpow. Fewer than 6 valid seeds -> 'nicht auswertbar'.
Seeds 3700-3702 on R with iid16w/stride16w repeat the probe v3 configuration (seen before this design) -> R-alone is also
reported without them (descriptive).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(HERE))
from result_loader import Expect, find_run, load_run  # noqa: E402
import confirm_p1 as c1  # noqa: E402
import design as D  # noqa: E402


def _mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_a43 = _mod("exp043_analyze", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
_a100 = _mod("exp100_analyze", LAB / "experiments/EXP-100-set-vs-order/analyze.py")   # conflict_reading, boot_ci (read only)
SPL = LAB / "experiments/EXP-100-set-vs-order/splits"
SEEN_R = (3700, 3701, 3702)
MIN_VALID = 6


def suffix(arm: str) -> str:
    bs, order = D.ARMS[arm]
    return (f"_bs{bs}" if bs else "") + ("_ordstride" if order == "stride" else "") + "_wd0.1"


def load(s: int, split: str, arm: str, root: Path | None = None):
    bs, order = D.ARMS[arm]
    pat = f"EXP-018_baseline_seed{s}_thr*_seed{s}_{split}{suffix(arm)}_devcuda"
    L = load_run(find_run(root or HERE / "raw", pat),
                 Expect(seed=s, device="cuda", max_steps=D.BUDGET, split_file=SPL / f"seed{s}_{split}.npy",
                        test_file=SPL / f"seed{s}_test.npy", config={"p": 113, "task": "add", "weight_decay": D.WD},
                        snapshots_at=(D.BUDGET,)))
    tag = f"seed {s} {split} {arm}"
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    r = L.res
    if r.get("batch_size", 0) != bs or r.get("order", "iid") != order or r.get("optimizer", "adamw") != "adamw":
        return f"{tag}: recorded batch/order/optimizer differ from the arm"
    if bs and r.get("events", {}).get("minibatch", {}).get("batch_size") != bs:
        return f"{tag}: minibatch event missing"
    end = _a43.group_power(L.snapshot(D.BUDGET), "add", 113)[0]
    if not np.isfinite(end).all():
        return f"{tag}: non-finite power"
    gen = (r.get("transitions") or {}).get("primary", {}).get("generalization", {}).get("first_crossing_step")
    return {"end": end, "t_gen": gen}


def o_share(pw: np.ndarray) -> float:
    return float(pw[[k - 1 for k in D.O]].sum() / pw.sum())


def peak_in_o(pw: np.ndarray) -> bool:
    return int(np.argmax(pw)) + 1 in D.O


def seed_row(s: int, loader=load) -> dict:
    meta = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["F"], meta["targets"]["G"]
    runs = {(x, arm): loader(s, x, arm) for arm in D.ARMS for x in "FG"}
    runs.update({("R", arm): loader(s, "R", arm) for arm in D.R_ARMS})
    row: dict = {"seed": s, "errors": [v for v in runs.values() if isinstance(v, str)]}
    for arm in D.ARMS:
        a, b = runs[("F", arm)], runs[("G", arm)]
        if isinstance(a, str) or isinstance(b, str):
            continue
        de = c1.delta_pow_checked(a["end"], b["end"], F, G)
        if de is None:
            row["errors"].append(f"seed {s} {arm}: delta_pow not finite")
            continue
        row[f"dpow_end_{arm}"] = de
        row[f"o_{arm}"] = (o_share(a["end"]) + o_share(b["end"])) / 2
        row[f"peakO_{arm}"] = [peak_in_o(a["end"]), peak_in_o(b["end"])]
        row[f"tgen_{arm}"] = [a["t_gen"], b["t_gen"]]
    for arm in D.R_ARMS:
        r = runs[("R", arm)]
        if not isinstance(r, str):
            row[f"R_o_{arm}"], row[f"R_peakO_{arm}"] = o_share(r["end"]), peak_in_o(r["end"])
    row["valid"] = all(f"dpow_end_{arm}" in row for arm in D.ARMS)
    return row


def verdict(rows: list[dict]) -> dict:
    ok = [r for r in rows if r["valid"]]
    if len(ok) < MIN_VALID:
        return {"n": len(ok), "K2_B16": "nicht auswertbar", "Konflikt": "nicht auswertbar"}
    col = lambda k, rs=ok: np.array([r[k] for r in rs], dtype=float)   # noqa: E731
    ci = {arm: _a100.boot_ci(col(f"dpow_end_{arm}")) for arm in D.ARMS}
    k2 = ("Menge steuert bei B = 16" if ci["iid16w"][0] > 0 else "kaum" if ci["iid16w"][1] < 1 else "gemischt")
    c = _a100.conflict_reading(ok, col, "stride16w", "iid16w", ci["stride16w"])
    lr = [np.log2(a / b) for r in ok for a, b in zip(r["tgen_stride16w"], r["tgen_iid16w"]) if a and b]
    unseen = [r for r in ok if r["seed"] not in SEEN_R and "R_o_stride16w" in r and "R_o_iid16w" in r]
    return {"n": len(ok), "K2_B16": k2, "Konflikt": c["conflict"], "Reihenfolge_allein": c["alone"],
            "dpow_end": {arm: {"mean": float(col(f"dpow_end_{arm}").mean()), "ci95": ci[arm]} for arm in D.ARMS},
            "o_share": {arm: float(col(f"o_{arm}").mean()) for arm in D.ARMS},
            "stride_peak_in_O_fraction": c["frac_o"], "o_diff_stride_minus_iid_ci95": c["o_diff_ci"],
            "dpow_stride_minus_iid": {"mean": float(c["dpow_diff"].mean()), "ci95": _a100.boot_ci(c["dpow_diff"])},
            "R_stride_peak_in_O_fraction": c["fo"], "R_o_diff_ci95": c["cio"],
            "R_o_diff_unseen_mean": (float(np.mean([r["R_o_stride16w"] - r["R_o_iid16w"] for r in unseen])) if unseen else None),
            "tgen_log2_stride_over_iid": ({"n": len(lr), "mean": float(np.mean(lr)), "ci95": _a100.boot_ci(np.array(lr))}
                                          if len(lr) >= 3 else {"n": len(lr)}),
            "n_generalised": {arm: int(sum(t is not None for r in ok for t in r[f"tgen_{arm}"])) for arm in D.ARMS}}


def selftest() -> None:
    assert suffix("fbw") == "_wd0.1" and suffix("iid16w") == "_bs16_wd0.1" and suffix("stride16w") == "_bs16_ordstride_wd0.1"
    assert len(D.jobs()) == 64 and len(set(D.jobs())) == 64
    rng = np.random.default_rng(0)
    pw = lambda hot: np.where(np.isin(np.arange(1, 57), hot), 10.0, 1.0) + rng.random(56) * 0.1   # noqa: E731

    def fake(set_hot, order_hot, gen=9000):
        def loader(s, split, arm):
            t = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
            hot = {"F": t["F"], "G": t["G"], "R": [2, 3, 4, 6, 8]}[split]
            if arm == "stride16w" and order_hot:
                hot = list(D.O)[:5] if not set_hot else hot + [11]
            elif not set_hot and split != "R":
                hot = [2, 3, 4, 6, 8]
            return {"end": pw(hot), "t_gen": gen}
        return loader
    v = verdict([seed_row(s, fake(True, False)) for s in D.SEEDS])
    assert v["K2_B16"] == "Menge steuert bei B = 16" and v["Konflikt"].startswith("Konflikt nicht pruefbar"), v
    v = verdict([seed_row(s, fake(False, True)) for s in D.SEEDS])
    assert v["Konflikt"] == "Reihenfolge gewinnt", v
    v = verdict([seed_row(s, fake(True, True)) for s in D.SEEDS])
    assert v["K2_B16"] == "Menge steuert bei B = 16" and v["Konflikt"] in ("Menge gewinnt", "beide wirken"), v
    assert verdict([seed_row(s, fake(True, False)) for s in D.SEEDS[:5]])["K2_B16"] == "nicht auswertbar"
    print("[exp106] selftest ok")


def main() -> None:
    rows = [seed_row(s) for s in D.SEEDS]
    out = {"primary": verdict(rows), "rows": [{k: v for k, v in r.items()} for r in rows]}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    print(json.dumps(out["primary"], indent=1, ensure_ascii=False))


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
