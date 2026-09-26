"""EXP-028 analysis (pre-registered in README.md): W_E top-5 in the memorisation window of the EXP-020 no-switch runs."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
X20 = HERE.parents[0] / "EXP-020-data-switch"
P = 113


def fold(k: int) -> int:
    k %= P
    return min(k, P - k)


def main() -> None:
    rows = []
    for f in sorted((X20 / "raw").glob("*/result.json")):
        r = json.loads(f.read_text())
        argv = " ".join(r.get("argv", []))
        if "--switch-step" in argv or r.get("status") not in ("completed", "done"):
            continue
        name = Path(r["split_file"]).name                      # seed{S}_train_{A}.npy
        seed, arm = int(name.split("_")[0][4:]), name.split("_")[-1][0]
        if seed not in range(30, 35) or arm not in "FG":
            continue
        T = set(json.loads((X20 / "splits" / f"seed{seed}.json").read_text())["targets"][arm])
        S, st = np.load(f.parent / "spectra.npy"), np.load(f.parent / "spectra_steps.npy")
        tr = r["transitions"]["primary"]
        mem = tr["memorization"]["first_crossing_step"]
        gen = tr["generalization"]["first_crossing_step"]
        end = int(st[-1])
        win = [i for i, t in enumerate(st) if mem is not None and t >= mem and t < (gen if gen is not None else end + 1)]
        top = [set(int(k) for k in np.argsort(-S[i])[:5] + 1) for i in range(len(st))]
        row = {"seed": seed, "arm": arm, "mem": mem, "gen": gen, "end": end, "targets": sorted(T),
               "ov_by_step": {int(t): len(top[i] & T) for i, t in enumerate(st)}}
        if win:
            i = win[-1]
            lost = T - top[-1]
            new = top[-1] - T
            row.update(window_step=int(st[i]), ov_window=len(top[i] & T), ov_end=len(top[-1] & T),
                       lost=sorted(lost), new=sorted(new), new_is_2f=[k in {fold(2 * t) for t in T} for k in sorted(new)])
        rows.append(row)
    ev = [x for x in rows if "ov_window" in x]
    out = {"n_runs": len(rows), "n_evaluable": len(ev), "rows": rows}
    if len(ev) < 6:
        out["verdict_P28a"] = "nicht auswertbar"
    else:
        full = sum(x["ov_window"] == 5 for x in ev)
        m = float(np.mean([x["ov_window"] for x in ev]))
        out.update(n_full=full, mean_ov_window=m, mean_ov_end=float(np.mean([x["ov_end"] for x in ev])))
        out["verdict_P28a"] = ("bestätigt" if full >= 8 and m >= 4.5 else "widerspricht" if m < 3 else "teilweise")
        f5 = [x for x in ev if x["ov_window"] == 5]
        out["P28b"] = {"n_full": len(f5), "n_lost_any": sum(x["ov_end"] < 5 for x in f5),
                       "replacements": sum(len(x["new"]) for x in f5), "replacements_2f": sum(sum(x["new_is_2f"]) for x in f5),
                       "by_arm": {a: {"n": sum(x["arm"] == a for x in f5),
                                      "lost_any": sum(x["arm"] == a and x["ov_end"] < 5 for x in f5)} for a in "FG"}}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
