"""Session 52: descriptive look at the first finished seed (3862) of EXP-117; the pre-set reading needs both seeds and is
NOT evaluated here. Uses the frozen analysis helpers unchanged (EXP-105 analyze_pilot.load/targets, head_delta)."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("exp117_analyze", HERE / "analyze.py")   # avoid the name clash with EXP-102 analyze
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)
AP = E.AP
fF, fG = (Path(x) for x in E.PAIRS[0].split(":")[1].split(","))
root = HERE / "raw"
rF, rG = AP.load(root, 3862, fF), AP.load(root, 3862, fG)
TF, TG = AP.targets(fF), AP.targets(fG)
din = {s: AP.A.delta_pow(rF["P"][s], rG["P"][s], TF, TG) for s in rF["steps"] if s in rG["P"]}
h = E.head_delta(root, 3862, fF, fG)
out = {"seed": 3862, "din": {s: round(v, 2) for s, v in din.items() if s % 1000 == 0 or s in (1500, 2500)},
       "dout": {s: round(v, 2) for s, v in h["dout_traj"].items() if int(s) % 1000 == 0 or s in ("1500", "2500")},
       "test_acc": [rF["res"]["curve"][-1][2], rG["res"]["curve"][-1][2]],
       "train_acc": [rF["res"]["curve"][-1][1], rG["res"]["curve"][-1][1]]}
print(json.dumps(out, indent=1))
Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1), encoding="utf-8")
