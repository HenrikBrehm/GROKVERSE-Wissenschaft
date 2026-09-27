"""EXP-072 addendum (exploration, post hoc on the 10 pilot models): the P2d/P2e measure in its irrep form for D59.
u_S = P_S X / ||P_S X|| with P_S the projection onto the isotypic columns (4 per 2-dim irrep) of the D59 irrep basis, X = W_E[:118];
X' = X - delta * u_S, delta = 0.02 ||X||; drop = mean correct-class logit margin on pairs in neither split, before minus after.
4 control sets of 5 irreps (1..29 without own, other and fold(2k) of own). D = mean over arms of (drop_own - mean drop_ctrl). Run under guarded_run.py.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB.parent / "training"))
_spec = importlib.util.spec_from_file_location("dihedral", LAB / "experiments/EXP-046-dihedral-steering/dihedral.py")
dh = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dh)
N, REL_DELTA, N_CTRL = 59, 0.02, 4
G = 2 * N


def fold(x: int) -> int:
    x %= N
    return min(x, N - x)


def load(d: Path):
    from grokverse.config import get_config
    from grokverse.models import build_model
    m = build_model(get_config("arch25k", seed=0, steps=10, threads=1, p=G))
    m.load_state_dict(torch.load(d / "model_final.pt", map_location="cpu"))
    return m.eval()


def margin(m, rows: np.ndarray | None, idx: np.ndarray, T: np.ndarray) -> tuple[float, float]:
    with torch.no_grad():
        saved = m.W_E.data.clone()
        if rows is not None:
            m.W_E.data[:G] = torch.from_numpy(rows).to(m.W_E.dtype)
        a, b = idx // G, idx % G
        x = torch.from_numpy(np.stack([a, b, np.full(len(idx), G)], 1)).long()
        lg = m.logits_last(x)[:, :G].double()
        y = torch.from_numpy(T[a, b]).long()
        acc = float((lg.argmax(-1) == y).double().mean())
        corr = lg.gather(1, y[:, None])[:, 0]
        wrong = lg.clone()
        wrong.scatter_(1, y[:, None], -float("inf"))
        mg = float((corr - wrong.max(1).values).mean())
        m.W_E.data.copy_(saved)
    return acc, mg


def main() -> None:
    torch.set_num_threads(4)
    B, labels = dh.irrep_basis(N)
    lab = np.array(labels)
    T = dh.compose_table(N)
    proj = lambda X, S: (lambda Bs: Bs @ (Bs.T @ X))(B[:, np.isin(lab, [f"k{k}" for k in S])])   # noqa: E731
    Xt = np.random.default_rng(0).standard_normal((G, 8))                                       # self check: projector
    assert np.allclose(proj(proj(Xt, [3, 7]), [3, 7]), proj(Xt, [3, 7])) and np.allclose(proj(Xt, [3]) + proj(Xt, [7]), proj(Xt, [3, 7]))
    rows = []
    for s in range(1000, 1005):
        stems = {a: f"confirm_exp1_eps2.0_D59_seed{s}_{a}" for a in "FG"}
        tg = {a: json.loads((LAB / "confirm/splits" / f"{stems[a]}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
        common = np.setdiff1d(np.arange(G * G), np.union1d(*[np.load(LAB / "confirm/splits" / f"{stems[a]}.npy") for a in "FG"]))
        arms = {}
        for a in "FG":
            m = load(HERE / "raw" / f"EXP-046_seed{s}_{stems[a]}_devcuda")
            X = m.W_E.detach().numpy().astype(np.float64)[:G]
            own, other = tg[a], tg["G" if a == "F" else "F"]
            pool = [k for k in range(1, 30) if k not in set(own) | set(other) | {fold(2 * k) for k in own}]
            rng = np.random.default_rng([72, s, ord(a)])
            ctrl = [sorted(int(k) for k in rng.choice(pool, 5, replace=False)) for _ in range(N_CTRL)]
            acc0, m0 = margin(m, None, common, T)
            delta = REL_DELTA * float(np.linalg.norm(X))
            drop = {}
            for key, S in [("own", own)] + [(f"c{i}", c) for i, c in enumerate(ctrl)]:
                PS = proj(X, S)
                drop[key] = m0 - margin(m, X - delta * PS / np.linalg.norm(PS), common, T)[1]
            e_own = float((proj(X, own) ** 2).sum() / (X ** 2).sum())
            arms[a] = {"acc": acc0, "margin": m0, "drop_own": drop["own"], "drop_ctrl": [drop[f"c{i}"] for i in range(N_CTRL)], "energy_own": e_own}
        D = float(np.mean([v["drop_own"] - np.mean(v["drop_ctrl"]) for v in arms.values()]))
        rows.append({"seed": s, "D": D, "arms": arms})
        print(s, round(D, 3), {a: (round(v["acc"], 3), round(v["drop_own"], 3), round(float(np.mean(v["drop_ctrl"])), 3), round(v["energy_own"], 3)) for a, v in arms.items()}, flush=True)
    D = np.array([r["D"] for r in rows])
    out = {"D_mean": float(D.mean()), "D_sd": float(D.std(ddof=1)), "n_pos": int((D > 0).sum()), "rows": rows}
    (HERE / "p2d_irrep_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print({k: v for k, v in out.items() if k != "rows"})


if __name__ == "__main__":
    main()
