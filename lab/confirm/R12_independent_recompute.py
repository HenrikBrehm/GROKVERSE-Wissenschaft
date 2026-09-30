"""Independent re-computation of R12, built only from R12_REGISTRATION_DRAFT.md and R5 "Fassung 2"
(confirm_r12.py / confirm_r5.py deliberately NOT read). --selftest: synthetic checks (tempdir only);
--analyze: reads r12_raw, prints and writes R12_independent_recompute.json. MC seeds differ from the
official code, so p values agree only approximately; events, L, means and ratios must agree exactly."""
from __future__ import annotations

import argparse, hashlib, json, math, sys, tempfile
from pathlib import Path
from typing import Callable, Optional

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SPLITS, RAW = ROOT / "lab/confirm/r12_splits", ROOT / "lab/confirm/r12_raw"
OUT = ROOT / "lab/confirm/R12_independent_recompute.json"
TASKS = {"add97": ("add", 97), "mul113": ("mul", 113)}
ARMS = ("R", "E2_0", "D_0", "E2_1", "D_1")
N_UNITS, HORIZON, TEST_EVERY, TRAIN_EVERY = 20, 8000, 25, 10
TEST_THR, TRAIN_THR, TIE, ALPHA = 0.95, 0.99, 1e-9, 0.05
N_BOOT, N_FLIP, SEED_BOOT, SEED_FLIP = 10_000, 100_000, 12_12_2026, 30_09_2026
Part = tuple[float, bool]  # (bounded time b, event observed)


class Unusable(Exception):
    """Any violation that makes the whole block 'nicht auswertbar'."""


def check_grid(steps: object, accs: object, every: int, what: str) -> None:
    want = list(range(0, HORIZON + 1, every))
    if not (isinstance(steps, list) and isinstance(accs, list) and len(steps) == len(accs) == len(want)):
        raise Unusable(f"{what}: grid length")
    if any(type(s) is not int or s != w for s, w in zip(steps, want)) or any(
            type(a) not in (int, float) or not math.isfinite(a) or not 0 <= a <= 1 for a in accs):
        raise Unusable(f"{what}: grid not exactly 0:{every}:{HORIZON} or bad accuracy values")


def event_step(dense: dict) -> Optional[int]:
    """First test eval s with test>=.95 at s, s+25, s+50 and train>=.99 at some step <= s."""
    check_grid(dense.get("test_steps"), dense.get("test_acc"), TEST_EVERY, "test")
    check_grid(dense.get("train_steps"), dense.get("train_acc"), TRAIN_EVERY, "train")
    te, first_mem = dense["test_acc"], next(
        (i * TRAIN_EVERY for i, a in enumerate(dense["train_acc"]) if a >= TRAIN_THR), None)
    for i in range(len(te) - 2):  # s+50 must have been evaluated, so s <= 7950
        if first_mem is not None and first_mem <= i * TEST_EVERY and min(te[i:i + 3]) >= TEST_THR:
            return i * TEST_EVERY
    return None


def order_sign(early: list[Part], late: list[Part]) -> int:
    """early/late = parts of the side predicted faster (E) / slower (R, D); aggregate = geometric
    mean, observed iff all parts are. +1 late really later, -1 really earlier, 0 undetermined."""
    d = float(np.mean([math.log2(b) for b, _ in late]) - np.mean([math.log2(b) for b, _ in early]))
    oe, ol = all(o for _, o in early), all(o for _, o in late)
    # one side censored (true time >= its bound): order known only if the observed side is smaller
    if abs(d) <= TIE or not ((oe and ol) or (oe and d > 0) or (ol and d < 0)):
        return 0
    return 1 if d > 0 else -1


def binom_upper(k: int, n: int) -> float:
    return 1.0 if n == 0 else sum(math.comb(n, i) for i in range(k, n + 1)) / 2.0 ** n


def stats(L: np.ndarray, signs: list[int]) -> dict:
    n, m = len(L), float(np.mean(L))
    boot = L[np.random.default_rng(SEED_BOOT).integers(0, n, size=(N_BOOT, n))].mean(axis=1)
    flips = (np.random.default_rng(SEED_FLIP).integers(0, 2, size=(N_FLIP, n)) * 2 - 1) * L
    npos, ndet = sum(s > 0 for s in signs), sum(s != 0 for s in signs)
    p_flip = (int(np.sum(flips.mean(axis=1) >= m - 1e-12)) + 1) / (N_FLIP + 1)  # +1 correction
    p_sign = binom_upper(npos, ndet)  # exact one-sided, over units with determined order
    return {"n": n, "mean_L": m, "ratio": 2.0 ** m, "p": max(p_flip, p_sign), "p_flip": p_flip,
            "ci95_ratio": [2.0 ** q for q in np.percentile(boot, [2.5, 97.5])], "p_sign": p_sign,
            "sign_pos": npos, "sign_det": ndet, "L": L.tolist(), "signs": signs}


def holm(ps: dict[str, float]) -> dict[str, str]:
    order, out, alive = sorted(ps, key=lambda k: ps[k]), {}, True
    for i, k in enumerate(order):
        alive = alive and ps[k] <= ALPHA / (len(order) - i)
        out[k] = "bestätigt" if alive else "nicht bestätigt"
    return out


def analyse_task(runs: dict[tuple[int, str], Part]) -> dict:
    Ler, Led, ser, sed = [], [], [], []
    for u in range(N_UNITS):
        r = {a: runs[(u, a)] for a in ARMS}
        lg = {a: math.log2(r[a][0]) for a in ARMS}
        Ler.append(lg["R"] - lg["E2_0"])
        Led.append(float(np.mean([lg[f"D_{j}"] - lg[f"E2_{j}"] for j in (0, 1)])))
        ser.append(order_sign([r["E2_0"]], [r["R"]]))
        sed.append(order_sign([r["E2_0"], r["E2_1"]], [r["D_0"], r["D_1"]]))
    return {"H-ER": stats(np.array(Ler), ser), "H-ED": stats(np.array(Led), sed)}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_block(splits: Path, raw: Path, tasks: dict = TASKS, n_units: int = N_UNITS) -> dict:
    # Runs are found via result.json fingerprint_fields.split_file_sha256 / test_file_sha256 (smoke run:
    # = sha256 of the .npy bytes): independent of path spelling and directory names. Top-level
    # 'split_hash' has an undocumented definition (unused); the split_file basename is a 2nd check.
    index, init, found = {}, {}, {}
    for key, (task, p) in tasks.items():
        for u in range(n_units):
            meta = json.loads((splits / f"r12_{key}_u{u}.json").read_text(encoding="utf-8"))
            if (meta["task"], meta["p"], meta["unit"]) != (task, p, u):
                raise Unusable(f"split meta mismatch {key} u{u}")
            init[(key, u)], tst = meta["init"], sha(splits / f"r12_{key}_u{u}_test.npy")
            for a in ARMS:
                f = splits / f"r12_{key}_u{u}_{a}.npy"
                if sha(f) in index:
                    raise Unusable(f"duplicate split hash {f.name}")
                index[sha(f)] = (key, u, a, f.name, tst)
    for rj in sorted(raw.glob("*/result.json")):
        d = json.loads(rj.read_text(encoding="utf-8"))
        fp, cfg, fa = d.get("fingerprint_fields") or {}, d.get("config") or {}, d.get("final_acc") or {}
        hit = index.get(fp.get("split_file_sha256"))
        if hit is None:
            continue  # not an R12 split; an R12 run with a wrong hash surfaces as "missing"
        key, u, a, fname, tst = hit
        if (key, u, a) in found:
            raise Unusable(f"two result.json for {key} u{u} {a}")
        checks = {"status": d.get("status") == "completed", "test hash": fp.get("test_file_sha256") == tst,
                  "split name": Path(str(d.get("split_file"))).name == fname,
                  "task/p": (cfg.get("task"), cfg.get("p")) == tasks[key],
                  "seed": d.get("seed") == cfg.get("seed") == init[(key, u)],
                  "device": d.get("device") == "cuda", "train_frac": cfg.get("train_frac") == 0.3,
                  "budget": d.get("steps_completed") == HORIZON == cfg.get("steps"),
                  "final_acc": all(type(fa.get(k)) in (int, float) and math.isfinite(fa[k])
                                   for k in ("train", "test"))}
        if not all(checks.values()):
            raise Unusable(f"{rj.parent.name}: failed {[k for k, ok in checks.items() if not ok]}")
        ev = event_step(d.get("dense") or {})
        found[(key, u, a)] = {"event": ev, "b": float(HORIZON if ev is None else ev),  # ev <= 7950
                              "init": d.get("init_checksum_shared"), "dir": rj.parent.name}
    missing = [v[:3] for v in index.values() if v[:3] not in found]
    if missing:
        raise Unusable(f"{len(missing)} runs missing, e.g. {missing[0]}")
    for key, u in init:
        checksums = {found[(key, u, a)]["init"] for a in ARMS}
        if len(checksums) != 1 or None in checksums:
            raise Unusable(f"init checksum differs within {key} u{u}")
    return found


def analyze() -> dict:
    try:
        found = load_block(SPLITS, RAW)
    except Unusable as e:
        return {"block": "nicht auswertbar", "reason": str(e)}
    res, ps = {"block": "auswertbar", "tasks": {}}, {}
    for key in TASKS:
        f = {(u, a): found[(key, u, a)] for u in range(N_UNITS) for a in ARMS}
        res["tasks"][key] = t = analyse_task({k: (v["b"], v["event"] is not None) for k, v in f.items()})
        t["events"] = {a: [f[(u, a)]["event"] for u in range(N_UNITS)] for a in ARMS}
        ps.update({f"{key}/{h}": t[h]["p"] for h in ("H-ER", "H-ED")})
    res["holm"] = holm(ps)
    return res


def trace(test_ok_from: Optional[int], mem_at: Optional[int], dip: Optional[int] = None) -> dict:
    ts, tr = list(range(0, HORIZON + 1, 25)), list(range(0, HORIZON + 1, 10))
    te = [1.0 if test_ok_from is not None and s >= test_ok_from and s != dip else 0.1 for s in ts]
    ta = [1.0 if mem_at is not None and s >= mem_at else 0.5 for s in tr]
    return {"test_steps": ts, "test_acc": te, "train_steps": tr, "train_acc": ta}


def rejected(fn: Callable[[], object]) -> bool:
    try:
        fn()
    except Unusable:
        return True
    return False


def selftest() -> int:
    ev = lambda *a: event_step(trace(*a))  # noqa: E731
    assert ev(1000, 100) == 1000 and ev(0, 0) == 0 and ev(1000, 1500) == 1500  # memorisation first
    assert ev(1000, 1510) == 1525 and ev(1000, 100, 1050) == 1075               # three in a row
    assert ev(7950, 0) == 7950 and ev(7975, 0) is None and ev(None, 0) is None and ev(100, None) is None
    for key, i, val in (("test_steps", 3, 76), ("test_steps", 2, 50.0), ("test_acc", 5, float("nan")),
                        ("train_acc", 7, 1.5), ("train_acc", slice(800, None), [])):
        d = trace(1000, 0); d[key][i] = val
        assert rejected(lambda: event_step(d)), key
    O, C = True, False  # event observed / censored
    cases = [([(1000, O)], [(4000, O)], 1), ([(4000, O)], [(1000, O)], -1), ([(2000, O)], [(2000, O)], 0),
             ([(1000, O)], [(8000, C)], 1), ([(8000, C)], [(1000, O)], -1), ([(8000, C)], [(8000, C)], 0),
             ([(1000, O), (8000, C)], [(4000, O), (4000, O)], 0),  # E gm censored and larger
             ([(1000, O), (2000, O)], [(8000, C), (500, O)], 1),   # D gm 2000 > E gm 1414
             ([(1000, O), (4000, O)], [(8000, C), (100, O)], 0)]   # D gm 894 < 2000 but D censored
    assert all(order_sign(e, l) == want for e, l, want in cases) and binom_upper(0, 0) == 1.0
    assert abs(binom_upper(20, 20) - 2 ** -20) < 1e-18 and abs(binom_upper(15, 20) - 0.020694) < 1e-6
    t = analyse_task({(u, a): ((500.0, O) if a.startswith("E") else (4000.0, O))
                      for u in range(N_UNITS) for a in ARMS})
    assert all(t[h]["mean_L"] == 3.0 and t[h]["ratio"] == 8.0 and t[h]["sign_pos"] == 20
               and t[h]["p_flip"] < 2e-5 and t[h]["p"] == t[h]["p_flip"] for h in ("H-ER", "H-ED"))
    ok, no = "bestätigt", "nicht bestätigt"  # .03 > .05/2 stops Holm; second case hits all bounds
    assert list(holm({"a": .01, "b": .015, "c": .03, "d": .2}).values()) == [ok, ok, no, no]
    assert list(holm({"a": .0125, "b": .016, "c": .025, "d": .05}).values()) == [ok] * 4
    loader_selftest()
    print(json.dumps({"selftest": "ok"}))
    return 0


def loader_selftest() -> None:  # one-unit fixture; runs in arbitrary dirs, found by split hash
    with tempfile.TemporaryDirectory() as td:
        sp, rw = Path(td) / "s", Path(td) / "r"; sp.mkdir(); rw.mkdir()
        (sp / "r12_add97_u0.json").write_text(json.dumps({"task": "add", "p": 97, "unit": 0, "init": 7}))
        np.save(sp / "r12_add97_u0_test.npy", np.arange(3))

        def write(bad_arm: str = "", field: str = "", val: object = None) -> None:
            for i, a in enumerate(ARMS):
                np.save(sp / f"r12_add97_u0_{a}.npy", np.arange(5) + 10 * i)
                fp = {"split_file_sha256": sha(sp / f"r12_add97_u0_{a}.npy"),
                      "test_file_sha256": sha(sp / "r12_add97_u0_test.npy")}
                d = {"status": "completed", "seed": 7, "device": "cuda", "steps_completed": 8000,
                     "split_file": f"x/r12_add97_u0_{a}.npy", "init_checksum_shared": "c",
                     "final_acc": {"train": 1.0, "test": 0.9}, "dense": trace(1000 + 100 * i, 0),
                     "config": {"task": "add", "p": 97, "seed": 7, "steps": 8000, "train_frac": 0.3}}
                (fp if field.endswith("sha256") else d).update({field: val} if a == bad_arm else {})
                (rw / f"run{i}").mkdir(exist_ok=True)
                (rw / f"run{i}/result.json").write_text(json.dumps({**d, "fingerprint_fields": fp}))
        write()
        found = load_block(sp, rw, one := {"add97": TASKS["add97"]}, 1)
        assert [found[("add97", 0, a)]["event"] for a in ARMS] == [1000, 1100, 1200, 1300, 1400]
        for bad in (("D_0", "seed", 8), ("E2_1", "init_checksum_shared", "z"), ("R", "status", "failed"),
                    ("R", "steps_completed", 7990), ("E2_0", "test_file_sha256", "0"),
                    ("D_1", "split_file_sha256", "0"), ("D_1", "split_file", "x/r12_add97_u0_D_0.npy")):
            write(*bad)
            assert rejected(lambda: load_block(sp, rw, one, 1)), bad


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    for flag in ("--selftest", "--analyze"):
        g.add_argument(flag, action="store_true")
    if ap.parse_args().selftest:
        return selftest()
    res = analyze()
    print(txt := json.dumps(res, indent=1, ensure_ascii=False))
    OUT.write_text(txt + "\n", encoding="utf-8")
    return 0 if res["block"] == "auswertbar" else 2


if __name__ == "__main__":
    sys.exit(main())
