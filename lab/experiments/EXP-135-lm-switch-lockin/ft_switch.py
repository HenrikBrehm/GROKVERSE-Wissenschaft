"""EXP-135 (session 64, 2026-09-30; written before any run): does the LM show the early lock-in of K4? Data switch F -> G
after t steps in the LM1 configuration, then a fixed post-switch budget of 6000 steps (= the LM1 G-only budget).

Competing models: (start) as in the toy model, the choice locks within ~10 epochs (one LM1 epoch = 3831 facts / 608 facts per
step ~ 6.3 steps), so even t = 250 leaves F in the final spectrum; (learning) steering appears only with fact learning
(LM1 held-out >= 0.5 at 2500-3000 steps; no steering at step 1000, S59), so switches before learning leave no trace.

The frozen trainer lm_stage2.py is NOT modified (LM1/LM3 manifests bind its hash). The wrapper swaps the module's Stream
class for SwitchStream: after t * batch sequences the fact set becomes G (fresh permutation from the same fact generator,
fact_pos 0); model, AdamW state and the text stream continue. Switch state is derived from n_tok (every sequence has ctx + 1
tokens), so a resumed checkpoint restores it. The trainer's "train" accuracy keeps measuring F facts (F retention).
Sidecar switch.json in every run dir.

  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-135-lm-switch-lockin/ft_switch.py \
      --seed 4100 --pair 4000 --t 250 --device cuda
  ... ft_switch.py --selftest --device cuda
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TRAINER = ROOT / "lab/experiments/EXP-105-lm-ladder-stage2/lm_stage2.py"
SPL = ROOT / "lab/confirm/lm1_splits"
POST = 6000


def load_trainer():
    spec = importlib.util.spec_from_file_location("lm_stage2", TRAINER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_switch_stream(base, g_facts: np.ndarray, n_switch_seq: int):
    class SwitchStream(base):
        def __init__(self, text, facts, *a, **k):
            assert len(facts) == len(g_facts), "F and G must have equal size (order vector is reused)"
            super().__init__(text, facts, *a, **k)
            self.f_facts, self.switched = facts, False

        def n_seq(self) -> int:
            return self.n_tok // (self.ctx + 1)

        def sequence(self, keep_out=None):
            if not self.switched and self.n_seq() >= n_switch_seq:
                self.facts, self.switched = g_facts, True
                self.order, self.fact_pos = self.g_fact.permutation(len(g_facts)), 0
            return super().sequence(keep_out)

        def load(self, s: dict) -> None:
            super().load(s)
            # strictly '>': a checkpoint written exactly after step t precedes the lazy switch (review s64); sequence() switches
            if self.n_seq() > n_switch_seq:                  # the saved order/fact_pos already belong to G
                self.facts, self.switched = g_facts, True

    return SwitchStream


def run_one(L, seed: int, pair: int, t: int, device: str, out_root: Path, **over) -> dict:
    g = np.load(SPL / f"seed{pair}_G.npy").astype(np.int64)
    kw = dict(batch=32, ctx=256, d=384, layers=6, heads=6, lr=6e-4, warmup=500, wd=0.1, loss="answer")
    steps = over.pop("steps", t + POST)
    kw.update(over)
    side_info = {"switch_step": t, "G_split": f"lab/confirm/lm1_splits/seed{pair}_G.npy", "post_switch_steps": POST,
                 "wrapper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    orig = L.Stream
    L.Stream = make_switch_stream(orig, g, t * kw["batch"])
    try:
        res = L.run(argparse.Namespace(seed=seed, split_file=str(SPL / f"seed{pair}_F.npy"),
                                       test_file=str(SPL / f"seed{pair}_test.npy"), steps=steps,
                                       device=device, out_root=str(out_root), arith_facts=19, **kw))
    finally:
        L.Stream = orig
    side = out_root / res["run_id"] / "switch.json"
    if side.exists():                                    # a resumed run must use the same wrapper and switch (review s64)
        old = json.loads(side.read_text(encoding="utf-8"))
        assert old == side_info, ("switch.json differs from this wrapper/switch", old, side_info)
    else:
        side.write_text(json.dumps(side_info, indent=1), encoding="utf-8")
    return res


def selftest(device: str) -> None:
    """Tiny model: (1) the stream switches exactly after t*batch sequences and only G facts appear afterwards;
    (2) interrupted + resumed run equals a straight run (switch state survives the checkpoint)."""
    L = load_trainer()
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(L.TOK_FILE))
    ids = L.special_ids(tok)
    L.NUM_ID = ids["num"]
    f = np.load(SPL / "seed4000_F.npy").astype(np.int64)
    g = np.load(SPL / "seed4000_G.npy").astype(np.int64)
    text = np.load(L.TEXT_NPY, mmap_mode="r")
    S = make_switch_stream(L.Stream, g, 3 * 4)
    s = S(text, f, L.template_parts(tok), tok.token_to_id("Ċ"), ids["eot"], 4100, 256, 19)
    seen = []
    orig_next = s.next_fact
    s.next_fact = lambda: seen.append((s.n_seq(), orig_next())) or seen[-1][1]
    for _ in range(6):
        s.batch(4)
    fs, gs = set(f.tolist()), set(g.tolist())
    assert all(x in fs for n, x in seen if n < 12) and all(x in gs for n, x in seen if n >= 12), "switch boundary wrong"
    # resume equality with the real run(): straight 30 steps vs 20 + resume (checkpoint at CKPT_EVERY)
    tmp = Path(tempfile.mkdtemp(prefix="exp135_"))
    ck_every = L.CKPT_EVERY
    try:
        L.CKPT_EVERY = 10
        tiny = dict(d=32, layers=1, heads=2, batch=4, warmup=5)
        for tt in (15, 20):                              # checkpoint at 20 after the switch / exactly at the switch step
            resume_case(L, tt, device, tmp / f"t{tt}", tiny)
        assert L.Stream.__name__ == "Stream"
        print("selftest ok")
    finally:
        L.CKPT_EVERY = ck_every
        shutil.rmtree(tmp, ignore_errors=True)


def resume_case(L, tt: int, device: str, tmp: Path, tiny: dict) -> None:
    a = run_one(L, 4100, 4000, tt, device, tmp / "a", steps=30, **tiny)
    # interrupted run: stop after the step-20 checkpoint by limiting steps, then continue with the full budget
    b1 = run_one(L, 4100, 4000, tt, device, tmp / "b", steps=20, **tiny)
    rb = tmp / "b" / b1["run_id"]
    (rb / "result.json").unlink()
    import torch
    ck = torch.load(rb / "checkpoint.pt", weights_only=False)
    # the steps-20 run has another config hash; rename its checkpoint into the steps-30 run dir with the right hash
    a_dir = tmp / "a" / a["run_id"]
    ref = torch.load(a_dir / "checkpoint.pt", weights_only=False)
    ck["config_hash"] = ref["config_hash"]
    c_dir = tmp / "c" / a["run_id"]
    c_dir.mkdir(parents=True)
    torch.save(ck, c_dir / "checkpoint.pt")
    c = run_one(L, 4100, 4000, tt, device, tmp / "c", steps=30, **tiny)
    wa = torch.load(a_dir / "checkpoint.pt", weights_only=False)["model"]
    wc = torch.load(c_dir / "checkpoint.pt", weights_only=False)["model"]
    same = all(torch.equal(wa[k], wc[k]) for k in wa)
    print(f"t={tt}: resume bit-identical: {same}")
    # CPU is deterministic: weights must be bit-identical (curves differ only by the extra final eval of the 20-step run);
    # on the GPU nondeterministic kernels make this a smoke check only (s64: GPU False, CPU True)
    assert same or device != "cpu", f"t={tt}: resume across the switch differs on CPU"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int)
    ap.add_argument("--pair", type=int)
    ap.add_argument("--t", type=int)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest(a.device)
        return
    res = run_one(load_trainer(), a.seed, a.pair, a.t, a.device, HERE / f"raw_t{a.t}")
    print(f"EXP-135 seed {a.seed} t {a.t}: {res['status']}, test {res['curve'][-1][2]:.3f}", flush=True)


if __name__ == "__main__":
    main()
