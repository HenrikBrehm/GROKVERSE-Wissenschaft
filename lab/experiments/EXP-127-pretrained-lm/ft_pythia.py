"""EXP-127 (rule 20 e2, session 58): does the choice of arithmetic facts steer the Fourier frequencies of the number-token
embeddings when a PRETRAINED language model (Pythia-160M, untied input/output embeddings) is fine-tuned on them?
Session 58 (2026-09-30); UNTESTED until the selftest and a smoke run have passed.

Model: EleutherAI/pythia-160m at a pinned revision (Hugging Face, Apache-2.0), fp32, all parameters trained.
Numbers: the tokens " 0" .. " 112" (one GPT-NeoX token each; checked at start). Task: c = (a + b) mod 113 with a neutral
operator token " @" (so the pretrained integer addition is not invoked by "+"): one fact = [ a, " @", b, " =", c, "\\n" ].
A training sequence = end-of-text token + K facts; loss only on the answer tokens c (cross-entropy over the full vocabulary).
Facts: the flat indices a*113 + b of one split file (EXP-102/LM1 construction); every fact equally often (fixed cycle,
reshuffled per round, no weighted redraw), as in lm_stage2.py.
Streams (numpy SeedSequence [127, seed, k]): k=1 fact order, k=2 torch seed (dropout is off in Pythia; the stream is only
kept for symmetry). Arms F and G of one seed share the pretrained weights and all other settings; only the facts differ.
Measures (every EVAL_EVERY steps and at 0): rows of the 113 number tokens in embed_in and embed_out (snapshots), held-out
accuracy (test file; prompt [eot, a, @, b, =], argmax over the 113 number tokens), accuracy on up to 2000 train facts,
mean answer loss of the last steps. End: ablation as in EXP-120 (remove the cos/sin subspace of a frequency set from the
number rows of the input side, the output side or both; own targets, other split's targets, 4 control sets from 1..56 without
both target sets, numpy default_rng(SeedSequence([127, split_seed])) ) -> held-out accuracy per case.
Runs are short (< 1 h); no mid-run checkpoint: an interrupted run restarts from scratch (a completed run is skipped).

  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-127-pretrained-lm/ft_pythia.py --selftest
  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-127-pretrained-lm/ft_pythia.py \\
      --seed S --split-file <split.npy> --test-file <test.npy> --targets-file <seedX.json> --steps N --out-root <dir>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
P = 113
REPO, REVISION = "EleutherAI/pythia-160m", "50f5173d932e8e61f858120bcb800b97af589f46"
EVAL_EVERY, TRAIN_EVAL = 250, 2000


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save_atomic(path: Path, obj, kind: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    if kind == "npy":
        with open(tmp, "wb") as f:
            np.save(f, obj)
    else:
        tmp.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    os.replace(tmp, path)


def load_model(device: str):
    from transformers import AutoTokenizer, GPTNeoXForCausalLM
    tok = AutoTokenizer.from_pretrained(REPO, revision=REVISION)
    model = GPTNeoXForCausalLM.from_pretrained(REPO, revision=REVISION, dtype=torch.float32).to(device)
    return tok, model


def token_ids(tok) -> dict:
    def one(s: str) -> int:
        ids = tok.encode(s, add_special_tokens=False)
        assert len(ids) == 1, (s, ids)
        return ids[0]
    num = [one(f" {n}") for n in range(P)]
    assert len(set(num)) == P
    return {"num": num, "op": one(" @"), "eq": one(" ="), "nl": one("\n"), "eot": tok.eos_token_id}


def power(W: np.ndarray) -> np.ndarray:
    """Same as EXP-102 analyze.power: power of frequencies 1..56 over the number index, summed over the embedding dims."""
    sq = (np.abs(np.fft.fft(W.astype(np.float64), axis=0)) ** 2).sum(1)
    return 2.0 * sq[1:(P - 1) // 2 + 1] / P


def projector(S: list[int]) -> torch.Tensor:
    n = np.arange(P)
    B = np.stack([f(2 * np.pi * k * n / P) for k in S for f in (np.cos, np.sin)], 1)
    Q, _ = np.linalg.qr(B)
    return torch.tensor(Q @ Q.T, dtype=torch.float32)


class Stream:
    def __init__(self, facts: np.ndarray, ids: dict, seed: int, k: int):
        self.facts, self.ids, self.k = facts, ids, k
        self.g = np.random.default_rng(np.random.SeedSequence([127, seed, 1]))
        self.order, self.pos, self.rounds = self.g.permutation(len(facts)), 0, 0

    def next_fact(self) -> int:
        if self.pos == len(self.order):
            self.order, self.pos, self.rounds = self.g.permutation(len(self.facts)), 0, self.rounds + 1
        f = int(self.facts[self.order[self.pos]])
        self.pos += 1
        return f

    def batch(self, bs: int) -> tuple[torch.Tensor, torch.Tensor]:
        """x: bs x (1 + 6k) tokens; y: next-token targets with -100 everywhere except the answer positions."""
        L = 1 + 6 * self.k
        x = np.empty((bs, L), np.int64)
        y = np.full((bs, L), -100, np.int64)
        num, op, eq, nl = self.ids["num"], self.ids["op"], self.ids["eq"], self.ids["nl"]
        for i in range(bs):
            row = [self.ids["eot"]]
            for _ in range(self.k):
                a, b = divmod(self.next_fact(), P)
                c = (a + b) % P
                y[i, len(row) + 3] = num[c]                     # position of " =" predicts c
                row += [num[a], op, num[b], eq, num[c], nl]
            x[i] = row
        return torch.from_numpy(x), torch.from_numpy(y)


def prompts(pairs: np.ndarray, ids: dict) -> tuple[torch.Tensor, torch.Tensor]:
    a, b = pairs // P, pairs % P
    num = ids["num"]
    x = torch.tensor([[ids["eot"], num[i], ids["op"], num[j], ids["eq"]] for i, j in zip(a, b)])
    return x, torch.from_numpy((a + b) % P)


@torch.no_grad()
def accuracy(model, x: torch.Tensor, c: torch.Tensor, num: torch.Tensor, device: str) -> float:
    model.eval()
    head = model.get_output_embeddings()
    pred = torch.cat([head(model.gpt_neox(x[i:i + 1024].to(device)).last_hidden_state[:, -1])[:, num].argmax(1).cpu()
                      for i in range(0, len(x), 1024)])
    model.train()
    return float((pred == c).float().mean())


def run(a: argparse.Namespace) -> dict:
    facts = np.load(a.split_file).astype(np.int64)
    test = np.load(a.test_file).astype(np.int64)
    assert facts.ndim == 1 and len(np.unique(facts)) == len(facts) and 0 <= facts.min() and facts.max() < P * P
    assert not np.intersect1d(test, facts).size, "test facts overlap the training facts"
    tj = json.loads(Path(a.targets_file).read_text(encoding="utf-8"))
    arm = a.arm or Path(a.split_file).stem.split("_")[-1]
    assert arm in ("F", "G"), arm
    targets = tj["targets"]
    own, other = targets[arm], targets["G" if arm == "F" else "F"]
    cfg = {"seed": a.seed, "arm": arm, "split_sha256": sha(a.split_file), "test_sha256": sha(a.test_file),
           "targets_sha256": sha(a.targets_file), "targets": targets, "steps": a.steps, "batch": a.batch, "k_facts": a.k,
           "lr": a.lr, "wd": a.wd, "warmup": a.warmup, "betas": [0.9, 0.95], "operator": " @", "model": REPO,
           "revision": REVISION, "device": a.device, "script_sha256": sha(__file__), "torch": torch.__version__}
    import transformers
    cfg["transformers"] = transformers.__version__
    h = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:16]
    out = Path(a.out_root) / f"pt_seed{a.seed}_{Path(a.split_file).stem}_steps{a.steps}_{h}"
    if (out / "result.json").exists() and json.loads((out / "result.json").read_text(encoding="utf-8")).get("status") == "completed":
        print(f"[skip] completed: {out}")
        return {}
    out.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(int(np.random.SeedSequence([127, a.seed, 2]).generate_state(1)[0]))
    t0 = time.time()
    tok, model = load_model(a.device)
    ids = token_ids(tok)
    num = torch.tensor(ids["num"], device=a.device)
    E_in, E_out = model.get_input_embeddings().weight, model.get_output_embeddings().weight
    cfg["n_params"] = sum(p.numel() for p in model.parameters())
    cfg["tied"] = E_in.data_ptr() == E_out.data_ptr()
    assert not cfg["tied"], "Pythia-160M is expected to have untied embeddings"
    decay = [p for n, p in model.named_parameters() if p.ndim >= 2]
    no_decay = [p for n, p in model.named_parameters() if p.ndim < 2]
    opt = torch.optim.AdamW([{"params": decay, "weight_decay": a.wd}, {"params": no_decay, "weight_decay": 0.0}],
                            lr=a.lr, betas=(0.9, 0.95))
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / max(1, a.warmup)))
    stream = Stream(facts, ids, a.seed, a.k)
    xt, ct = prompts(test, ids)
    tr = facts[np.random.default_rng(np.random.SeedSequence([127, a.seed, 3])).permutation(len(facts))[:TRAIN_EVAL]]
    xr, cr = prompts(tr, ids)
    snaps_in, snaps_out, steps_snap, curve = [], [], [], []
    losses: list[float] = []

    def snapshot(step: int) -> None:
        snaps_in.append(E_in.detach()[num].float().cpu().numpy().copy())
        snaps_out.append(E_out.detach()[num].float().cpu().numpy().copy())
        steps_snap.append(step)
        te, tra = accuracy(model, xt, ct, num, a.device), accuracy(model, xr, cr, num, a.device)
        lo = float(np.mean(losses[-50:])) if losses else float("nan")
        curve.append([step, tra, te, lo])
        pin, pout = power(snaps_in[-1]), power(snaps_out[-1])
        s = lambda pw, S: float(pw[[k - 1 for k in S]].sum() / pw.sum())   # noqa: E731
        print(f"step {step} train {tra:.3f} test {te:.3f} loss {lo:.4f} own_in {s(pin, own):.3f} other_in {s(pin, other):.3f} "
              f"own_out {s(pout, own):.3f} other_out {s(pout, other):.3f} t {time.time() - t0:.0f}s", flush=True)

    model.train()
    snapshot(0)
    for step in range(1, a.steps + 1):
        x, y = stream.batch(a.batch)
        x, y = x.to(a.device), y.to(a.device)
        sel = y != -100                                                  # answer labels sit at the " =" positions
        h = model.gpt_neox(x).last_hidden_state[sel]                     # output layer only where the loss is taken
        loss = F.cross_entropy(model.get_output_embeddings()(h), y[sel])
        if not torch.isfinite(loss):
            print(f"non-finite loss at step {step}", flush=True)
            save_atomic(out / "result.json", {"status": "diverged", "step": step, "config": cfg, "curve": curve}, "json")
            sys.exit(1)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        sched.step()
        losses.append(loss.item())
        if step % EVAL_EVERY == 0 or step == a.steps:
            snapshot(step)
    save_atomic(out / "in_snapshots.npy", np.stack(snaps_in).astype(np.float32), "npy")
    save_atomic(out / "out_snapshots.npy", np.stack(snaps_out).astype(np.float32), "npy")
    save_atomic(out / "snapshot_steps.npy", np.asarray(steps_snap), "npy")
    abl = ablation(model, xt, ct, num, own, other, targets, tj.get("seed", a.seed), a.device)
    res = {"status": "completed", "config": cfg, "curve": curve, "ablation": abl, "rounds": stream.rounds,
           "seconds": time.time() - t0, "max_mem_gb": (torch.cuda.max_memory_allocated() / 2 ** 30) if a.device == "cuda" else None}
    save_atomic(out / "result.json", res, "json")
    print(json.dumps({"out": str(out), "test": curve[-1][2], "ablation": abl}), flush=True)
    return res


@torch.no_grad()
def ablation(model, xt, ct, num, own, other, targets, split_seed, device) -> dict:
    rng = np.random.default_rng(np.random.SeedSequence([127, int(split_seed)]))
    free = [k for k in range(1, 57) if k not in targets["F"] and k not in targets["G"]]
    controls = [sorted(rng.choice(free, 5, replace=False).tolist()) for _ in range(4)]
    W = {"in": model.get_input_embeddings().weight.data, "out": model.get_output_embeddings().weight.data}
    X0 = {s: W[s][num].clone() for s in W}
    cache: dict = {}

    def acc(S, sides) -> float:
        for s in sides:
            W[s][num] = X0[s] - cache.setdefault(tuple(S), projector(S).to(device)) @ X0[s]
        r = accuracy(model, xt, ct, num, device)
        for s in sides:
            W[s][num] = X0[s]
        return r

    out = {"controls": controls, "base": accuracy(model, xt, ct, num, device)}
    for name, sides in (("in", ("in",)), ("out", ("out",)), ("both", ("in", "out"))):
        out[f"{name}_own"], out[f"{name}_other"] = acc(own, sides), acc(other, sides)
        out[f"{name}_ctl"] = [acc(S, sides) for S in controls]
        out[f"C_{name}"] = out[f"{name}_other"] - out[f"{name}_own"]
    return out


def selftest(device: str) -> None:
    """No training: tokens, batch layout, loss mask, projector, prompt accuracy path."""
    tok, model = load_model(device)
    ids = token_ids(tok)
    facts = np.array([37 * P + 58, 100 * P + 50])
    s = Stream(facts, ids, 0, 2)
    x, y = s.batch(3)
    assert x.shape == (3, 13) and (y != -100).sum() == 6
    row = x[0].tolist()
    # every answer label sits at the " =" position and equals the token that follows it
    for i in range(3):
        pos = (y[i] != -100).nonzero().flatten().tolist()
        for p_ in pos:
            assert x[i, p_] == ids["eq"] and y[i, p_] == x[i, p_ + 1], (i, p_)
            a_, b_, c_ = (ids["num"].index(int(x[i, p_ + k])) for k in (-3, -1, 1))
            assert c_ == (a_ + b_) % P
    print("decoded:", repr(tok.decode(row)))
    xb, yb = x.to(device), y.to(device)
    with torch.no_grad():
        full = F.cross_entropy(model(xb).logits.reshape(-1, model.config.vocab_size), yb.reshape(-1), ignore_index=-100)
        sel = yb != -100
        part = F.cross_entropy(model.get_output_embeddings()(model.gpt_neox(xb).last_hidden_state[sel]), yb[sel])
    assert abs(float(full) - float(part)) < 1e-4 * max(1.0, float(full)), (float(full), float(part))
    print(f"loss paths agree: full-logit {float(full):.6f} vs answer-only {float(part):.6f}")
    Pm = projector([3, 7])
    assert torch.allclose(Pm @ Pm, Pm, atol=1e-5) and abs(float(torch.trace(Pm)) - 4) < 1e-4
    n = np.arange(P)
    W = np.stack([np.cos(2 * np.pi * 5 * n / P), np.sin(2 * np.pi * 9 * n / P)], 1)
    pw = power(W)
    assert set(np.argsort(pw)[-2:] + 1) == {5, 9}
    num = torch.tensor(ids["num"], device=device)
    xt, ct = prompts(np.arange(0, P * P, 997), ids)
    acc = accuracy(model, xt, ct, num, device)
    print(f"selftest ok; pretrained accuracy on {len(ct)} mod-113 prompts: {acc:.3f}; "
          f"params {sum(p.numel() for p in model.parameters())}; tied {model.get_input_embeddings().weight.data_ptr() == model.get_output_embeddings().weight.data_ptr()}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--split-file")
    ap.add_argument("--test-file")
    ap.add_argument("--targets-file")
    ap.add_argument("--arm", choices=("F", "G"))
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--k", type=int, default=16, help="facts per sequence")
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--wd", type=float, default=0.1)
    ap.add_argument("--warmup", type=int, default=100)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--out-root", default=str(HERE / "raw"))
    ap.add_argument("--threads", type=int, default=1)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    if a.selftest:
        selftest(a.device)
        sys.stdout.flush()
        os._exit(0)
    run(a)
    sys.stdout.flush()
    os._exit(0)                     # results are written atomically; skip the ROCm teardown that hung ~150 s in the smoke


if __name__ == "__main__":
    main()
