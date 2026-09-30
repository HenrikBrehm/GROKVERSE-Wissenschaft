"""EXP-134 (N62, session 64, 2026-10-01; written before any run): does the choice of arithmetic facts still steer the
number embeddings of our own small LM when its body was first pretrained on text only?

Bridge between LM1 (from scratch: steers, confirmed) and the Pythia line (pretrained 160 M: does not steer; with reset
number rows it does not even generalize, EXP-133). Here the number tokens <n0>..<n112> never occur in the pretraining
text (lm_stage2 keeps them out of the stories), so after phase 1 only the body (blocks, positions, text rows) is pretrained;
the number rows got only output-side softmax gradients and weight decay (no frequency structure expected).

Per model seed S (one job): phase 1 = lm_stage2.run with --arith-facts 0 (text only, loss on text), N1 steps, text read
from the SECOND half of the token file (phase 2 reads from the start as in LM1, so no text is seen twice); then arms F and
G = exactly the LM1 configuration (K = 19, answer loss, 6000 steps, LM1 splits/test files), but the model starts from the
phase-1 weights (fresh AdamW and warmup, as run() builds them). lm_stage2.py is NOT modified (LM1/LM3 manifests bind its
hash); the wrapper only swaps the module's GPT/Stream classes. Sidecar pretrain.json in every phase-2 run dir.

  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-134-text-pretrain-steering/ft_textpre.py \
      --seed 4100 --pair 4000 --device cuda
  ... ft_textpre.py --selftest --device cuda     (tiny: phase 1 + one arm, checks weights are really loaded, text offset)
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TRAINER = ROOT / "lab/experiments/EXP-105-lm-ladder-stage2/lm_stage2.py"
SPL = ROOT / "lab/confirm/lm1_splits"
N1 = 6000                                   # pretraining steps (= the LM1 fact-phase budget)


def load_trainer():
    spec = importlib.util.spec_from_file_location("lm_stage2", TRAINER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ns(**kw) -> argparse.Namespace:
    base = dict(batch=32, ctx=256, d=384, layers=6, heads=6, lr=6e-4, warmup=500, wd=0.1, loss="answer")
    base.update(kw)
    return argparse.Namespace(**base)


def phase1(L, seed: int, pair: int, steps: int, device: str, out_root: Path) -> Path:
    """Text-only pretraining; returns the checkpoint path. Stream starts in the second half of the text."""
    orig = L.Stream

    class OffsetStream(orig):
        def __init__(self, text, *a, **k):
            super().__init__(text, *a, **k)
            self.text_pos = len(text) // 2

    L.Stream = OffsetStream
    try:
        res = L.run(ns(seed=seed, split_file=str(SPL / f"seed{pair}_F.npy"), test_file=str(SPL / f"seed{pair}_test.npy"),
                       steps=steps, device=device, out_root=str(out_root), arith_facts=0))
    finally:
        L.Stream = orig
    assert res["status"] == "completed", res.get("status")
    assert res["text_wraps"] == 0, "phase 1 wrapped the text"
    ck = out_root / res["run_id"] / "checkpoint.pt"
    # review M1: result.json is written before the final checkpoint; a kill in between would leave an older checkpoint
    assert torch.load(ck, map_location="cpu", weights_only=False)["step"] == steps, "phase-1 checkpoint is not the final one"
    return ck


def phase2(L, seed: int, pair: int, arm: str, steps: int, device: str, out_root: Path, ck: Path) -> dict:
    state = torch.load(ck, map_location="cpu", weights_only=False)["model"]
    orig = L.GPT

    class PretrainedGPT(orig):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)                    # consumes the same init RNG as a from-scratch run
            self.load_state_dict(state)

    L.GPT = PretrainedGPT
    try:
        res = L.run(ns(seed=seed, split_file=str(SPL / f"seed{pair}_{arm}.npy"), test_file=str(SPL / f"seed{pair}_test.npy"),
                       steps=steps, device=device, out_root=str(out_root), arith_facts=19))
    finally:
        L.GPT = orig
    side = out_root / res["run_id"] / "pretrain.json"
    if not side.exists():
        side.write_text(json.dumps({"pretrain_run": ck.parent.name, "pretrain_checkpoint": str(ck.relative_to(ROOT)) if ck.is_relative_to(ROOT) else str(ck),
                                    "pretrain_sha256": hashlib.sha256(ck.read_bytes()).hexdigest(),
                                    "wrapper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}, indent=1),
                        encoding="utf-8")
    return res


def selftest(device: str) -> None:
    L = load_trainer()
    tmp = Path(tempfile.mkdtemp(prefix="exp134_"))
    tiny = dict(d=32, layers=1, heads=2, batch=4, ctx=256, warmup=5)   # ctx 256: the K = 19 block needs ~200 tokens
    base_ns = ns
    try:
        globals()["ns"] = lambda **kw: base_ns(**{**tiny, **kw})
        ck = phase1(L, 4100, 4000, 10, device, tmp / "pre")
        pre = torch.load(ck, map_location="cpu", weights_only=False)
        assert pre["stream"]["text_pos"] > 113651592 // 2 - 1, "offset not applied"
        # the phase-2 model must start from the phase-1 weights: check the step-0 snapshot of the number rows
        res = phase2(L, 4100, 4000, "F", 3, device, tmp / "ft", ck)
        import numpy as np
        snap0 = np.load(tmp / "ft" / res["run_id"] / "we_snapshots.npy")[0]
        num = L.NUM_ID
        want = pre["model"]["emb.weight"][num].float().numpy()
        assert np.allclose(snap0, want), "phase-2 start is not the phase-1 model"
        assert (tmp / "ft" / res["run_id"] / "pretrain.json").exists()
        assert L.GPT.__name__ == "GPT" and L.Stream.__name__ == "Stream", "classes not restored"
        # a from-scratch run with the same seed must differ at step 0 (sanity of the check above)
        scratch = L.run(base_ns(**{**tiny, "seed": 4100, "split_file": str(SPL / "seed4000_F.npy"),
                                   "test_file": str(SPL / "seed4000_test.npy"), "steps": 3, "device": device,
                                   "out_root": str(tmp / "scratch"), "arith_facts": 19}))
        s0 = np.load(tmp / "scratch" / scratch["run_id"] / "we_snapshots.npy")[0]
        assert not np.allclose(s0, snap0), "scratch equals pretrained start"
        print("selftest ok")
    finally:
        globals()["ns"] = base_ns
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int)
    ap.add_argument("--pair", type=int, help="LM1 split seed (4000 / 4001)")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(a.device)
        return
    L = load_trainer()
    ck = phase1(L, a.seed, a.pair, N1, a.device, HERE / "raw_pre")
    for arm in ("F", "G"):
        res = phase2(L, a.seed, a.pair, arm, 6000, a.device, HERE / "raw_ft", ck)
        print(f"EXP-134 seed {a.seed} {arm}: {res['status']}, test {res['curve'][-1][2]:.3f}", flush=True)


if __name__ == "__main__":
    main()
