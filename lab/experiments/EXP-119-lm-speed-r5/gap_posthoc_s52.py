"""Session 52, post hoc exploration: learning gap t_test / t_train (first interpolated step with fact accuracy >= 0.5) in all
stored lm_stage2 / lm_untied runs except the frozen LM1 block. Reading fixed before computing (JOURNAL S52 cycle 7): median ratio
<= 1.3 "no notable gap"; >= 2 "grokking-like gap"; else "small gap".
"""
import json, sys
from pathlib import Path
import numpy as np
LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from analyze import cross  # noqa: E402
rows = []
for f in sorted(LAB.glob("experiments/EXP-1*/raw*/lm2_*/result.json")):
    r = json.loads(f.read_text(encoding="utf-8"))
    if r.get("status") != "completed":
        continue
    c = r["curve"]
    tr, te = cross(c, 1), cross(c, 2)
    rows.append({"run": f"{f.parts[-4]}/{f.parent.name[:48]}", "loss": r["config"].get("loss"), "K": r["config"].get("arith_facts"),
                 "t_train": tr, "t_test": te, "ratio": (te / tr) if (tr and te) else None, "final_test": round(c[-1][2], 3)})
for x in rows:
    print(json.dumps(x))
rs = [x["ratio"] for x in rows if x["ratio"] is not None]
med = float(np.median(rs)) if rs else None
reading = None if med is None else "no notable gap" if med <= 1.3 else "grokking-like gap" if med >= 2 else "small gap"
out = {"n_runs": len(rows), "n_ratio": len(rs), "median_ratio": med, "min": min(rs, default=None), "max": max(rs, default=None),
       "reading": reading, "rows": rows}
print(json.dumps({k: v for k, v in out.items() if k != "rows"}))
Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1), encoding="utf-8")
