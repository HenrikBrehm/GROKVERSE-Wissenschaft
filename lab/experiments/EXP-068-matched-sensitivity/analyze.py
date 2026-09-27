"""EXP-068 (exploration): sensitivity to old vs new target frequencies at matched perturbation size (equal step norm; equal removed energy)
on the 80 bound N29 final models. Definition: README.md (fixed before the computation). Run under guarded_run.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "tools"))
import confirm_n29 as n  # noqa: E402  (frozen N29 loader + binding, read-only)

REL_DELTA, FRAC_E = 0.02, 0.5


def drops(m, W: np.ndarray, old: list[int], new: list[int], test: np.ndarray) -> dict:
    ev = lambda Wr: n.p2.e55.evaluate(m, Wr, test)["margin"]   # noqa: E731
    base, Bm, delta = ev(None), n.p2.e51.basis(), REL_DELTA * float(np.linalg.norm(W))
    E = {k: n.p2.e51.energy(W, Bm, S) for k, S in (("old", old), ("new", new))}
    amount = FRAC_E * min(E.values())
    out = {"E_old": E["old"], "E_new": E["new"]}
    for k, S in (("old", old), ("new", new)):
        PS = n.g61().project(W, S)
        out[f"step_{k}"] = base - ev(W - delta * PS / np.linalg.norm(PS))
        out[f"energy_{k}"] = base - ev(n.p2.e51.remove_energy(W, Bm, S, amount))
    return out


def ratio(r: dict, kind: str) -> float | None:
    dom, weak = ("old", "new") if r["E_old"] >= r["E_new"] else ("new", "old")
    a, b = r[f"{kind}_{dom}"], r[f"{kind}_{weak}"]
    return float(np.log(a / b)) if a > 0 and b > 0 else None


def main() -> None:
    man = json.loads((LAB / "confirm/N29_manifest.json").read_text(encoding="utf-8"))
    n.BLOCK.check_manifest(LAB / "confirm/N29_manifest.json", man)
    rows = []
    for s in man["seeds"]:
        meta = json.loads((n.SPL / f"n29_seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        test = np.load(n.SPL / f"n29_seed{s}_test.npy")
        for t in man["ts"]:
            for first, second, old, new in (("A", "B", F, G), ("B", "A", G, F)):
                cmd = ["x", n.FB, "--seed", str(s), "--threads", "1", "--device", "cuda", "--split-file", str(n.SPL / f"{n.stem(s, first)}.npy"),
                       "--switch-split-file", str(n.SPL / f"{n.stem(s, second)}.npy"), "--switch-step", str(t)]
                d = n.run_dir(cmd)
                if (why := n.BLOCK.unbound(man, d)):
                    raise SystemExit(f"{d.name}: {why}")
                m = n.p2.load_model_bytes(n.BLOCK.bound_bytes(man, d / "model_final.pt"))
                W = m.W_E.detach().numpy().astype(np.float64)[:113]
                rows.append({"seed": s, "t": t, "dir": first + second, **drops(m, W, old, new, test)})
    out = {}
    for t in man["ts"]:
        rt = [r for r in rows if r["t"] == t]
        out[str(t)] = {}
        for kind in ("step", "energy"):
            q = [x for x in (ratio(r, kind) for r in rt) if x is not None]
            out[str(t)][kind] = {"n_defined": len(q), "n": len(rt), "median_log_dom_over_weak": float(np.median(q)) if q else None,
                                 "frac_pos": float(np.mean(np.array(q) > 0)) if q else None,
                                 "median_drop_dom": float(np.median([r[f"{kind}_{'old' if r['E_old'] >= r['E_new'] else 'new'}"] for r in rt])),
                                 "median_drop_weak": float(np.median([r[f"{kind}_{'new' if r['E_old'] >= r['E_new'] else 'old'}"] for r in rt]))}
    (HERE / "summary.json").write_text(json.dumps({"summary": out, "rows": rows}, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
