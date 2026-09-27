"""Session 34, post hoc. After switch_cleanup_s34.py (M_clean contradicted) an exploration on N28 only showed: in runs WITHOUT a
switch the own-target W_E share at step 250 predicts the grokking time strongly (Spearman -0.71, 60 runs), and switch runs@25 are
less concentrated on their new targets at t+250 (0.216) than destination-only runs at 250 (0.31).

Hypothesis M_deficit (fixed here, BEFORE P3's s_new values are read; N28 is the exploration set): the switch cost at t = 25 is a
concentration deficit. The same dose-response that maps W_E target concentration to grokking time without a switch also maps the
switch runs. Procedure per block, unchanged for N28 and P3:
  1. Fit OLS log2(gen) = a + b * share on the destination-only runs (share = own-target share of W_E power at step 250; runs without an
     event excluded from the fit).
  2. For every switch run X->Y@25 with an event, predict log2(gen) from s_new = share of Y's targets at step 275 (= t + 250).
     The predicted delay is pred - log2(gen(Y only)), the observed delay log2(gen(X->Y@25)) - log2(gen(Y only)).
  3. Measures: ratio R = mean predicted delay / mean observed delay; Spearman(pred delay, obs delay) over runs.
  Verdict (P3 decides; N28 descriptive): "accounts" if 0.7 <= R <= 1.3 AND rho >= 0.3; "partly" if 0.3 <= R < 0.7 and rho >= 0.3 (or R in
  [0.7, 1.3] with rho < 0.3); "does not account" if R < 0.3 or the predicted delay is <= 0.
Caveat, stated before: step 250 vs 275 differ by 25 steps of training (favours the switch runs slightly -> predictions conservative);
censored switch runs are excluded (the slowest), which shrinks the observed mean delay.
  python lab/confirm/switch_deficit_s34.py
"""
import json, math, re
import numpy as np
import switch_cleanup_s34 as sc

OUT = sc.LAB / "confirm/switch_deficit_s34.json"


def block(name: str, t: int = 25) -> dict:
    raw_, spl_, pre, w = sc.BLOCKS[name]
    raw, spl = sc.LAB / raw_, sc.LAB / spl_
    tg = lambda s: json.loads((spl / f"{pre}_seed{s}_{w}.json").read_text(encoding="utf-8"))["targets"]  # noqa: E731
    base, sw = {}, []
    for d in raw.iterdir():
        if (m := re.search(rf"seed(\d+)_thr1_{pre}_seed\d+_{w}_(A|B)_devcuda$", d.name)):
            s, x = int(m.group(1)), m.group(2)
            g = sc.gen(d)
            base[(s, x)] = (sc.shares(d, tg(s)[x], 250, None)[0], math.log2(g) if g else None)
        elif (m := re.search(rf"seed(\d+)_thr1_{pre}_seed\d+_{w}_(A|B)_to_{pre}_seed\d+_{w}_(A|B)_at{t}_devcuda$", d.name)):
            s, x, y = int(m.group(1)), m.group(2), m.group(3)
            g = sc.gen(d)
            if g:
                sw.append((s, y, sc.shares(d, tg(s)[y], t + 250, None)[0], math.log2(g)))
    fit = np.array([(sh, lg) for sh, lg in base.values() if lg is not None])
    b, a = np.polyfit(fit[:, 0], fit[:, 1], 1)
    pred, obs = [], []
    for s, y, sn, lg in sw:
        ly = base[(s, y)][1]
        if ly is None:
            continue
        pred.append(a + b * sn - ly); obs.append(lg - ly)
    pred, obs = np.array(pred), np.array(obs)
    R = float(pred.mean() / obs.mean()); rho = sc.spearman(pred, obs)
    if pred.mean() <= 0 or R < 0.3:
        v = "does not account"
    elif 0.7 <= R <= 1.3 and rho >= 0.3:
        v = "accounts"
    else:
        v = "partly"
    return {"block": name, "fit": {"a": float(a), "b": float(b), "n": len(fit)}, "n_switch_runs": len(obs),
            "mean_pred_delay": float(pred.mean()), "mean_obs_delay": float(obs.mean()), "R": R, "rho": rho, "verdict": v,
            "mean_s_new_switch": float(np.mean([x[2] for x in sw])), "mean_share_base": float(fit[:, 0].mean())}


if __name__ == "__main__":
    out = {k: block(k) for k in ("N28", "P3")}
    for k, r in out.items():
        print(f"{k}: fit b={r['fit']['b']:+.2f} (n={r['fit']['n']}), switch runs {r['n_switch_runs']}, s_new {r['mean_s_new_switch']:.3f} vs base {r['mean_share_base']:.3f}; "
              f"pred delay {r['mean_pred_delay']:+.3f} obs {r['mean_obs_delay']:+.3f} R={r['R']:.2f} rho={r['rho']:+.3f} -> {r['verdict']}")
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
