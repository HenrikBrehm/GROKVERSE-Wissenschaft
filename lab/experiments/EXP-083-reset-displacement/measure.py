"""EXP-083: how much does each reset at a switch after 50 steps undo? (exploration, known seeds of N29b/N29c)

For every seed of N29b (attention vs MLP reset) and N29c (W_V/W_O vs W_Q/W_K reset) and both first splits (A, B), compare the
50-step model of this experiment (jobs.txt, same init/split/device as the frozen blocks) with its initialization and report, per reset
part, the Frobenius displacement ||W(50) - W(0)|| (what a reset to the init removes) and the displacement relative to ||W(0)||.

Gates (fail closed, before any number is printed):
  * the rebuilt init has the checksum stored in the run's result.json (init_checksum_shared);
  * W_E at step 0 and at step 50 matches the stored W_E snapshots (steps 0 and 50) of the frozen block's no-reset run with the
    same first split, max |diff| <= TOL (GPU runs are not bit-exact; TOL is fixed here before any run).

Usage (in the run window, via the guard):  python lab/tools/guarded_run.py -- python lab/experiments/EXP-083-reset-displacement/measure.py
Only reads stored runs and writes summary.json next to this file. Pre-registered reading: README.md.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "training"))
from grokverse.config import get_config  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.seed import set_seed  # noqa: E402

TOL = 1e-3            # max |W_E diff| against the frozen block's snapshots (fixed before any run)
PARTS = {"attn": ("W_Q", "W_K", "W_V", "W_O"), "mlp": ("W_in", "W_out"), "qk": ("W_Q", "W_K"), "vo": ("W_V", "W_O"),
         "unembed": ("W_U",), "we": ("W_E",)}
BLOCKS = {"n29b": (range(2300, 2320), ("attn", "mlp")), "n29c": (range(2320, 2340), ("vo", "qk"))}
RAW = HERE / "raw"


def init_state(seed: int) -> tuple[dict[str, np.ndarray], torch.nn.Module]:
    """Same order as freq_ban.run: set_seed, (dataset uses its own generator), build_model on the CPU."""
    cfg = get_config("arch25k", seed=seed, steps=50, threads=1, p=113, task="add", arch="transformer")
    set_seed(cfg.seed)
    model = build_model(cfg)
    return {n: prm.detach().cpu().numpy().astype(np.float64) for n, prm in model.named_parameters()}, model


def checksum(model) -> str:
    h = hashlib.sha256()
    for name, prm in sorted(model.named_parameters()):
        h.update(name.encode())
        h.update(np.ascontiguousarray(prm.detach().cpu().numpy()).tobytes())
    return h.hexdigest()


def index_runs(root: Path) -> dict[tuple[str, str | None], Path]:
    """(split_file basename, reset_at_switch) -> run dir; only completed runs."""
    out = {}
    for rj in root.glob("*/result.json"):
        r = json.loads(rj.read_text())
        if r.get("status") != "completed":
            continue
        key = (Path(r["split_file"]).name, r.get("reset_at_switch"))
        if key in out:
            raise SystemExit(f"duplicate run for {key}: {out[key]} and {rj.parent}")
        out[key] = rj.parent
    return out


def part_norms(w50: dict, w0: dict, names) -> tuple[float, float]:
    d2 = sum(float(((w50[n] - w0[n]) ** 2).sum()) for n in names)
    n2 = sum(float((w0[n] ** 2).sum()) for n in names)
    return float(np.sqrt(d2)), float(np.sqrt(d2 / n2))


def main() -> None:
    mine = index_runs(RAW)
    rows, failures = [], []
    for blk, (seeds, pair) in BLOCKS.items():
        frozen = index_runs(ROOT / "lab" / "confirm" / f"{blk}_raw")
        for s in seeds:
            w0, model = init_state(s)
            cs = checksum(model)
            for first in ("A", "B"):
                split = f"{blk}_seed{s}_w0_{first}.npy"
                if (split, None) not in mine:
                    failures.append(f"missing EXP-083 run {split}")
                    continue
                run = mine[(split, None)]
                res = json.loads((run / "result.json").read_text())
                if res["init_checksum_shared"] != cs:
                    failures.append(f"init checksum mismatch {split}")
                    continue
                if res["steps_completed"] != 50:
                    failures.append(f"{split}: steps_completed {res['steps_completed']} != 50")
                    continue
                state = torch.load(run / "model_final.pt", map_location="cpu", weights_only=True)
                w50 = {n: t.numpy().astype(np.float64) for n, t in state.items()}
                ref = frozen.get((split, None))          # the block's no-reset run whose first split is `split`
                if ref is None:
                    failures.append(f"no frozen reference for {split}")
                    continue
                snaps, st = np.load(ref / "we_snapshots.npy"), np.load(ref / "we_snapshot_steps.npy").tolist()
                d0 = float(np.abs(snaps[st.index(0)] - w0["W_E"][:113]).max())
                d50 = float(np.abs(snaps[st.index(50)] - w50["W_E"][:113]).max())
                if max(d0, d50) > TOL:
                    failures.append(f"{split}: W_E differs from frozen snapshot (step0 {d0:.2e}, step50 {d50:.2e})")
                    continue
                row = {"block": blk, "seed": s, "first": first, "we_diff_step0": d0, "we_diff_step50": d50}
                for part, names in PARTS.items():
                    row[f"abs_{part}"], row[f"rel_{part}"] = part_norms(w50, w0, names)
                row["n_params"] = {part: int(sum(w0[n].size for n in names)) for part, names in PARTS.items()}
                rows.append(row)
    if failures:
        print("\n".join(failures))
        raise SystemExit(f"EXP-083: {len(failures)} gate failure(s); no numbers reported")
    summary = {"tol": TOL, "rows": rows, "pairs": {}}
    for blk, (seeds, (big, small)) in BLOCKS.items():
        per_seed = {}
        for r in rows:
            if r["block"] == blk:
                per_seed.setdefault(r["seed"], []).append(r)
        out = {}
        for kind in ("abs", "rel"):
            ratio = np.array([np.mean([x[f"{kind}_{big}"] for x in v]) / np.mean([x[f"{kind}_{small}"] for x in v])
                              for v in per_seed.values()])
            out[kind] = {"median_ratio": float(np.median(ratio)), "n_big_gt_small": int((ratio > 1).sum()), "n": int(ratio.size),
                         f"mean_{big}": float(np.mean([x[f"{kind}_{big}"] for v in per_seed.values() for x in v])),
                         f"mean_{small}": float(np.mean([x[f"{kind}_{small}"] for v in per_seed.values() for x in v]))}
            n, k = out[kind]["n"], out[kind]["n_big_gt_small"]
            out[kind]["reading"] = ("size alternative contradicted" if n - k >= 15 else
                                    "size alternative open" if k >= 15 else "unclear")
        readings = {out["abs"]["reading"], out["rel"]["reading"]}
        out["combined_reading"] = readings.pop() if len(readings) == 1 else "unclear"   # README: abs/rel disagree -> unclear
        summary["pairs"][f"{blk}: {big} vs {small}"] = out
    (HERE / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary["pairs"], indent=1))


if __name__ == "__main__":
    main()
