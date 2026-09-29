"""EXP-105 (rule 20e, LM ladder stage 2): does the choice of arithmetic facts steer the number embeddings of a small
language model trained from scratch on natural text? Session 48 (2026-09-29); UNTESTED until the selftest has run.

Data. Text: TinyStoriesV2-GPT4 (Hugging Face roneneldan/TinyStories, revision f54c09fd, CDLA-Sharing-1.0), stored in
lab/external/tinystories (not in git). Own byte-level BPE (vocab 8192) trained on the first TOK_TRAIN_MB of the train
file; 113 number tokens <n0>..<n112> and the operator tokens <plus>, <eq> are special tokens that occur ONLY in arithmetic
sentences (digits in the stories stay ordinary BPE tokens, so the number tokens carry no text statistics).
Arithmetic: the facts of one split file (flat indices a*113 + b, as in all lab splits), c = (a + b) mod 113. Every fact
occurs equally often: a fixed cycle, reshuffled per round (no weighted redraw). Templates (chosen uniformly per sentence):
  T0 "<na> <plus> <nb> <eq> <nc>"   T1 "<na> plus <nb> is <nc>"   T2 "the sum of <na> and <nb> is <nc>"
Each training sequence (CTX + 1 tokens) = one arithmetic block of ARITH_FACTS sentences (joined by "\n", framed by the
end-of-text token) inserted at a random offset into the next text tokens; the arithmetic token share is logged.
Streams (numpy SeedSequence [105, seed, k]): k=1 text/insert offsets, k=2 fact order, k=3 templates, k=4 init
(torch.manual_seed from it). Arms F and G of one seed therefore share init, text and positions; only the facts differ.
Model: decoder-only pre-LN transformer, tied embeddings, learned positions; defaults 6 layers, d 384, 6 heads, ctx 256
(~13.8 M parameters; vocab 8192 including the specials). AdamW (betas 0.9/0.95), linear warmup then constant lr, wd on matrices only.
Loss: next-token cross-entropy on every position (a real LM; stage 1 showed that the loss on the b position delays
grokking by > x10, EXP-102).
Measures (every EVAL_EVERY steps): W_E rows of the 113 number tokens (snapshot), accuracy on held-out facts (complement
of the split or --test-file; prompt T0 without the answer, argmax over the 113 number tokens), accuracy on 2000 train
facts, text loss on a fixed validation batch.
Checkpoints (rule 20g): model, AdamW state, torch/cuda RNG, stream cursors and numpy generator states, step, config hash;
every CKPT_EVERY steps and at the end (atomic). A run resumes only with the same config hash.

  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-105-lm-ladder-stage2/lm_stage2.py --prepare
  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-105-lm-ladder-stage2/lm_stage2.py --selftest --device cuda
  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-105-lm-ladder-stage2/lm_stage2.py \
      --seed S --split-file <split.npy> [--test-file <test.npy>] --steps N --device cuda --out-root <dir>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "lab/external/tinystories"
TRAIN_TXT, VALID_TXT = DATA / "TinyStoriesV2-GPT4-train.txt", DATA / "TinyStoriesV2-GPT4-valid.txt"
TOK_FILE, TEXT_NPY, VALID_NPY = DATA / "bpe8192.json", DATA / "text_u16.npy", DATA / "valid_u16.npy"
P, VOCAB_BPE, TOK_TRAIN_MB, TEXT_MB = 113, 8192, 100, 450
EOT = "<|endoftext|>"
NUM = [f"<n{i}>" for i in range(P)]
SPECIAL = [EOT] + NUM + ["<plus>", "<eq>"]
TEMPLATES = ("{a} <plus> {b} <eq> {c}", "{a} plus {b} is {c}", "the sum of {a} and {b} is {c}")
EVAL_EVERY, CKPT_EVERY, ARITH_FACTS = 250, 1000, 2


# ----------------------------------------------------------------------------------------------------------------- data
def prepare() -> None:
    """Train the BPE and tokenize TEXT_MB of the train file and the whole validation file (never overwrites)."""
    from tokenizers import Tokenizer, decoders, models, pre_tokenizers, trainers
    if TOK_FILE.exists():
        print(f"{TOK_FILE.name} exists, kept")
        tok = Tokenizer.from_file(str(TOK_FILE))
    else:
        tok = Tokenizer(models.BPE())
        tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
        tok.decoder = decoders.ByteLevel()
        tr = trainers.BpeTrainer(vocab_size=VOCAB_BPE, special_tokens=SPECIAL, initial_alphabet=pre_tokenizers.ByteLevel.alphabet())
        with open(TRAIN_TXT, encoding="utf-8") as f:
            head = f.read(TOK_TRAIN_MB * 2**20)
        tok.train_from_iterator((d for d in head.split(EOT)), tr)
        tok.save(str(TOK_FILE))
    ids = special_ids(tok)
    for src, dst, mb in ((TRAIN_TXT, TEXT_NPY, TEXT_MB), (VALID_TXT, VALID_NPY, None)):
        if dst.exists():
            print(f"{dst.name} exists, kept")
            continue
        with open(src, encoding="utf-8") as f:
            txt = f.read(mb * 2**20) if mb else f.read()
        docs = [d.strip() for d in txt.split(EOT)][:-1 if mb else None]          # last doc of a cut file is partial
        out = []                                                         # uint16 chunks (a Python int list would need GBs)
        for i in range(0, len(docs), 10000):
            enc = tok.encode_batch(docs[i:i + 10000])
            out.append(np.concatenate([np.asarray(e.ids + [ids["eot"]], dtype=np.uint16) for e in enc]))
        arr = np.concatenate(out)
        assert not np.isin(arr, ids["num"] + [ids["plus"], ids["eq"]]).any(), "number/operator token inside the text"
        with open(dst, "xb") as f:
            np.save(f, arr)
        print(f"{dst.name}: {len(arr)} tokens from {len(docs)} stories")


def special_ids(tok) -> dict:
    g = tok.token_to_id
    return {"eot": g(EOT), "num": [g(t) for t in NUM], "plus": g("<plus>"), "eq": g("<eq>")}


class Stream:
    """Deterministic training batches: text + one arithmetic block per sequence; state is a small dict (checkpointable)."""

    def __init__(self, text: np.ndarray, facts: np.ndarray, tmpl_ids: list[list[list[int]]], nl: int, eot: int, seed: int, ctx: int):
        self.text, self.facts, self.tmpl, self.nl, self.eot, self.ctx = text, facts, tmpl_ids, nl, eot, ctx
        self.g_text, self.g_fact, self.g_tmpl = (np.random.default_rng(np.random.SeedSequence([105, seed, k])) for k in (1, 2, 3))
        self.text_pos, self.fact_pos, self.order, self.rounds = 0, 0, self.g_fact.permutation(len(facts)), 0
        self.n_tok, self.n_arith, self.wraps = 0, 0, 0

    def next_fact(self) -> int:
        if self.fact_pos == len(self.order):
            self.order, self.fact_pos, self.rounds = self.g_fact.permutation(len(self.facts)), 0, self.rounds + 1
        f = int(self.facts[self.order[self.fact_pos]])
        self.fact_pos += 1
        return f

    def sequence(self) -> np.ndarray:
        block = [self.eot]
        for i in range(ARITH_FACTS):
            f = self.next_fact()
            a, b = divmod(f, P)
            parts = self.tmpl[int(self.g_tmpl.integers(len(self.tmpl)))]
            block += (parts[0] + [NUM_ID[a]] + parts[1] + [NUM_ID[b]] + parts[2] + [NUM_ID[(a + b) % P]] + parts[3])
            block.append(self.nl if i < ARITH_FACTS - 1 else self.eot)
        n_text = self.ctx + 1 - len(block)
        if self.text_pos + n_text > len(self.text):
            self.text_pos, self.wraps = 0, self.wraps + 1                # budget should avoid it
        t = self.text[self.text_pos:self.text_pos + n_text].astype(np.int64)
        self.text_pos += n_text
        cut = int(self.g_text.integers(n_text + 1))
        seq = np.concatenate([t[:cut], np.asarray(block, np.int64), t[cut:]])
        self.n_tok += len(seq)
        self.n_arith += len(block)
        return seq

    def batch(self, bs: int) -> np.ndarray:
        return np.stack([self.sequence() for _ in range(bs)])

    def state(self) -> dict:
        return {"text_pos": self.text_pos, "fact_pos": self.fact_pos, "order": self.order.tolist(), "rounds": self.rounds,
                "n_tok": self.n_tok, "n_arith": self.n_arith, "wraps": self.wraps,
                "g": [g.bit_generator.state for g in (self.g_text, self.g_fact, self.g_tmpl)]}

    def load(self, s: dict) -> None:
        self.text_pos, self.fact_pos, self.order, self.rounds = s["text_pos"], s["fact_pos"], np.asarray(s["order"]), s["rounds"]
        self.n_tok, self.n_arith, self.wraps = s["n_tok"], s["n_arith"], s["wraps"]
        for g, st in zip((self.g_text, self.g_fact, self.g_tmpl), s["g"]):
            g.bit_generator.state = st


NUM_ID: list[int] = []


def template_parts(tok) -> list[list[list[int]]]:
    """Token ids of the fixed pieces around a, b, c for every template (encoded with the same BPE as the text)."""
    out = []
    for t in TEMPLATES:
        pieces = t.replace("{a}", "\x00").replace("{b}", "\x00").replace("{c}", "\x00").split("\x00")
        out.append([tok.encode(p).ids if p else [] for p in pieces])
    return out


# ---------------------------------------------------------------------------------------------------------------- model
class Block(nn.Module):
    def __init__(self, d: int, h: int):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.qkv, self.proj = nn.Linear(d, 3 * d), nn.Linear(d, d)
        self.fc, self.out = nn.Linear(d, 4 * d), nn.Linear(4 * d, d)
        self.h = h

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, D = x.shape
        q, k, v = self.qkv(self.ln1(x)).view(B, T, 3, self.h, D // self.h).permute(2, 0, 3, 1, 4)
        z = F.scaled_dot_product_attention(q, k, v, is_causal=True).transpose(1, 2).reshape(B, T, D)
        x = x + self.proj(z)
        return x + self.out(F.gelu(self.fc(self.ln2(x))))


class GPT(nn.Module):
    def __init__(self, vocab: int, ctx: int, d: int, layers: int, heads: int):
        super().__init__()
        self.emb, self.pos = nn.Embedding(vocab, d), nn.Embedding(ctx, d)
        self.blocks = nn.ModuleList(Block(d, heads) for _ in range(layers))
        self.ln = nn.LayerNorm(d)
        for m in self.modules():
            if isinstance(m, (nn.Linear, nn.Embedding)):
                nn.init.normal_(m.weight, std=0.02)
                if isinstance(m, nn.Linear):
                    nn.init.zeros_(m.bias)
        for b in self.blocks:                                            # GPT-2 residual scaling
            nn.init.normal_(b.proj.weight, std=0.02 / math.sqrt(2 * layers))
            nn.init.normal_(b.out.weight, std=0.02 / math.sqrt(2 * layers))

    def forward(self, idx: torch.Tensor) -> torch.Tensor:
        x = self.emb(idx) + self.pos(torch.arange(idx.shape[1], device=idx.device))
        for b in self.blocks:
            x = b(x)
        return self.ln(x) @ self.emb.weight.T                             # tied output layer


# ---------------------------------------------------------------------------------------------------------------- train
def save_atomic(path: Path, obj, kind: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    if kind == "torch":
        torch.save(obj, tmp)
    elif kind == "npy":
        with open(tmp, "wb") as f:
            np.save(f, obj)
    else:
        tmp.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    os.replace(tmp, path)


def run(a: argparse.Namespace) -> dict:
    global NUM_ID
    from tokenizers import Tokenizer
    tok = Tokenizer.from_file(str(TOK_FILE))
    ids = special_ids(tok)
    NUM_ID = ids["num"]
    vocab = tok.get_vocab_size()
    text = np.load(TEXT_NPY, mmap_mode="r")
    valid = np.load(VALID_NPY, mmap_mode="r")
    split = Path(a.split_file)
    facts = np.load(split).astype(np.int64)
    assert facts.ndim == 1 and len(np.unique(facts)) == len(facts) and facts.min() >= 0 and facts.max() < P * P, split
    test = np.load(a.test_file).astype(np.int64) if a.test_file else np.setdiff1d(np.arange(P * P), facts)
    assert not np.intersect1d(test, facts).size, "test facts overlap the training facts"
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()   # noqa: E731
    cfg = {"seed": a.seed, "split_sha256": sha(split), "test_sha256": sha(a.test_file) if a.test_file else "complement",
           "steps": a.steps, "batch": a.batch, "ctx": a.ctx, "d": a.d, "layers": a.layers, "heads": a.heads, "lr": a.lr,
           "warmup": a.warmup, "wd": a.wd, "arith_facts": ARITH_FACTS, "templates": TEMPLATES, "tokenizer_sha256": sha(TOK_FILE),
           "text_tokens": int(len(text)), "script_sha256": sha(__file__), "device": a.device}
    chash = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:16]
    run_id = f"lm2_seed{a.seed}_{split.stem}_steps{a.steps}_{chash}"
    out = Path(a.out_root) / run_id
    out.mkdir(parents=True, exist_ok=True)
    if (out / "result.json").exists() and json.loads((out / "result.json").read_text(encoding="utf-8")).get("status") == "completed":
        print(f"skip {run_id} (completed)")
        return json.loads((out / "result.json").read_text(encoding="utf-8"))
    dev = torch.device(a.device)
    g_init = np.random.default_rng(np.random.SeedSequence([105, a.seed, 4]))
    torch.manual_seed(int(g_init.integers(2**62)))
    model = GPT(vocab, a.ctx, a.d, a.layers, a.heads).to(dev)
    decay = [p for n, p in model.named_parameters() if p.dim() >= 2]
    no_decay = [p for n, p in model.named_parameters() if p.dim() < 2]
    opt = torch.optim.AdamW([{"params": decay, "weight_decay": a.wd}, {"params": no_decay, "weight_decay": 0.0}],
                            lr=a.lr, betas=(0.9, 0.95))
    stream = Stream(text, facts, template_parts(tok), tok.token_to_id("Ċ"), ids["eot"], a.seed, a.ctx)
    num = torch.tensor(NUM_ID, device=dev)
    rng_eval = np.random.default_rng(np.random.SeedSequence([105, a.seed, 5]))
    tr_eval = facts[rng_eval.choice(len(facts), min(2000, len(facts)), replace=False)]
    vstart = np.random.default_rng(np.random.SeedSequence([105, a.seed, 6])).integers(0, len(valid) - a.ctx - 1, 16)
    vbatch = torch.from_numpy(np.stack([valid[s:s + a.ctx + 1].astype(np.int64) for s in vstart])).to(dev)
    t0p = tmpl_prompt(template_parts(tok)[0])

    def prompts(f: np.ndarray) -> torch.Tensor:
        aa, bb = f // P, f % P
        return torch.tensor([[ids["eot"]] + t0p[0] + [NUM_ID[x]] + t0p[1] + [NUM_ID[y]] + t0p[2] for x, y in zip(aa, bb)], device=dev)

    te_x, te_c = prompts(test), torch.from_numpy((test // P + test % P) % P).to(dev)
    tr_x, tr_c = prompts(tr_eval), torch.from_numpy((tr_eval // P + tr_eval % P) % P).to(dev)

    @torch.no_grad()
    def evaluate(step: int) -> list:
        model.eval()
        acc = lambda x, c: float(sum((model(x[i:i + 1024])[:, -1, num].argmax(1) == c[i:i + 1024]).sum().item()   # noqa: E731
                                     for i in range(0, len(x), 1024)) / len(x))
        vl = F.cross_entropy(model(vbatch[:, :-1]).flatten(0, 1), vbatch[:, 1:].flatten()).item()
        row = [step, acc(tr_x, tr_c), acc(te_x, te_c), vl]
        model.train()
        return row

    step, curve, snaps, snap_steps, events = 0, [], [], [], {}
    ck = out / "checkpoint.pt"
    if ck.exists():
        s = torch.load(ck, map_location=dev, weights_only=False)
        assert s["config_hash"] == chash, "checkpoint from another configuration"
        model.load_state_dict(s["model"])
        opt.load_state_dict(s["opt"])
        torch.set_rng_state(s["torch_rng"])
        if dev.type == "cuda" and s.get("cuda_rng") is not None:
            torch.cuda.set_rng_state(s["cuda_rng"], dev)
        stream.load(s["stream"])
        step, curve, snaps, snap_steps, events = s["step"], s["curve"], list(s["snaps"]), s["snap_steps"], s["events"]
        print(f"resume {run_id} at step {step}")
    lock = out / "run.lock"
    if lock.exists():
        old = lock.read_text(encoding="utf-8").strip()
        if old.isdigit() and pid_alive(int(old)):
            raise SystemExit(f"{run_id}: {lock} held by live process {old}")
        print(f"stale lock {lock} (pid {old} not alive), taking over")
    lock.write_text(str(os.getpid()), encoding="utf-8")
    t_start = time.perf_counter()

    def checkpoint() -> None:
        save_atomic(ck, {"config_hash": chash, "model": model.state_dict(), "opt": opt.state_dict(),
                         "torch_rng": torch.get_rng_state(), "cuda_rng": torch.cuda.get_rng_state(dev) if dev.type == "cuda" else None,
                         "stream": stream.state(), "step": step, "curve": curve, "snaps": snaps, "snap_steps": snap_steps,
                         "events": events}, "torch")

    if step == 0:
        snaps.append(model.emb.weight[num].detach().float().cpu().numpy())
        snap_steps.append(0)
        curve.append(evaluate(0))
    status = "completed"
    while step < a.steps:
        step += 1
        for gr in opt.param_groups:
            gr["lr"] = a.lr * min(1.0, step / a.warmup)
        xb = torch.from_numpy(stream.batch(a.batch)).to(dev)
        loss = F.cross_entropy(model(xb[:, :-1]).flatten(0, 1), xb[:, 1:].flatten())
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        if step % EVAL_EVERY == 0 or step == a.steps:
            if not torch.isfinite(loss):
                events["nonfinite_step"], status = step, "error"
                break
            curve.append(evaluate(step) + [loss.item()])
            snaps.append(model.emb.weight[num].detach().float().cpu().numpy())
            snap_steps.append(step)
            if "generalization_step" not in events and curve[-1][2] >= 0.95:
                events["generalization_step"] = step
            print(f"step {step} loss {loss.item():.3f} train {curve[-1][1]:.3f} test {curve[-1][2]:.3f} "
                  f"val {curve[-1][3]:.3f} arith share {stream.n_arith / max(1, stream.n_tok):.3f}", flush=True)
        if step % CKPT_EVERY == 0 and step < a.steps:
            checkpoint()
    save_atomic(out / "we_snapshots.npy", np.asarray(snaps, np.float32), "npy")
    save_atomic(out / "we_snapshot_steps.npy", np.asarray(snap_steps), "npy")
    res = {"status": status, "run_id": run_id, "config": cfg, "config_hash": chash, "steps_completed": step, "events": events,
           "curve_cols": ["step", "train_fact_acc", "test_fact_acc", "val_text_loss", "train_loss"], "curve": curve,
           "arith_token_share": stream.n_arith / max(1, stream.n_tok), "fact_rounds": stream.rounds,
           "text_wraps": stream.wraps, "n_params": sum(p.numel() for p in model.parameters()),
           "elapsed_s_this_segment": time.perf_counter() - t_start, "torch": torch.__version__}
    save_atomic(out / "result.json", res, "json")
    checkpoint() if status == "completed" else None
    lock.unlink(missing_ok=True)
    print(f"{run_id}: {status}, test {curve[-1][2]:.3f}, gen {events.get('generalization_step')}")
    return res


def pid_alive(pid: int) -> bool:
    """True if a process with this PID is running (Windows: OpenProcess + GetExitCodeProcess; never signals it)."""
    if os.name != "nt":
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    import ctypes
    k32 = ctypes.windll.kernel32
    h = k32.OpenProcess(0x1000, False, pid)                           # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return False
    code = ctypes.c_ulong()
    ok = k32.GetExitCodeProcess(h, ctypes.byref(code))
    k32.CloseHandle(h)
    return bool(ok) and code.value == 259                              # STILL_ACTIVE


def tmpl_prompt(parts: list[list[int]]) -> list[list[int]]:
    """Template T0 up to the answer: [before a], [between a and b], [between b and c]."""
    return parts[:3]


# -------------------------------------------------------------------------------------------------------------- selftest
def selftest(device: str) -> None:
    """Tiny model: (1) 40 steps straight == 20 steps, checkpoint, resume 20 steps (bit-identical weights);
    (2) stream: every fact once per round, share of arithmetic tokens > 0, no number tokens in the text."""
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="lm2_selftest_"))
    split = tmp / "split.npy"
    np.save(split, np.sort(np.random.default_rng(0).choice(P * P, 300, replace=False)).astype(np.int64))
    base = dict(seed=1, split_file=str(split), test_file=None, batch=4, ctx=64, d=32, layers=2, heads=2, lr=1e-3,
                warmup=5, wd=0.1, device=device)
    global CKPT_EVERY, EVAL_EVERY
    CKPT_EVERY, EVAL_EVERY = 20, 10
    r1 = run(argparse.Namespace(**base, steps=40, out_root=str(tmp / "a")))
    d2 = tmp / "b"
    ns = argparse.Namespace(**base, steps=40, out_root=str(d2))
    # simulate an interruption after the checkpoint at step 20: run 40 steps with a hook that stops at 25
    orig = Stream.batch
    calls = {"n": 0}

    def stopping(self, bs):
        calls["n"] += 1
        if calls["n"] == 26:
            raise KeyboardInterrupt
        return orig(self, bs)
    Stream.batch = stopping
    try:
        run(ns)
    except KeyboardInterrupt:
        pass
    Stream.batch = orig
    rd = next(d2.iterdir())
    (rd / "run.lock").unlink(missing_ok=True)
    r2 = run(ns)
    w1 = torch.load(next((tmp / "a").iterdir()) / "checkpoint.pt", weights_only=False)["model"]
    w2 = torch.load(rd / "checkpoint.pt", weights_only=False)["model"]
    same = all(torch.equal(w1[k], w2[k]) for k in w1)
    print(f"resume bit-identical: {same}; curves equal: {r1['curve'] == r2['curve']}; arith share {r1['arith_token_share']:.3f}")
    assert same and r1["curve"] == r2["curve"]
    assert pid_alive(os.getpid()) and not pid_alive(4_000_000_000 // 4 * 4 - 4), "pid_alive check"   # a PID that cannot exist
    shutil.rmtree(tmp)
    print("selftest ok")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--split-file")
    ap.add_argument("--test-file")
    ap.add_argument("--steps", type=int, default=10000)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--ctx", type=int, default=256)
    ap.add_argument("--d", type=int, default=384)
    ap.add_argument("--layers", type=int, default=6)
    ap.add_argument("--heads", type=int, default=6)
    ap.add_argument("--lr", type=float, default=6e-4)
    ap.add_argument("--warmup", type=int, default=500)
    ap.add_argument("--wd", type=float, default=0.1)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--out-root", default=str(HERE / "raw"))
    a = ap.parse_args()
    if a.prepare:
        prepare()
    elif a.selftest:
        selftest(a.device)
    else:
        if a.seed is None or not a.split_file:
            raise SystemExit("--seed and --split-file are required")
        run(a)


if __name__ == "__main__":
    main()
