"""EXP-051 (P2, programme A): are the steered target frequencies functionally used? UNTESTED (written out of window).

No training: loads the saved EXP-047 models (freq_ban.py --save-model, add mod 113, transformer, 2000 steps, seeds 150-159,
kinds eng/shuf, arms F/G) and ablates frequencies in the input embedding W_E[:113] at evaluation time.
Per model: base accuracy on the COMMON test set (pairs in neither the F nor the G train split of that seed/kind), then two
ablations that remove the SAME, always feasible W_E energy X = 0.5 * min(E_own, E_ctrl) (Nachtrag a, review s13: the 5 targets
hold 76-89 % of the W_E energy in EXP-016, so 'remove as much elsewhere as the targets hold' is impossible):
  own : scale the own 5 target frequencies by c_own so that X is removed
  ctrl: scale the control frequencies by c_ctrl so that X is removed; control = all k except own targets, the other arm's
        targets and the harmonics fold(2t) of the own targets (the model uses them because of the targets)
Secondary: full removal of the own / the other arm's targets (drop_own_full, drop_other_full).
drop_x = base_acc - acc_after_x.  Primary (eng): D_i = mean over the seed's two models of [drop_own - drop_ctrl] > 0.
Validity: both eng models of a seed load and their base common-test accuracy >= 0.9.
Definition and reading: README.md.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E47 = ROOT / "lab/experiments/EXP-047-marginal-control"
sys.path.insert(0, str(ROOT / "training"))
sys.path.insert(0, str(ROOT / "lab/tools"))
from result_loader import Expect, find_run, load_run  # noqa: E402

P, K, SEEDS, STEP, ACC_MIN, ALPHA, MIN_VALID = 113, 56, range(150, 160), 2000, 0.9, 0.05, 8


def basis() -> np.ndarray:
    """Orthonormal real DFT basis over Z_p, columns [const, cos_1, sin_1, ..., cos_K, sin_K] (as freq_ban.fourier_basis)."""
    a = np.arange(P)
    cols = [np.ones(P) / np.sqrt(P)]
    for k in range(1, K + 1):
        cols += [np.cos(2 * np.pi * k * a / P) * np.sqrt(2 / P), np.sin(2 * np.pi * k * a / P) * np.sqrt(2 / P)]
    return np.stack(cols, 1)


def cols(freqs) -> list[int]:
    return [c for k in freqs for c in (2 * k - 1, 2 * k)]


def energy(W: np.ndarray, B: np.ndarray, freqs) -> float:
    C = B.T @ W
    return float((C[cols(freqs)] ** 2).sum())


def remove(W: np.ndarray, B: np.ndarray, freqs) -> np.ndarray:
    C = B.T @ W
    C[cols(freqs)] = 0.0
    return B @ C


def remove_energy(W: np.ndarray, B: np.ndarray, freqs, amount: float) -> np.ndarray:
    """Scale the given frequencies by one factor c so that exactly `amount` energy is removed (amount <= their energy)."""
    C = B.T @ W
    e = float((C[cols(freqs)] ** 2).sum())
    if amount > e + 1e-12:
        raise ValueError("amount exceeds the available energy")
    C[cols(freqs)] *= np.sqrt(max(0.0, 1.0 - amount / e)) if e > 0 else 0.0
    return B @ C


def fold(x: int) -> int:
    x %= P
    return min(x, P - x)


def control_set(own, other) -> list[int]:
    excl = set(own) | set(other) | {fold(2 * t) for t in own}
    return [k for k in range(1, K + 1) if k not in excl]


def load_model(d: Path):
    import torch
    torch.set_num_threads(4)                   # rule 17 thread budget (review s13)
    from grokverse.config import get_config
    from grokverse.models import build_model
    cfg = get_config("arch25k", seed=0, steps=STEP, threads=1)
    model = build_model(cfg)
    model.load_state_dict(torch.load(d / "model_final.pt", map_location="cpu"))
    model.eval()
    return model


def accuracy(model, W_E_rows: np.ndarray | None, idx: np.ndarray) -> float:
    import torch
    with torch.no_grad():
        saved = model.W_E.data.clone()
        if W_E_rows is not None:
            model.W_E.data[:P] = torch.from_numpy(W_E_rows).to(model.W_E.dtype)
        a, b = idx // P, idx % P
        x = torch.from_numpy(np.stack([a, b, np.full(len(idx), P)], 1)).long()
        pred = model.logits_last(x)[:, :P].argmax(-1).numpy()
        model.W_E.data.copy_(saved)
    return float((pred == (a + b) % P).mean())


def seed_row(s: int, kind: str, B: np.ndarray) -> dict:
    r: dict = {"seed": s, "kind": kind, "valid": False}
    meta = json.loads((E47 / f"splits/split_add113_seed{s}_{kind}_F.json").read_text(encoding="utf-8"))
    T = {"F": meta["targets"], "G": json.loads((E47 / f"splits/split_add113_seed{s}_{kind}_G.json").read_text(encoding="utf-8"))["targets"]}
    trains = [np.load(E47 / f"splits/split_add113_seed{s}_{kind}_{a}.npy") for a in "FG"]
    common = np.setdiff1d(np.arange(P * P), np.union1d(*trains))
    arms = {}
    for arm, other in (("F", "G"), ("G", "F")):
        stem = f"split_add113_seed{s}_{kind}_{arm}"
        L = load_run(find_run(E47 / "raw", f"*_seed{s}_thr*_{stem}_devcuda"),
                     Expect(seed=s, device="cuda", max_steps=STEP, split_file=E47 / f"splits/{stem}.npy",
                            config={"p": P, "task": "add"}, files=("model_final.pt",)))
        if L.status != "ok":
            r["reason"] = f"{arm}: {L.status}: {L.reason}"
            return r
        m = load_model(L.path)
        W = m.W_E.detach().numpy().astype(np.float64)[:P]
        base = accuracy(m, None, common)
        ctrl = control_set(T[arm], T[other])
        e_own, e_ctrl = energy(W, B, T[arm]), energy(W, B, ctrl)
        X = 0.5 * min(e_own, e_ctrl)
        arms[arm] = {"base_acc": base, "energy_own": e_own, "energy_ctrl": e_ctrl, "X": X,
                     "energy_harmonics": energy(W, B, sorted({fold(2 * t) for t in T[arm]} - set(T[arm]))),
                     "drop_own": base - accuracy(m, remove_energy(W, B, T[arm], X), common),
                     "drop_ctrl": base - accuracy(m, remove_energy(W, B, ctrl, X), common),
                     "drop_own_full": base - accuracy(m, remove(W, B, T[arm]), common),
                     "drop_other_full": base - accuracy(m, remove(W, B, T[other]), common)}
    r["arms"] = arms
    r["n_common_test"] = int(len(common))
    if not all(v["base_acc"] >= ACC_MIN for v in arms.values()):
        r["reason"] = "base accuracy < 0.9"
        return r
    r["valid"] = True
    r["D"] = float(np.mean([v["drop_own"] - v["drop_ctrl"] for v in arms.values()]))
    r["D_cross"] = float(np.mean([v["drop_own_full"] - v["drop_other_full"] for v in arms.values()]))
    return r


def one_sided_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def selftest() -> None:
    rng = np.random.default_rng(0)
    B = basis()
    assert np.allclose(B.T @ B, np.eye(P), atol=1e-10), "basis not orthonormal"
    W = rng.normal(size=(P, 16))
    T = [3, 17, 40]
    Wr = remove(W, B, T)
    assert energy(Wr, B, T) < 1e-20 and abs(energy(Wr, B, [5]) - energy(W, B, [5])) < 1e-9, "remove() is not a clean projection"
    ctrl = control_set(T, [8, 9])
    assert not ({fold(2 * t) for t in T} | set(T) | {8, 9}) & set(ctrl) and len(ctrl) > 40
    amount = 0.5 * min(energy(W, B, T), energy(W, B, ctrl))
    for S in (T, ctrl):
        We = remove_energy(W, B, S, amount)
        removed = ((B.T @ W) ** 2).sum() - ((B.T @ We) ** 2).sum()
        others = [k for k in range(1, K + 1) if k not in S]
        assert abs(removed - amount) < 1e-8 * amount and abs(energy(We, B, others) - energy(W, B, others)) < 1e-9
    try:
        remove_energy(W, B, T, 1e9)
        raise AssertionError("infeasible amount accepted")
    except ValueError:
        pass
    assert one_sided_p(np.ones(10)) == 1 / 1024
    print("[exp051] selftest ok", flush=True)


def main() -> None:
    if sys.argv[1:] == ["--selftest"]:
        selftest()
        return
    B = basis()
    out: dict = {}
    for kind in ("eng", "shuf"):
        rows = [seed_row(s, kind, B) for s in SEEDS]
        valid = [r for r in rows if r["valid"]]
        o: dict = {"rows": rows, "n_valid": len(valid)}
        if valid:
            D = np.array([r["D"] for r in valid])
            o.update({"D_mean": float(D.mean()), "p": one_sided_p(D) if len(D) >= 2 else None, "n_positive": int((D > 0).sum()),
                      "D_cross_mean": float(np.mean([r["D_cross"] for r in valid]))})
        out[kind] = o
    e = out["eng"]
    if e["n_valid"] < MIN_VALID:
        out["verdict"] = "nicht auswertbar"
    else:
        out["verdict"] = ("funktional genutzt" if e["D_mean"] > 0 and e["p"] < ALPHA else
                          "richtungsgleich, n. s." if e["D_mean"] > 0 else "nicht mehr genutzt als gleiche Energie anderswo")
    out["design"] = "Nachtrag a: equal feasible energy X = 0.5*min(E_own, E_ctrl); control excludes both target sets and fold(2t)"
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk != "rows"})
                      for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    main()
