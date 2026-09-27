"""Split construction for the reserved confirmation block of FINDINGS "Programm" (P1), session 14. UNTESTED. Pure numpy.

Same constructions as the pilots (EXP-016/043 cyclic groups in group coordinates, EXP-046 D_n), but every random draw comes from
SeedSequence([1000001, experiment, task, p, seed, arm, purpose]) (FINDINGS spec [1000001, Versuch, Seed, Arm, Zweck], extended
by task and p so that add 113 and mul 113 at the same seed cannot share a stream; review s14). Writing split files requires a
frozen analysis manifest committed unchanged at the commit it names, so the block cannot be generated before the freeze:

  python lab/tools/confirm_splits.py --selftest
  python lab/tools/confirm_splits.py --manifest lab/confirm/P1_manifest.json      # writes lab/confirm/splits/
Manifest: {"commit": "<git id containing this manifest>", "experiment": 1, "seeds": [1000, ...], "eps": 2.0,
           "tasks": [{"task": "add", "p": 113}, {"task": "mul", "p": 113}, {"task": "D", "p": 59}, ...]}
Integer codes: task add 0, mul 1, D 2; arm F 0, G 1, R 2; purpose targets 0, phases 1, keys 2.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    """Load a module by path (EXP-043 and EXP-046 both have a make_split.py; review s14)."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


dh = _load("dihedral", LAB / "experiments/EXP-046-dihedral-steering/dihedral.py")   # EXP-046 make_split imports it by name
ms43 = _load("make_split_043", LAB / "experiments/EXP-043-generalize-steering/make_split.py")
ms46 = _load("make_split_046", LAB / "experiments/EXP-046-dihedral-steering/make_split.py")
group_coords, mask_power, n_freq = ms43.group_coords, ms43.mask_power, ms43.n_freq

ROOT_SALT, TRAIN_FRAC, M = 1_000_001, 0.3, 5
ARM = {"F": 0, "G": 1, "R": 2}
PURPOSE = {"targets": 0, "phases": 1, "keys": 2}
TASK_ID = {"add": 0, "mul": 1, "D": 2}
OUT = LAB / "confirm" / "splits"


def rng_for(experiment: int, task: str, p: int, seed: int, arm: str, purpose: str) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([ROOT_SALT, experiment, TASK_ID[task], p, seed, ARM[arm],
                                                         PURPOSE[purpose]]))


def n_targets_pool(task: str, p: int) -> int:
    return dh.n_irrep2(p) if task == "D" else n_freq(group_coords(task, p)[3])


def target_sets(experiment: int, task: str, p: int, seed: int) -> dict[str, list[int]]:
    """F and G disjoint, 5 each, from one stream (so they cannot collide by construction)."""
    ks = rng_for(experiment, task, p, seed, "F", "targets").permutation(np.arange(1, n_targets_pool(task, p) + 1))
    return {"F": sorted(int(k) for k in ks[:M]), "G": sorted(int(k) for k in ks[M:2 * M])}


def weights_cyclic(task: str, p: int, targets: list[int], eps: float, rng: np.random.Generator) -> np.ndarray:
    u, v, valid, n = group_coords(task, p)
    phi = rng.uniform(0, 2 * np.pi, size=(len(targets), n))
    wave = np.mean([np.cos(2 * np.pi * k * u / n + phi[i, (u + v) % n]) for i, k in enumerate(targets)], axis=0)
    return np.where(valid, np.clip(1.0 + eps * wave, 0.05, None), 1.0)


def weights_dihedral(n: int, targets: list[int], eps: float, rng: np.random.Generator) -> np.ndarray:
    G = 2 * n
    A = rng.standard_normal((len(targets), G, 2, 2))
    A /= np.linalg.norm(A, axis=(2, 3), keepdims=True)
    T = dh.compose_table(n)
    a, c = np.arange(G).repeat(G), T.reshape(-1)
    wave = np.mean([np.einsum("pij,pji->p", A[i, c], dh.rho(n, k)[a]) for i, k in enumerate(targets)], axis=0)
    return np.clip(1.0 + eps * wave, 0.05, None)


def draw(task: str, p: int, T: list[int], eps: float, rp: np.random.Generator, rk: np.random.Generator) -> np.ndarray:
    """The pilot construction with explicit phase and key streams (the pilots used one generator for both)."""
    if task == "D":
        dh.check_group(p)
    q = weights_dihedral(p, T, eps, rp) if task == "D" else weights_cyclic(task, p, T, eps, rp)
    keys = rk.random(len(q)) ** (1.0 / q)
    return np.sort(np.argsort(-keys)[:int(round(TRAIN_FRAC * len(q)))])


def build(experiment: int, task: str, p: int, seed: int, arm: str, eps: float) -> tuple[np.ndarray, list[int]]:
    T = target_sets(experiment, task, p, seed)["G" if arm == "G" else "F"]
    return draw(task, p, T, 0.0 if arm == "R" else eps, rng_for(experiment, task, p, seed, arm, "phases"),
                rng_for(experiment, task, p, seed, arm, "keys")), T


def m0(idx: np.ndarray, task: str, p: int) -> np.ndarray:
    return dh.mask_power(idx, p) if task == "D" else mask_power(idx, task, p)


def selftest() -> None:
    # (1) pilot regression: with the pilots' single generator injected, draw() reproduces the pilot splits bit for bit
    for task, p, seed, arm in (("add", 97, 70, "F"), ("mul", 113, 71, "G"), ("add", 113, 5, "F")):
        T = ms43.target_set(seed, task, p, arm)
        g = np.random.default_rng(seed + ms43.TARGET_SALT + ms43.TASK_SALT[task] + 1 + ms43.ARM_SALT[arm])
        assert np.array_equal(draw(task, p, T, 2.0, g, g), ms43.engineered_train_idx(seed, task, p, T, 2.0, arm)), (task, seed)
    for seed, arm in ((140, "F"), (141, "G")):
        T = ms46.target_set(seed, 59, arm)
        g = np.random.default_rng(seed + ms46.TARGET_SALT + 1 + ms46.ARM_SALT[arm])
        assert np.array_equal(draw("D", 59, T, 2.0, g, g), ms46.engineered_train_idx(seed, 59, T, 2.0, arm)), ("D", seed)
    # (2) new streams: strength like the pilots, task-specific bounds relative to the uniform share M/K
    for task, p in (("add", 113), ("add", 97), ("mul", 113), ("D", 59)):
        K = n_targets_pool(task, p)
        tg = target_sets(9, task, p, 1)
        assert not set(tg["F"]) & set(tg["G"]) and len(tg["F"]) == len(tg["G"]) == M, (task, tg)
        for arm in ("F", "G", "R"):
            idx, T = build(9, task, p, 1, arm, 2.0)
            assert np.array_equal(idx, build(9, task, p, 1, arm, 2.0)[0]), task             # deterministic
            pw = m0(idx, task, p)
            share = pw[[k - 1 for k in T]].sum() / pw.sum()
            top = set(int(k) + 1 for k in np.argsort(-pw)[:M])
            if arm == "R":
                assert share <= 1.3 * M / K, (task, arm, share)
            else:
                assert share > 1.5 * M / K and len(top & set(T)) >= 4, (task, arm, share, sorted(top), T)
    # (3) session 20 (Codex B1): code gate
    h = code_hashes()
    assert "lab/experiments/EXP-001-freq-ban/freq_ban.py" in h and any(k.startswith("training/grokverse/models/") for k in h)
    check_code({"code_sha256": h})
    for bad in ({}, {"code_sha256": {**h, "lab/tools/confirm_p1.py": "0" * 64}}, {"code_sha256": {k: v for k, v in list(h.items())[1:]}}):
        try:
            check_code(bad)
            raise AssertionError("code gate accepted a mismatch")
        except SystemExit:
            pass
    print("[confirm_splits] selftest ok", flush=True)


CODE_FILES = ("lab/tools/confirm_splits.py", "lab/tools/confirm_p1.py", "lab/tools/result_loader.py", "lab/tools/trainer_guard.py",
              "lab/experiments/EXP-001-freq-ban/freq_ban.py", "lab/experiments/EXP-043-generalize-steering/make_split.py",
              "lab/experiments/EXP-043-generalize-steering/analyze.py", "lab/experiments/EXP-046-dihedral-steering/make_split.py",
              "lab/experiments/EXP-046-dihedral-steering/group_train.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py")


def code_hashes() -> dict[str, str]:
    """Session 20 (Codex B1): SHA-256 of every file that builds splits, trains or analyses the block (plus all of
    training/grokverse). Stored in the frozen manifest; any later change to executed code makes the gate fail."""
    import hashlib
    files = list(CODE_FILES) + sorted(q.relative_to(LAB.parent).as_posix()
                                      for q in (LAB.parent / "training/grokverse").rglob("*.py") if "__pycache__" not in q.parts)
    return {f: hashlib.sha256((LAB.parent / f).read_bytes()).hexdigest() for f in files}


def check_code(man: dict) -> None:
    want = man.get("code_sha256")
    if not want:
        raise SystemExit("manifest has no 'code_sha256' (python lab/tools/confirm_splits.py --hash-code): freeze the code too (Codex B1)")
    have = code_hashes()
    diff = sorted(set(want) ^ set(have)) + sorted(f for f in set(want) & set(have) if want[f] != have[f])
    if diff:
        raise SystemExit(f"executed code differs from the frozen manifest: {diff[:5]}")


def check_manifest(manifest: Path, man: dict) -> None:
    """The manifest must be committed unchanged at man['commit'] and use only reserved seeds (review s14)."""
    c = str(man.get("commit", "")).strip()
    if not c:
        raise SystemExit("manifest has no 'commit': freeze and commit the analysis manifest first (FINDINGS, Regel 18c)")
    rel = manifest.resolve().relative_to(LAB.parent.resolve()).as_posix()
    got = subprocess.run(["git", "show", f"{c}:{rel}"], cwd=LAB.parent, capture_output=True, text=True, encoding="utf-8")
    if got.returncode != 0:
        raise SystemExit(f"manifest not found at commit {c}: {got.stderr.strip()}")
    frozen = json.loads(got.stdout)
    strip = lambda d: {k: v for k, v in d.items() if k != "commit"}   # noqa: E731
    if strip(frozen) != strip(man):
        raise SystemExit("manifest differs from its frozen version at the named commit")
    if not man["seeds"] or not all(1000 <= int(x) <= 1099 for x in man["seeds"]):
        raise SystemExit("seeds must lie in the reserved block 1000-1099")
    check_code(man)


def main(manifest: Path) -> None:
    man = json.loads(manifest.read_text(encoding="utf-8"))
    check_manifest(manifest, man)
    E, eps = int(man["experiment"]), float(man["eps"])
    jobs = [(t, s, arm, f"confirm_exp{E}_eps{eps}_{t['task']}{t['p']}_seed{s}_{arm}")
            for t in man["tasks"] for s in man["seeds"] for arm in ("F", "G", "R")]
    OUT.mkdir(parents=True, exist_ok=True)
    clash = [st for *_, st in jobs if (OUT / f"{st}.npy").exists() or (OUT / f"{st}.json").exists()]
    if clash:                                              # check everything before writing anything
        raise SystemExit(f"{len(clash)} confirmation splits exist already (e.g. {clash[0]}): never overwrite")
    for t, s, arm, st in jobs:
        idx, T = build(E, t["task"], t["p"], s, arm, eps)
        pw = m0(idx, t["task"], t["p"])
        with open(OUT / f"{st}.npy", "xb") as f:
            np.save(f, idx)
        with open(OUT / f"{st}.json", "x", encoding="utf-8") as f:
            json.dump({"targets": T, "arm": arm, "seed": s, **t, "experiment": E, "eps": 0.0 if arm == "R" else eps,
                       "n_train": int(len(idx)), "M0_target_share": float(pw[[k - 1 for k in T]].sum() / pw.sum()),
                       "manifest_commit": man["commit"]}, f)
    print(f"[confirm_splits] wrote {len(jobs)} splits to {OUT}")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif sys.argv[1:] == ["--hash-code"]:
        print(json.dumps(code_hashes(), indent=1))
    elif len(sys.argv) == 3 and sys.argv[1] == "--manifest":
        main(Path(sys.argv[2]))
    else:
        raise SystemExit(__doc__)
