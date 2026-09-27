"""EXP-065 (EXPLORATION): local sensitivity per equal parameter-step norm on the bound P2c models. Definition: README.md. Run under guarded_run.py."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "tools"))
import confirm_p2c as c  # noqa: E402

_s = importlib.util.spec_from_file_location("exp061", LAB / "experiments/EXP-061-grad-alignment/analyze.py")
G61 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(G61)
e51, e55 = c.p2.e51, c.p2.e55
N_SEEDS, N_CTRL, REL_DELTA, P = 40, 4, 0.02, 113


def margin(m, W: np.ndarray, test: np.ndarray) -> float:
    return e55.evaluate(m, W, test)["margin"]


def main() -> None:
    man = json.loads((LAB / "confirm/P2c_manifest.json").read_text(encoding="utf-8"))
    summ = json.loads((LAB / "confirm/P2c_summary.json").read_text(encoding="utf-8"))
    seeds = [r["seed"] for r in summ["rows"] if r["valid"]][:N_SEEDS]
    rows = []
    for s in seeds:
        T = {a: json.loads((c.SPL / f"{c.stem(s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
        trains = [np.load(c.SPL / f"{c.stem(s, a)}.npy") for a in "FG"]
        test = np.setdiff1d(np.arange(P * P), np.union1d(*trains))
        for arm, other in (("F", "G"), ("G", "F")):
            split = c.SPL / f"{c.stem(s, arm)}.npy"
            d = c.run_dir(["x", c.FB, "--seed", str(s), "--threads", "1", "--device", "cuda", "--split-file", str(split)])
            m = c.p2.load_model_bytes(c.BLOCK.bound_bytes(man, d / "model_final.pt"))
            W = m.W_E.detach().numpy().astype(np.float64)[:P]
            delta = REL_DELTA * np.linalg.norm(W)
            base = margin(m, None, test)
            pool = sorted(e51.control_set(T[arm], T[other]))
            rng = np.random.default_rng([65, s, ord(arm)])
            sets = {"own": T[arm]} | {f"c{i}": sorted(rng.choice(pool, 5, replace=False).tolist()) for i in range(N_CTRL)}
            drop = {}
            for k, S in sets.items():
                PS = G61.project(W, S)
                drop[k] = base - margin(m, W - delta * PS / np.linalg.norm(PS), test)
            ctrl = float(np.mean([drop[f"c{i}"] for i in range(N_CTRL)]))
            rows.append({"seed": s, "arm": arm, "base_margin": base, "drop_own": drop["own"], "drop_ctrl_mean": ctrl,
                         "log_ratio": float(np.log(drop["own"] / ctrl)) if drop["own"] > 0 and ctrl > 0 else None})
    lr = np.array([r["log_ratio"] for r in rows if r["log_ratio"] is not None])
    out = {"n_models": len(rows), "n_ratio": int(len(lr)), "log_ratio_mean": float(lr.mean()), "log_ratio_sd": float(lr.std(ddof=1)),
           "share_positive": float((lr > 0).mean()), "drop_own_median": float(np.median([r["drop_own"] for r in rows])),
           "drop_ctrl_median": float(np.median([r["drop_ctrl_mean"] for r in rows])), "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
