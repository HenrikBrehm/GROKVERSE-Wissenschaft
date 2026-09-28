"""EXP-100 (L0 pilot, exploration; rule 20b): set composition vs data order under minibatch. README.md. Session 43, UNTESTED.
Run under guarded_run.py with the global python after the pilot block (jobs.txt from design.py --jobs).

Per seed and arm (fb, iid256, iid64, sgdm256, stride256; each on the engineered splits F and G), through the shared loader
(seed, device, steps = budget, split/test hashes, p/task; recorded batch_size / order / optimizer / sgd_lr), final and step-2000
W_E group power (EXP-043 basis):
  dpow(arm)   = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)]  (P1 definition, confirm_p1.delta_pow) at the end and at step 2000
  o(run)      = share of the group power on the stride-order frequencies O
  peak(run)   = frequency with the largest power (in O or not)
  t_gen(run)  = first step with test accuracy >= 0.95 (trainer transitions, primary thresholds), also in epochs
R runs (random split): iid256 and stride256 -> o and peak (order alone).
Bootstrap over seeds (10 000, rng 100). Readings fixed here (pilot; the confirmation L0-R gets its own registration):
  K2-MB   'Menge steuert unter Minibatch'   dpow_end CI lower > 0 in iid256 AND iid64
          'Menge steuert kaum'              dpow_end CI upper < 1 in iid256 AND iid64   (P1 minimum effect 1)
          else 'gemischt'.  sgdm256 reported separately ('nicht auswertbar' if fewer than 6 seeds generalise in both splits).
  Konflikt (stride256 on F/G, 2 x n runs; Fassung 2 after review s43: the order must be shown to act at all)
          order_acts = R-alone 'wirkt' OR paired CI lower bound of o(stride256) - o(iid256) on F/G > 0
          not order_acts        -> 'Konflikt nicht pruefbar (Reihenfolge wirkt nicht)'
          'Menge gewinnt'       order_acts, dpow_end(stride) CI lower > 0 and peak outside O in >= 75 % of the runs
          'Reihenfolge gewinnt' order_acts, peak in O in >= 75 % of the runs and dpow_end(stride) CI lower <= 0
          else 'beide wirken'.  Also reported: paired dpow(stride) - dpow(iid256), share of runs with a frequency of O in the top 5.
  Reihenfolge allein (R): 'wirkt' if peak in O in >= 75 % of R-stride runs; 'wirkt nicht' if <= 25 % and the paired CI of
          o(R-stride) - o(R-iid) contains 0; else 'unklar'.
Descriptive: all dpow means/CIs (end, 2000), o means per arm, t_gen per arm (steps and epochs), E-iid256 vs R-iid256 t_gen (R5).
Valid seed: the engineered runs of fb, fb30k, iid256, iid64 and stride256 all ok with a finite dpow (delta_pow_checked);
fewer than 6 valid seeds -> everything 'nicht auswertbar'. Runs that never generalise stay valid; the number of generalised
runs per arm is reported. fb30k (full batch, same 30 000 steps) separates 'minibatch' from 'long training' in K2-MB.
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

_spec = importlib.util.spec_from_file_location("exp043_analyze", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
_a43 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_a43)

RAW, SPL, SUF = HERE / "raw", HERE / "splits", "_devcuda"
MIN_VALID, N_BOOT, SHARE = 6, 10_000, 0.75


def suffix(arm: str) -> str:
    bs, order, opt, _ = D.ARMS[arm]
    return ((f"_bs{bs}" if bs else "") + (f"_ord{order}" if order != "iid" else "")
            + (f"_sgdm{float(D.SGD_LR)!r}_0.9" if opt == "sgdm" else ""))


def load(s: int, split: str, arm: str):
    bs, order, opt, budget = D.ARMS[arm]
    pat = f"EXP-018_baseline_seed{s}_thr*_seed{s}_{split}{suffix(arm)}{SUF}"
    L = load_run(find_run(HERE / D.ROOTS.get(arm, "raw"), pat), Expect(seed=s, device="cuda", max_steps=budget, split_file=SPL / f"seed{s}_{split}.npy",
                                            test_file=SPL / f"seed{s}_test.npy", config={"p": 113, "task": "add"},
                                            snapshots_at=(budget, 2000)))
    tag = f"seed {s} {split} {arm}"
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    r = L.res
    if (r.get("batch_size", 0) != bs or r.get("order", "iid") != order or r.get("optimizer", "adamw") != opt
            or (opt == "sgdm" and r.get("sgd_lr") != D.SGD_LR)):
        return f"{tag}: recorded batch/order/optimizer differ from the arm"
    if bs and r.get("events", {}).get("minibatch", {}).get("batch_size") != bs:
        return f"{tag}: minibatch event missing"
    gp = lambda st: _a43.group_power(L.snapshot(st), "add", 113)[0]   # noqa: E731
    end, at2k = gp(budget), gp(2000)
    if not (np.isfinite(end).all() and np.isfinite(at2k).all()):
        return f"{tag}: non-finite power"
    gen = (r.get("transitions") or {}).get("primary", {}).get("generalization", {}).get("first_crossing_step")
    spe = r.get("events", {}).get("minibatch", {}).get("steps_per_epoch", 1) if bs else 1
    return {"end": end, "at2k": at2k, "t_gen": gen, "spe": spe}


def o_share(pw: np.ndarray) -> float:
    return float(pw[[k - 1 for k in D.O]].sum() / pw.sum())


def peak_in_o(pw: np.ndarray) -> bool:
    return int(np.argmax(pw)) + 1 in D.O


def seed_row(s: int) -> dict:
    meta = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["F"], meta["targets"]["G"]
    runs = {(x, arm): load(s, x, arm) for arm in D.ARMS for x in "FG"}
    runs.update({("R", arm): load(s, "R", arm) for arm in D.R_ARMS})
    row: dict = {"seed": s, "errors": [v for v in runs.values() if isinstance(v, str)]}
    for arm in D.ARMS:
        a, b = runs[("F", arm)], runs[("G", arm)]
        if isinstance(a, str) or isinstance(b, str):
            continue
        de, d2 = c1.delta_pow_checked(a["end"], b["end"], F, G), c1.delta_pow_checked(a["at2k"], b["at2k"], F, G)
        if de is None or d2 is None:
            row["errors"].append(f"seed {s} {arm}: delta_pow not finite")
            continue
        row[f"dpow_end_{arm}"], row[f"dpow_2k_{arm}"] = de, d2
        row[f"top5O_{arm}"] = [bool(set(int(k) + 1 for k in np.argsort(-x["end"])[:5]) & set(D.O)) for x in (a, b)]
        row[f"o_{arm}"] = (o_share(a["end"]) + o_share(b["end"])) / 2
        row[f"peakO_{arm}"] = [peak_in_o(a["end"]), peak_in_o(b["end"])]
        row[f"tgen_{arm}"] = [a["t_gen"], b["t_gen"]]
        row[f"tgen_ep_{arm}"] = [None if x["t_gen"] is None else x["t_gen"] / x["spe"] for x in (a, b)]
    for arm in D.R_ARMS:
        r = runs[("R", arm)]
        if not isinstance(r, str):
            row[f"R_o_{arm}"], row[f"R_peakO_{arm}"], row[f"R_tgen_ep_{arm}"] = (
                o_share(r["end"]), peak_in_o(r["end"]), None if r["t_gen"] is None else r["t_gen"] / r["spe"])
    row["valid"] = all(f"dpow_end_{arm}" in row for arm in ("fb", "fb30k", "iid256", "iid64", "stride256"))
    return row


def boot_ci(x: np.ndarray, seed: int = 100) -> list[float]:
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), size=(N_BOOT, len(x)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def verdict(rows: list[dict]) -> dict:
    ok = [r for r in rows if r["valid"]]
    if len(ok) < MIN_VALID:
        return {"n": len(ok), "K2_MB": "nicht auswertbar", "Konflikt": "nicht auswertbar", "Reihenfolge_allein": "nicht auswertbar"}
    col = lambda k, rs=ok: np.array([r[k] for r in rs], dtype=float)   # noqa: E731
    ci = {arm: boot_ci(col(f"dpow_end_{arm}")) for arm in ("fb", "fb30k", "iid256", "iid64", "stride256")}
    if ci["iid256"][0] > 0 and ci["iid64"][0] > 0:
        k2 = "Menge steuert unter Minibatch"
    elif ci["iid256"][1] < 1 and ci["iid64"][1] < 1:
        k2 = "Menge steuert kaum"
    else:
        k2 = "gemischt"
    peaks = [p for r in ok for p in r["peakO_stride256"]]
    frac_o = float(np.mean(peaks))
    o_diff_ci = boot_ci(col("o_stride256") - col("o_iid256"))
    dpow_diff = col("dpow_end_stride256") - col("dpow_end_iid256")
    rr = [r for r in ok if "R_o_stride256" in r and "R_o_iid256" in r]
    if rr:
        fo = float(np.mean([r["R_peakO_stride256"] for r in rr]))
        do = col("R_o_stride256", rr) - col("R_o_iid256", rr)
        cio = boot_ci(do)
        alone = "wirkt" if fo >= SHARE else ("wirkt nicht" if fo <= 1 - SHARE and cio[0] <= 0 <= cio[1] else "unklar")
    else:
        fo, cio, alone = None, None, "nicht auswertbar"
    order_acts = alone == "wirkt" or o_diff_ci[0] > 0
    if not order_acts:
        conflict = "Konflikt nicht pruefbar (Reihenfolge wirkt nicht)"
    elif ci["stride256"][0] > 0 and 1 - frac_o >= SHARE:
        conflict = "Menge gewinnt"
    elif frac_o >= SHARE and ci["stride256"][0] <= 0:
        conflict = "Reihenfolge gewinnt"
    else:
        conflict = "beide wirken"
    sg = [r for r in rows if "dpow_end_sgdm256" in r and all(t is not None for t in r["tgen_sgdm256"])]
    out = {"n": len(ok), "K2_MB": k2, "Konflikt": conflict, "Reihenfolge_allein": alone,
           "dpow_end": {arm: {"mean": float(col(f"dpow_end_{arm}").mean()), "ci95": ci[arm]} for arm in ci},
           "dpow_2k": {arm: float(col(f"dpow_2k_{arm}").mean()) for arm in ci},
           "o_share": {arm: float(col(f"o_{arm}").mean()) for arm in ci},
           "stride_peak_in_O_fraction": frac_o, "o_diff_stride_minus_iid_ci95": o_diff_ci,
           "dpow_stride_minus_iid": {"mean": float(dpow_diff.mean()), "ci95": boot_ci(dpow_diff)},
           "top5_has_O_fraction": {arm: float(np.mean([t for r in ok for t in r[f"top5O_{arm}"]])) for arm in ci},
           "n_generalised": {arm: int(sum(t is not None for r in ok for t in r[f"tgen_{arm}"])) for arm in ci},
           "R5_tgen_epochs_median": {"E_iid256": float(np.median([t for r in ok for t in r["tgen_ep_iid256"] if t is not None] or [np.nan])),
                                     "R_iid256": float(np.median([r["R_tgen_ep_iid256"] for r in ok if r.get("R_tgen_ep_iid256") is not None] or [np.nan]))}, "R_stride_peak_in_O_fraction": fo, "R_o_diff_ci95": cio,
           "sgdm256": ({"n": len(sg), "dpow_end_mean": float(np.mean([r["dpow_end_sgdm256"] for r in sg])),
                        "dpow_end_ci95": boot_ci(np.array([r["dpow_end_sgdm256"] for r in sg]))}
                       if len(sg) >= MIN_VALID else {"n": len(sg), "reading": "nicht auswertbar"})}
    return out


def main() -> None:
    if D.SGD_LR is None:
        raise SystemExit("SGD_LR is not set in design.py")
    rows = [seed_row(s) for s in D.SEEDS]
    out = {"primary": verdict(rows), "rows": [{k: v for k, v in r.items()} for r in rows]}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    print(json.dumps(out["primary"], indent=1, ensure_ascii=False))


def selftest() -> None:
    rng = np.random.default_rng(0)

    def mk(s: int, k2: float, stride: float, peak_o: bool, r_peak_o: bool) -> dict:
        r = {"seed": s, "valid": True, "errors": []}
        for arm in ("fb", "fb30k", "iid256", "iid64", "stride256", "sgdm256"):
            r[f"dpow_end_{arm}"] = (stride if arm == "stride256" else k2) + rng.normal(0, 0.3)
            r[f"dpow_2k_{arm}"] = r[f"dpow_end_{arm}"]
            r[f"o_{arm}"] = (0.3 if (arm == "stride256" and r_peak_o) else 0.1) + rng.normal(0, 0.01)
            r[f"peakO_{arm}"] = [peak_o, peak_o]
            r[f"top5O_{arm}"] = [peak_o, peak_o]
            r[f"tgen_{arm}"] = [1000, 1000]
            r[f"tgen_ep_{arm}"] = [100.0, 100.0]
        r["R_o_stride256"], r["R_o_iid256"] = 0.1 + rng.normal(0, 0.01), 0.1 + rng.normal(0, 0.01)
        r["R_peakO_stride256"] = r_peak_o
        return r
    v = verdict([mk(s, 5.0, 5.0, False, False) for s in range(8)])
    assert (v["K2_MB"], v["Konflikt"], v["Reihenfolge_allein"]) == ("Menge steuert unter Minibatch",
                                                                     "Konflikt nicht pruefbar (Reihenfolge wirkt nicht)", "wirkt nicht"), v
    rows = [mk(s, 5.0, 5.0, False, False) for s in range(8)]
    for r in rows:
        r["o_stride256"] = 0.2 + rng.normal(0, 0.01)          # the order acts on o, the set keeps the peak
    assert verdict(rows)["Konflikt"] == "Menge gewinnt", verdict(rows)
    v = verdict([mk(s, 0.0, 0.0, True, True) for s in range(8)])
    assert (v["K2_MB"], v["Konflikt"], v["Reihenfolge_allein"]) == ("Menge steuert kaum", "Reihenfolge gewinnt", "wirkt"), v
    v = verdict([mk(s, 5.0, 5.0, True, True) for s in range(8)])
    assert v["Konflikt"] == "beide wirken", v
    assert verdict([mk(s, 5.0, 5.0, False, False) for s in range(5)])["K2_MB"] == "nicht auswertbar"
    assert suffix("stride256") == "_bs256_ordstride" and suffix("iid64") == "_bs64" and suffix("fb") == ""
    assert D.ROOTS["fb30k"] != "raw"           # fb and fb30k share the run id, so they need separate roots
    print("[exp100] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
