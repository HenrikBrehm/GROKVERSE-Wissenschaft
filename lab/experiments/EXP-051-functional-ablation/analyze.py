"""EXP-051 (P2, programme A): are the steered target frequencies functionally used? UNTESTED (written out of window).

No training: loads the saved EXP-047 models (freq_ban.py --save-model, add mod 113, transformer, 2000 steps, seeds 150-159,
kinds eng/shuf, arms F/G) and ablates frequencies in the input embedding W_E[:113] at evaluation time.
Per model: base accuracy on the COMMON test set (pairs in neither the F nor the G train split of that seed/kind), then
  own   : remove the model's own 5 target frequencies (project W_E onto the complement of their cos/sin columns)
  other : remove the other arm's 5 targets
  energy: remove the same W_E energy as 'own', taken proportionally from all non-target frequencies (scale factor c)
drop_x = base_acc - acc_after_x.  Primary (eng): D_i = mean over the seed's two models of [drop_own - drop_energy] > 0.
Validity: both eng models of a seed load, their base common-test accuracy >= 0.9, the energy match is complete.
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


def remove_energy_elsewhere(W: np.ndarray, B: np.ndarray, targets, amount: float) -> tuple[np.ndarray, bool]:
    """Scale all non-target frequencies by c so that exactly `amount` energy is removed; (W', complete)."""
    rest = [k for k in range(1, K + 1) if k not in set(targets)]
    C = B.T @ W
    e_rest = float((C[cols(rest)] ** 2).sum())
    complete = amount <= e_rest
    c = np.sqrt(max(0.0, 1.0 - amount / e_rest)) if e_rest > 0 else 0.0
    C[cols(rest)] *= c
    return B @ C, complete


def load_model(d: Path):
    import torch
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
        e_own = energy(W, B, T[arm])
        W_en, complete = remove_energy_elsewhere(W, B, T[arm], e_own)
        arms[arm] = {"base_acc": base, "energy_own": e_own, "energy_total": float(((W - W.mean(0)) ** 2).sum()),
                     "drop_own": base - accuracy(m, remove(W, B, T[arm]), common),
                     "drop_other": base - accuracy(m, remove(W, B, T[other]), common),
                     "drop_energy": base - accuracy(m, W_en, common), "energy_match_complete": complete}
    r["arms"] = arms
    r["n_common_test"] = int(len(common))
    ok = all(v["base_acc"] >= ACC_MIN and v["energy_match_complete"] for v in arms.values())
    if not ok:
        r["reason"] = "base accuracy < 0.9 or incomplete energy match"
        return r
    r["valid"] = True
    r["D"] = float(np.mean([v["drop_own"] - v["drop_energy"] for v in arms.values()]))
    r["D_cross"] = float(np.mean([v["drop_own"] - v["drop_other"] for v in arms.values()]))
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
    amount = 0.3 * energy(W, B, [k for k in range(1, K + 1) if k not in T])
    We, complete = remove_energy_elsewhere(W, B, T, amount)
    removed = ((B.T @ W) ** 2).sum() - ((B.T @ We) ** 2).sum()
    assert complete and abs(removed - amount) < 1e-8 * amount and abs(energy(We, B, T) - energy(W, B, T)) < 1e-9
    assert not remove_energy_elsewhere(W, B, T, 1e9)[1]
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
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk != "rows"})
                      for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    main()
