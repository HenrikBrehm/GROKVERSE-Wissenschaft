"""EXP-055 (P2 pilot): dose-response of the test loss when equal W_E energy is removed from the own targets vs the control set.
No training: the 20 saved EXP-047 eng models (seeds 150-159, arms F/G). Reuses the ablation helpers of EXP-051 unchanged.
Definition and reading: README.md (registered before this code ran)."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
_spec = importlib.util.spec_from_file_location("exp051", ROOT / "lab/experiments/EXP-051-functional-ablation/analyze.py")
e51 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e51)
from result_loader import Expect, find_run, load_run  # noqa: E402  (path set up by exp051)

P, SEEDS, DOSES, PRIMARY_F, ACC_MIN, ALPHA, MIN_VALID = e51.P, e51.SEEDS, (0.1, 0.25, 0.5, 0.75, 1.0), 1.0, 0.9, 0.05, 8


def evaluate(model, W_rows: np.ndarray | None, idx: np.ndarray) -> dict:
    """Mean cross-entropy (logits[:, :P]), accuracy and mean margin (correct minus best wrong) on the pairs idx."""
    import torch
    with torch.no_grad():
        saved = model.W_E.data.clone()
        if W_rows is not None:
            model.W_E.data[:P] = torch.from_numpy(W_rows).to(model.W_E.dtype)
        a, b = idx // P, idx % P
        x = torch.from_numpy(np.stack([a, b, np.full(len(idx), P)], 1)).long()
        lg = model.logits_last(x)[:, :P].double()
        y = torch.from_numpy((a + b) % P).long()
        loss = float(torch.nn.functional.cross_entropy(lg, y))
        acc = float((lg.argmax(-1) == y).double().mean())
        corr = lg.gather(1, y[:, None])[:, 0]
        wrong = lg.clone()
        wrong.scatter_(1, y[:, None], -float("inf"))
        margin = float((corr - wrong.max(1).values).mean())
        model.W_E.data.copy_(saved)
    return {"loss": loss, "acc": acc, "margin": margin}


def seed_row(s: int, B: np.ndarray) -> dict:
    kind = "eng"
    r: dict = {"seed": s, "valid": False}
    E47 = e51.E47
    T = {a: json.loads((E47 / f"splits/split_add113_seed{s}_{kind}_{a}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
    trains = [np.load(E47 / f"splits/split_add113_seed{s}_{kind}_{a}.npy") for a in "FG"]
    common = np.setdiff1d(np.arange(P * P), np.union1d(*trains))
    arms = {}
    for arm, other in (("F", "G"), ("G", "F")):
        stem = f"split_add113_seed{s}_{kind}_{arm}"
        L = load_run(find_run(E47 / "raw", f"*_seed{s}_thr*_{stem}{e51.FB_SUFFIX}"),
                     Expect(seed=s, device=e51.DEV, max_steps=e51.STEP, split_file=E47 / f"splits/{stem}.npy",
                            config={"p": P, "task": "add"}, files=("model_final.pt",)))
        if L.status != "ok":
            r["reason"] = f"{arm}: {L.status}: {L.reason}"
            return r
        m = e51.load_model(L.path)
        W = m.W_E.detach().numpy().astype(np.float64)[:P]
        base = evaluate(m, None, common)
        ctrl = e51.control_set(T[arm], T[other])
        e_own, e_ctrl = e51.energy(W, B, T[arm]), e51.energy(W, B, ctrl)
        if e_own <= e_ctrl:
            r["reason"] = f"{arm}: E_own <= E_ctrl, dose 1.0 infeasible"
            return r
        dose = {}
        for f in DOSES:
            E = f * e_ctrl
            ev_o = evaluate(m, e51.remove_energy(W, B, T[arm], E), common)
            ev_c = evaluate(m, e51.remove_energy(W, B, ctrl, E), common)
            dose[str(f)] = {"E": E, "dL_own": ev_o["loss"] - base["loss"], "dL_ctrl": ev_c["loss"] - base["loss"],
                            "dacc_own": base["acc"] - ev_o["acc"], "dacc_ctrl": base["acc"] - ev_c["acc"],
                            "margin_own": ev_o["margin"], "margin_ctrl": ev_c["margin"]}
        arms[arm] = {"base": base, "energy_own": e_own, "energy_ctrl": e_ctrl, "dose": dose}
    r["arms"] = arms
    r["n_common_test"] = int(len(common))
    vals = [v["dose"][str(f)][k] for v in arms.values() for f in DOSES for k in ("dL_own", "dL_ctrl")]
    if not all(v["base"]["acc"] >= ACC_MIN for v in arms.values()):
        r["reason"] = "base accuracy < 0.9"
        return r
    if not np.all(np.isfinite(vals)):
        r["reason"] = "non-finite loss change"
        return r
    r["valid"] = True
    r["D"] = float(np.mean([v["dose"][str(PRIMARY_F)]["dL_own"] - v["dose"][str(PRIMARY_F)]["dL_ctrl"] for v in arms.values()]))
    r["D_by_dose"] = {str(f): float(np.mean([v["dose"][str(f)]["dL_own"] - v["dose"][str(f)]["dL_ctrl"] for v in arms.values()]))
                      for f in DOSES}
    return r


def verdict(D: np.ndarray) -> tuple[str, float | None]:
    if len(D) < MIN_VALID:
        return "nicht auswertbar", None
    p = e51.one_sided_p(D)
    if D.mean() > 0 and p < ALPHA:
        return "je Energie stärker genutzt", p
    return ("richtungsgleich, n. s." if D.mean() > 0 else "nicht stärker genutzt"), p


def selftest() -> None:
    assert verdict(np.ones(10))[0] == "je Energie stärker genutzt"
    assert verdict(-np.ones(10))[0] == "nicht stärker genutzt"
    assert verdict(np.ones(7))[0] == "nicht auswertbar"
    d = np.array([1.0, -0.2, 0.3, 0.1, -0.1, 0.2, 0.1, -0.3, 0.05, 0.02])
    assert verdict(d)[0] in ("richtungsgleich, n. s.", "je Energie stärker genutzt")
    e51.selftest()
    print("[exp055] selftest ok", flush=True)


def main() -> None:
    if sys.argv[1:] == ["--selftest"]:
        selftest()
        return
    B = e51.basis()
    rows = [seed_row(s, B) for s in SEEDS]
    valid = [r for r in rows if r["valid"]]
    D = np.array([r["D"] for r in valid])
    v, p = verdict(D)
    out = {"n_valid": len(valid), "D_mean": float(D.mean()) if len(D) else None, "p": p,
           "n_positive": int((D > 0).sum()), "verdict": v,
           "D_by_dose_mean": {str(f): float(np.mean([r["D_by_dose"][str(f)] for r in valid])) for f in DOSES} if valid else None,
           "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
