"""EXP-132 (session 61, N60): fine-tune Pythia-160M on MULTIPLICATION mod 113 with P1 mul splits (targets in discrete-log
coordinates). Does the fact selection steer the number embedding where the pretrained decimal features do not fit?

Wrapper around EXP-127's ft_pythia.py (imported unchanged): the task-specific pieces are replaced before ft.main() runs:
  - Stream.batch / prompts: answer c = a * b mod 113 (same token layout " a @ b = c\\n", same loss on the answer only);
  - power(): power per frequency k = 1..55 of the number rows in discrete-log order (elem[i] = 3^i mod 113, EXP-043
    make_split.group; the basis P1 used), row of 0 excluded;
  - projector(S): projection onto cos/sin(2 pi k i / 112) placed on the rows elem[i] (row 0 untouched); all-zero columns
    (sin at the Nyquist frequency 56) are dropped before the QR.
Run ids: ft_pythia's config does not know the task -> always use --out-root lab/experiments/EXP-132-pythia-mul/raw;
a sidecar task_meta_<hash>.json records task and wrapper hash.
Written in session 61 before any EXP-132 run; UNTESTED until --selftest-mul and a smoke run have passed.

  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-132-pythia-mul/ft_mul.py --selftest-mul
  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-132-pythia-mul/ft_mul.py \\
      --seed S --split-file <F|G.npy> --test-file <test.npy> --targets-file <seedS.json> --steps N --out-root <dir>
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-127-pretrained-lm"))
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
import ft_pythia as ft  # noqa: E402
from make_split import group  # noqa: E402

P = ft.P
N, ELEM = group("mul", P)                      # N = 112, ELEM[i] = 3^i mod 113
K = (N - 1) // 2                               # 55 frequencies (+ Nyquist 56, not used as a target)


def power_mul(W: np.ndarray) -> np.ndarray:
    X = W[ELEM].astype(np.float64)
    sq = (np.abs(np.fft.fft(X, axis=0)) ** 2).sum(1)
    return 2.0 * sq[1:K + 1] / N


def projector_mul(S: list[int]) -> torch.Tensor:
    i = np.arange(N)
    cols = []
    for k in S:
        for f in (np.cos, np.sin):
            c = np.zeros(P)
            c[ELEM] = f(2 * np.pi * k * i / N)
            if np.abs(c).max() > 1e-9:
                cols.append(c)
    Q, _ = np.linalg.qr(np.stack(cols, 1))
    return torch.tensor(Q @ Q.T, dtype=torch.float32)


def batch_mul(self, bs: int) -> tuple[torch.Tensor, torch.Tensor]:
    L = 1 + 6 * self.k
    x = np.empty((bs, L), np.int64)
    y = np.full((bs, L), -100, np.int64)
    num, op, eq, nl = self.ids["num"], self.ids["op"], self.ids["eq"], self.ids["nl"]
    for r in range(bs):
        row = [self.ids["eot"]]
        for _ in range(self.k):
            a, b = divmod(self.next_fact(), P)
            c = (a * b) % P
            y[r, len(row) + 3] = num[c]
            row += [num[a], op, num[b], eq, num[c], nl]
        x[r] = row
    return torch.from_numpy(x), torch.from_numpy(y)


def prompts_mul(pairs: np.ndarray, ids: dict) -> tuple[torch.Tensor, torch.Tensor]:
    a, b = pairs // P, pairs % P
    num = ids["num"]
    x = torch.tensor([[ids["eot"], num[i], ids["op"], num[j], ids["eq"]] for i, j in zip(a, b)])
    return x, torch.from_numpy((a * b) % P)


def patch() -> None:
    ft.power, ft.projector, ft.prompts = power_mul, projector_mul, prompts_mul
    ft.Stream.batch = batch_mul


def selftest_mul() -> None:
    """No model: labels, projector, power in the log basis."""
    patch()
    ids = {"num": list(range(1000, 1113)), "op": 1, "eq": 2, "nl": 3, "eot": 0}
    s = ft.Stream(np.array([5 * P + 7, 112 * P + 112, 0 * P + 9]), ids, 0, 3)
    x, y = s.batch(2)
    for r in range(2):
        for p_ in (y[r] != -100).nonzero().flatten().tolist():
            a_, b_, c_ = (int(x[r, p_ + d]) - 1000 for d in (-3, -1, 1))
            assert c_ == (a_ * b_) % P and int(y[r, p_]) == int(x[r, p_ + 1]), (a_, b_, c_)
    xt, ct = ft.prompts(np.array([5 * P + 7, 112 * P + 112]), ids)
    assert ct.tolist() == [35, 1]
    Pm = ft.projector([3, 7])
    assert torch.allclose(Pm @ Pm, Pm, atol=1e-5) and abs(float(torch.trace(Pm)) - 4) < 1e-4
    assert float(Pm[0].abs().max()) < 1e-6                      # row of the number 0 untouched
    Pn = ft.projector([56])
    assert abs(float(torch.trace(Pn)) - 1) < 1e-4               # Nyquist: cosine only
    i = np.arange(N)
    W = np.zeros((P, 4))
    W[ELEM, 0], W[ELEM, 1] = np.cos(2 * np.pi * 9 * i / N), np.sin(2 * np.pi * 30 * i / N)
    pw = ft.power(W)
    assert len(pw) == 55 and set(np.argsort(pw)[-2:] + 1) == {9, 30}
    print("selftest-mul ok")


def main() -> None:
    if "--selftest-mul" in sys.argv:
        selftest_mul()
        return
    patch()
    args = sys.argv[1:]
    if "--out-root" in args:
        root = Path(args[args.index("--out-root") + 1])
        root.mkdir(parents=True, exist_ok=True)
        meta = {"task": "mul", "wrapper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "ft_pythia_sha256": ft.sha(ft.__file__), "argv": args}
        (root / f"task_meta_{hashlib.sha256(json.dumps(args).encode()).hexdigest()[:12]}.json").write_text(
            json.dumps(meta, indent=1), encoding="utf-8")
    ft.main()


if __name__ == "__main__":
    main()
