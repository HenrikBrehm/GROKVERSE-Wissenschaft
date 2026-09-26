"""EXP-020 smoke check (Codex review): the 60-step smoke run must show the switch exactly at step 30, the right
hashes and the subset diagnostics. Exit 1 otherwise. Reads files only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "training"))
from grokverse.data import split_hash  # noqa: E402

d = HERE / "raw_smoke/EXP-020_baseline_seed30_thr4_seed30_train_F_to_seed30_train_G_at30"
res = json.loads((d / "result.json").read_text(encoding="utf-8"))
sw = res["events"].get("switch", {})
checks = {
    "completed": res["status"] == "completed" and res["steps_completed"] == 60,
    "switch_at_30": sw.get("step") == 30 and res.get("switch_step") == 30,
    "F_hash": res["split_hash"] == split_hash(np.load(HERE / "splits/seed30_train_F.npy")),
    "G_hash": sw.get("new_train_hash") == split_hash(np.load(HERE / "splits/seed30_train_G.npy")),
    "test_hash": res["test_hash"] == split_hash(np.load(HERE / "splits/seed30_test.npy")),
    "subsets": all(f"acc_{k}" in sw and sw.get(f"n_{k}", 0) > 0 for k in ("G_minus_F", "F_minus_G", "F_and_G")),
    "train_eval_after_switch": len(res["dense"]["train_steps"]) > 0,
}
print(json.dumps({"checks": checks, "switch": sw}, indent=1))
sys.exit(0 if all(checks.values()) else 1)
