"""EXP-038 smoke check: both smoke runs completed (40 steps, switch at 30); the reset touched exactly W_E ("we") resp.
all other parameters ("rest"), i.e. n_we = numel(W_E) and n_we + n_rest = all parameters of the arch25k model."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "training"))
from grokverse.config import get_config  # noqa: E402
from grokverse.models import build_model  # noqa: E402


def main() -> int:
    model = build_model(get_config("arch25k", seed=30))
    n_all, n_we = sum(q.numel() for q in model.parameters()), model.W_E.numel()
    got = {}
    for which in ("we", "rest"):
        runs = list((HERE / "raw_smoke").glob(f"*_rs{which}/result.json"))
        if len(runs) != 1:
            print(f"[smoke] {which}: expected one run, found {len(runs)}")
            return 1
        r = json.loads(runs[0].read_text(encoding="utf-8"))
        ev = r["events"].get("reset_at_switch", {})
        if not (r["status"] == "completed" and r["steps_completed"] == 40 and r.get("reset_at_switch") == which
                and ev.get("which") == which and r["events"].get("switch", {}).get("step") == 30):
            print(f"[smoke] {which}: status/steps/flags wrong: {ev}")
            return 1
        got[which] = ev["n_params"]
    ok = got["we"] == n_we and got["we"] + got["rest"] == n_all
    print(f"[smoke] n_we={got['we']} (W_E {n_we}), n_rest={got['rest']}, all={n_all}, ok={ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
