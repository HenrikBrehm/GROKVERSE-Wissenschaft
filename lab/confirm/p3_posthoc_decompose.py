"""P3 post hoc (session 21, 06:09 Berlin, AFTER the P3 result and the Codex conclusion review; exploratory, no verdict).

Codex: pi > 0 can also arise from an UNSPECIFIC lag (the switch model adapts more slowly to B and stays nearer the balanced init, L ~ 0),
not only from retained A-specific preference. Decompose L = log P(F) - log P(G) into its parts, with P(X) = share of the total W_E power
in the five X targets (final step), per direction, omega = 0:
  dF = log P_F(first->second) - log P_F(pure second)   [retention predicts dF > 0: more power on the FIRST split's targets]
  dG = log P_G(first->second) - log P_G(pure second)   [lag predicts dG < 0: less power on the SECOND split's targets]
(for B->A the roles of F and G swap). Also: L of the pure second run at its step-250 snapshot, as a picture of an under-trained model.
Run under guarded_run.py. Reads only bound P3 runs (confirm_p3.load_level).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools"))
import confirm_p3 as c3  # noqa: E402


def logshare(pw: np.ndarray, T: list[int]) -> float:
    return float(np.log(pw[[k - 1 for k in T]].sum() / pw.sum()))


def main() -> None:
    man = json.loads((LAB / "confirm/P3_manifest.json").read_text(encoding="utf-8"))
    gp = lambda W: c3.a43().group_power(W, "add", 113)[0]   # noqa: E731
    rows = []
    for s in man["seeds"]:
        meta = json.loads((c3.SPL / f"p3_seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        sn = c3.load_level(man, s, 0.0)
        if isinstance(sn, str):
            rows.append({"seed": s, "error": sn})
            continue
        end = {k: gp(sn[k][c3.BUDGET + (c3.T_SWITCH if len(k) == 2 else 0)]) for k in ("A", "B", "AB", "BA")}
        # direction A->B: first targets F, second targets G, reference pure B; direction B->A: first G, second F, reference pure A
        d = {}
        for sw, ref, first, second in (("AB", "B", F, G), ("BA", "A", G, F)):
            d[sw] = {"d_first": logshare(end[sw], first) - logshare(end[ref], first),
                     "d_second": logshare(end[sw], second) - logshare(end[ref], second)}
        rows.append({"seed": s, **d})
    ok = [r for r in rows if "error" not in r]
    summ = {}
    for key in ("d_first", "d_second"):
        v = np.array([(r["AB"][key] + r["BA"][key]) / 2 for r in ok])
        summ[key] = {"mean": float(v.mean()), "sd": float(v.std(ddof=1)), "n_pos": int((v > 0).sum()), "n": len(v)}
    out = {"summary": summ, "rows": rows}
    (LAB / "confirm/P3_posthoc_decompose.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
