"""EXP-066 (exploration): P2d measure (margin drop per equal parameter step, own targets vs equal-size controls) on the bound P1 models of
mul 113 and add 97. Definition: README.md (fixed before the computation). Run under guarded_run.py. CPU forward passes only.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
sys.path.insert(0, str(LAB.parent / "training"))
import confirm_p1 as c1  # noqa: E402
from make_split import group  # noqa: E402
from result_loader import Expect, find_run, load_run  # noqa: E402

TASKS, SEEDS, REL_DELTA, N_CTRL, ACC_MIN = (("mul", 113), ("add", 97)), range(1000, 1050), 0.02, 4, 0.9
MAN = json.loads((LAB / "confirm" / "P1_manifest.json").read_text(encoding="utf-8"))


def fold(x: int, n: int) -> int:
    x %= n
    return min(x, n - x)


def control_sets(own: list[int], other: list[int], n: int, key: list[int]) -> list[list[int]]:
    excl = set(own) | set(other) | {fold(2 * k, n) for k in own}
    pool = [k for k in range(1, (n - 1) // 2 + 1) if k not in excl]
    rng = np.random.default_rng(key)
    return [sorted(int(k) for k in rng.choice(pool, 5, replace=False)) for _ in range(N_CTRL)]


def proj(X: np.ndarray, S: list[int]) -> np.ndarray:
    """Projection of the group-ordered rows X [n, d] onto cos/sin of the frequencies S over Z_n."""
    n = X.shape[0]
    j = np.arange(n)
    B = np.stack([f(2 * np.pi * k * j / n) for k in S for f in (np.cos, np.sin)], 1)
    B /= np.linalg.norm(B, axis=0)
    return B @ (B.T @ X)


def load_model(task: str, p: int, data: bytes):
    import torch
    torch.set_num_threads(4)
    from grokverse.config import get_config
    from grokverse.models import build_model
    m = build_model(get_config("arch25k", seed=0, steps=c1.STEP, threads=1, p=p, task=task))
    m.load_state_dict(torch.load(io.BytesIO(data), map_location="cpu"))
    m.eval()
    return m


def evaluate(m, task: str, p: int, rows: np.ndarray | None, elem: np.ndarray, idx: np.ndarray) -> dict:
    import torch
    with torch.no_grad():
        saved = m.W_E.data.clone()
        if rows is not None:
            m.W_E.data[torch.from_numpy(elem).long()] = torch.from_numpy(rows).to(m.W_E.dtype)
        a, b = idx // p, idx % p
        x = torch.from_numpy(np.stack([a, b, np.full(len(idx), p)], 1)).long()
        lg = m.logits_last(x)[:, :p].double()
        y = torch.from_numpy((a + b) % p if task == "add" else (a * b) % p).long()
        acc = float((lg.argmax(-1) == y).double().mean())
        corr = lg.gather(1, y[:, None])[:, 0]
        wrong = lg.clone()
        wrong.scatter_(1, y[:, None], -float("inf"))
        margin = float((corr - wrong.max(1).values).mean())
        m.W_E.data.copy_(saved)
    return {"acc": acc, "margin": margin}


def arm_row(task: str, p: int, s: int, arm: str, T: dict, common: np.ndarray) -> dict | str:
    t = {"task": task, "p": p}
    st = c1.stem(MAN, t, s, arm)
    d = find_run(c1.RAW, f"EXP-0*_baseline_seed{s}_thr*_{st}_{task}{p}_devcuda")
    if d is None:
        return "fehlt"
    if (why := c1.unbound(MAN, d)):
        return f"defekt: {why}"
    L = load_run(d, Expect(seed=s, device="cuda", max_steps=c1.STEP, split_file=c1.SPLITS / f"{st}.npy",
                           config={"p": p, "task": task}, files=("model_final.pt",)))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    if (why := c1.post_load_check(MAN, d, L.res, c1.SPLITS / f"{st}.npy")):
        return why
    m = load_model(task, p, c1.bound_bytes(MAN, L.path / "model_final.pt"))
    n, elem = group(task, p)
    elem = np.arange(p) if elem is None else elem
    X = m.W_E.detach().numpy().astype(np.float64)[elem]
    other = "G" if arm == "F" else "F"
    sets = {"own": T[arm]} | {f"c{i}": c for i, c in enumerate(control_sets(T[arm], T[other], n, [66, ord(task[0]), p, s, ord(arm)]))}
    base = evaluate(m, task, p, None, elem, common)
    delta = REL_DELTA * float(np.linalg.norm(X))
    dr = {}
    for k, S in sets.items():
        PS = proj(X, S)
        dr[k] = base["margin"] - evaluate(m, task, p, X - delta * PS / np.linalg.norm(PS), elem, common)["margin"]
    return {"base": base, "drop_own": dr["own"], "drop_ctrl": [dr[f"c{i}"] for i in range(N_CTRL)]}


def task_rows(task: str, p: int) -> list[dict]:
    rows = []
    for s in SEEDS:
        T = {a: json.loads((c1.SPLITS / f"{c1.stem(MAN, {'task': task, 'p': p}, s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
        trains = [np.load(c1.SPLITS / f"{c1.stem(MAN, {'task': task, 'p': p}, s, a)}.npy") for a in "FG"]
        common = np.setdiff1d(np.arange(p * p), np.union1d(*trains))
        arms = {a: arm_row(task, p, s, a, T, common) for a in "FG"}
        bad = [f"{a}: {v}" for a, v in arms.items() if isinstance(v, str)]
        if bad:
            rows.append({"seed": s, "valid": False, "technical": True, "reason": "; ".join(bad)})
            continue
        D = float(np.mean([v["drop_own"] - np.mean(v["drop_ctrl"]) for v in arms.values()]))
        ok = all(v["base"]["acc"] >= ACC_MIN for v in arms.values())
        rows.append({"seed": s, "valid": ok, "technical": False, "D": D, "arms": arms})
    return rows


def summary(rows: list[dict]) -> dict:
    D = np.array([r["D"] for r in rows if r["valid"]])
    Dall = np.array([r["D"] for r in rows if not r["technical"]])
    rng = np.random.default_rng(66)
    out = {"n_valid": int(len(D)), "n_technical": sum(r["technical"] for r in rows), "n_nontechnical": int(len(Dall))}
    if len(D) >= 3:
        out |= {"mean": float(D.mean()), "sd": float(D.std(ddof=1)), "ci95": c1.boot_ci(D, rng), "n_positive": int((D > 0).sum()),
                "min": float(D.min())}
        own = [v["drop_own"] for r in rows if r["valid"] for v in r["arms"].values()]
        ctl = [np.mean(v["drop_ctrl"]) for r in rows if r["valid"] for v in r["arms"].values()]
        out |= {"median_drop_own": float(np.median(own)), "median_drop_ctrl": float(np.median(ctl))}
    if len(Dall):
        out |= {"all_mean": float(Dall.mean()), "all_n_positive": int((Dall > 0).sum())}
    return out


def selftest() -> None:
    n = 112
    X = np.random.default_rng(0).standard_normal((n, 8))
    P1 = proj(X, [3, 7])
    assert np.allclose(proj(P1, [3, 7]), P1) and np.allclose(proj(X - P1, [3, 7]), 0, atol=1e-10)
    assert np.allclose(proj(X, [3]) + proj(X, [7]), P1)
    cs = control_sets([1, 2, 3, 4, 5], [6, 7, 8, 9, 10], 97, [66, 1])
    assert all(len(c) == 5 and not set(c) & set(range(1, 11)) and 2 * 5 % 97 not in c for c in cs)
    print("[exp066] selftest ok", flush=True)


def main() -> None:
    selftest()
    out = {}
    for task, p in TASKS:
        rows = task_rows(task, p)
        out[f"{task}{p}"] = {**summary(rows), "rows": rows}
        print(f"{task}{p}", json.dumps(summary(rows)), flush=True)
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
