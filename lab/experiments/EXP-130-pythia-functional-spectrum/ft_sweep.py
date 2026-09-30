"""EXP-130 (session 61): functional frequency spectrum of a fine-tuned Pythia-160M on (a + b) mod 113.

Trains exactly as EXP-127 (imports ft_pythia.py unchanged, same arguments and run id scheme) and, after training, extends
the end-of-run ablation by a single-frequency sweep: for every k in 1..56 the cos/sin subspace of k is projected out of
the 113 number-token rows of the input side, the output side, or both (ft_pythia.projector), and held-out accuracy is
measured on the run's test prompts. Two extra sets: the pretrained top-8 input frequencies of Pythia-160M
(pretrained_spectrum.json, EXP-127: 1, 2, 3, 11, 4, 5, 23, 45) and the "decimal" set 11, 23, 45 (periods ~10, 5, 2.5).
Results go into result.json["ablation"]["sweep"]; a sidecar sweep_meta.json records this wrapper's hash. The fine-tuned
weights are saved (fp16) to <out-root>/models/model_split<seed>_<arm>.pt before the sweep (for layer-wise measures later).
Written in session 61 BEFORE any EXP-130 run; UNTESTED until the smoke run has passed.

  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-130-pythia-functional-spectrum/ft_sweep.py \\
      --seed S --split-file <split.npy> --test-file <test.npy> --targets-file <seedX.json> --steps N --out-root <dir>
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "EXP-127-pretrained-lm"))
import ft_pythia as ft  # noqa: E402

PRETRAINED_TOP8_IN = [1, 2, 3, 11, 4, 5, 23, 45]
DECIMAL = [11, 23, 45]
_orig_ablation = ft.ablation


MODEL_DIR: Path | None = None   # set in main() from --out-root; the fine-tuned weights are kept for later layer-wise measures


def save_model(model, split_seed: int, arm: str) -> None:
    """fp16 state dict (~0.33 GB), written atomically BEFORE the sweep (session 61, before any EXP-130 run)."""
    import torch
    if MODEL_DIR is None:
        return
    path = MODEL_DIR / f"model_split{int(split_seed)}_{arm}.pt"
    tmp = path.with_suffix(".pt.tmp")
    torch.save({k: v.detach().half().cpu() for k, v in model.state_dict().items()}, tmp)
    tmp.replace(path)


def sweep_ablation(model, xt, ct, num, own, other, targets, split_seed, device) -> dict:
    arm = "F" if list(own) == list(targets["F"]) else "G"
    save_model(model, split_seed, arm)
    out = _orig_ablation(model, xt, ct, num, own, other, targets, split_seed, device)
    W = {"in": model.get_input_embeddings().weight.data, "out": model.get_output_embeddings().weight.data}
    X0 = {s: W[s][num].clone() for s in W}

    def acc(S: list[int], sides: tuple[str, ...]) -> float:
        Pm = ft.projector(S).to(device)
        for s in sides:
            W[s][num] = X0[s] - Pm @ X0[s]
        r = ft.accuracy(model, xt, ct, num, device)
        for s in sides:
            W[s][num] = X0[s]
        return r

    sides = {"in": ("in",), "out": ("out",), "both": ("in", "out")}
    sweep = {"base": ft.accuracy(model, xt, ct, num, device), "base_orig": out["base"]}
    # GPU kernels need not be bitwise reproducible: allow two argmax flips (review S61), warn only
    if abs(sweep["base"] - out["base"]) > 2 / len(ct) + 1e-9:
        print(f"[warn] base accuracy differs: {sweep['base']} vs {out['base']}", flush=True)
    for name, sd in sides.items():
        sweep[name] = [acc([k], sd) for k in range(1, 57)]
        sweep[f"{name}_pretrained_top8"] = acc(PRETRAINED_TOP8_IN, sd)
        sweep[f"{name}_decimal"] = acc(DECIMAL, sd)
    sweep["base_after"] = ft.accuracy(model, xt, ct, num, device)             # weights restored after the sweep?
    out["sweep"] = sweep
    print(json.dumps({"sweep_in_top": sorted(range(1, 57), key=lambda k: sweep["in"][k - 1])[:8]}), flush=True)
    return out


def main() -> None:
    global MODEL_DIR
    ft.ablation = sweep_ablation
    args = sys.argv[1:]
    if "--out-root" in args:
        root = Path(args[args.index("--out-root") + 1])
        root.mkdir(parents=True, exist_ok=True)
        MODEL_DIR = root / "models"
        MODEL_DIR.mkdir(exist_ok=True)
        meta = {"wrapper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "ft_pythia_sha256": ft.sha(ft.__file__), "argv": args}
        (root / f"sweep_meta_{hashlib.sha256(json.dumps(args).encode()).hexdigest()[:12]}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    ft.main()


if __name__ == "__main__":
    main()
