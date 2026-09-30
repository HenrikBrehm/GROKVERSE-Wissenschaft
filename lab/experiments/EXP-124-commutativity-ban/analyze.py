"""EXP-124 (session 55, draft, written before any main run): readings as in README. Per unit u0-u9: t_swap / t_other (first 25-step
grid point with acc_swap / acc_other >= 0.5; not reached = censored at 8000); L_swap = log2 t_swap(T) - log2 t_swap(C), L_other
likewise; Delta = L_swap - L_other (session 55 review: separates a specific delay of the commutativity stage from a general
slow-down). 'Kommutativitaet ueber die Zielstruktur': mean L_swap >= 1, mean Delta >= 0.5 and Delta > 0 in >= 80 % of units;
'allgemeine Verlangsamung': mean L_swap >= 1, mean L_other >= 1 and |mean Delta| < 0.3; 'eigener Pfad': |mean L_swap| < 0.3 and
mean L_other >= 1; else 'unklar'. Descriptive: median t_swap(T) against the EXP-123 R median 4150 and E2_0 no-ban times (EXP-123).
Technical: every run completed with the planned seed, split, test file, 8000-step cap and ban, and the banned W_E power at the end
< 1e-6 of the median of the other frequencies (this only shows the code ran; the claim is 'without the targets in W_E');
more than 1 failing run -> 'nicht auswertbar'.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-124-commutativity-ban/analyze.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from make_jobs import arms

HERE = Path(__file__).resolve().parent
CENSOR = 8000


def first(steps: list[int], vals: list[float], thr: float = 0.5) -> int | None:
    return next((s for s, v in zip(steps, vals) if v >= thr), None)


def load(u: int, arm: str, ban: list[int]) -> dict:
    f = HERE / "raw" / f"u{u}_{arm}" / "result.json"
    if not f.exists():
        return {"unit": u, "arm": arm, "status": "fehlt"}
    r = json.loads(f.read_text(encoding="utf-8"))
    w = np.array(r["we_power_final"])
    rest = np.median(np.delete(w, [k - 1 for k in ban]))
    init = json.loads((HERE.parents[2] / f"lab/confirm/r5_splits/r5_u{u}.json").read_text(encoding="utf-8"))["init"]
    argv = " ".join(r.get("argv", []))
    ok = (r.get("status") == "completed" and r.get("seed") == init and r.get("steps_max") == CENSOR
          and f"r5_u{u}_E2_0.npy" in argv and f"r5_u{u}_test.npy" in argv
          and sorted(r["ban"]) == sorted(ban) and all(w[k - 1] < 1e-6 * rest for k in ban))
    t = r["trace"]
    return {"unit": u, "arm": arm, "status": "ok" if ok else "defekt", "t_gen": r["generalization_step"],
            "t_swap": first(t["step"], t["swap"]), "t_other": first(t["step"], t["other"]), "last_step": r["last_step"]}


def main() -> None:
    rows = [load(u, arm, ban) for u in range(10) for arm, ban in arms(u).items()]
    for r in rows:
        print(json.dumps(r), flush=True)
    bad = [r for r in rows if r["status"] != "ok"]
    out: dict = {"rows": rows, "n_not_ok": len(bad)}
    if len(bad) > 1:
        out["reading"] = f"nicht auswertbar ({len(bad)} Laeufe fehlen/defekt)"
    else:
        by = {(r["unit"], r["arm"]): r for r in rows if r["status"] == "ok"}
        us = [u for u in range(10) if (u, "T") in by and (u, "C") in by]
        lg = lambda v: np.log2(v if v is not None else CENSOR)  # noqa: E731
        ls = np.array([lg(by[(u, "T")]["t_swap"]) - lg(by[(u, "C")]["t_swap"]) for u in us])
        lo = np.array([lg(by[(u, "T")]["t_other"]) - lg(by[(u, "C")]["t_other"]) for u in us])
        dl = ls - lo
        ts = [by[(u, "T")]["t_swap"] for u in us]
        out.update({"n": len(us), "L_swap_mean": float(ls.mean()), "L_swap_pos": int((ls > 0).sum()),
                    "L_other_mean": float(lo.mean()), "L_other_pos": int((lo > 0).sum()),
                    "Delta_mean": float(dl.mean()), "Delta_pos": int((dl > 0).sum()),
                    "median_t_swap_T_censored": float(np.median([v if v is not None else CENSOR for v in ts])),
                    "ref_EXP123_R_median_t_swap": 4150})
        if ls.mean() >= 1 and dl.mean() >= 0.5 and (dl > 0).sum() >= 0.8 * len(us):
            out["reading"] = "Kommutativitaet ueber die Zielstruktur"
        elif ls.mean() >= 1 and lo.mean() >= 1 and abs(dl.mean()) < 0.3:
            out["reading"] = "allgemeine Verlangsamung"
        elif abs(ls.mean()) < 0.3 and lo.mean() >= 1:
            out["reading"] = "eigener Pfad"
        else:
            out["reading"] = "unklar"
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
