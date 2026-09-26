"""EXP-037 smoke check (after Codex): the training set selected after steps 5, 10, 15 must be G, F, G (split hashes),
the switch event at step 20 must point to G, and the run must be fresh (written by this commit's code)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "training"))
from grokverse.data import split_hash  # noqa: E402

S20 = HERE.parent / "EXP-020-data-switch" / "splits"


def main() -> int:
    runs = list((HERE / "raw_smoke").glob("*_alt5/result.json"))
    if len(runs) != 1:
        print(f"[smoke] expected one smoke run, found {len(runs)}")
        return 1
    r = json.loads(runs[0].read_text(encoding="utf-8"))
    h_f = split_hash(np.load(S20 / "seed30_train_F.npy"))
    h_g = split_hash(np.load(S20 / "seed30_train_G.npy"))
    ev = r["events"]
    checks = {
        "status": r["status"] == "completed" and r["steps_completed"] == 30,
        "alternate_every": r.get("alternate_every") == 5,
        "trace": ev.get("alternation_trace") == [[5, h_g], [10, h_f], [15, h_g]],
        "count": ev.get("alternations") == 3,
        "switch": ev.get("switch", {}).get("step") == 20 and ev["switch"].get("new_train_hash") == h_g,
        "first_split": r["split_hash"] == h_f,
    }
    print(f"[smoke] {checks}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
