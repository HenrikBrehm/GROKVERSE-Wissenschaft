"""P2f confirmation (FINDINGS programme A, generalisation of the P2d/P2e measure to the non-abelian group D59): splits, jobs, binding,
frozen analysis. Session 24 (UNTESTED until the selftest ran; Codex review before freezing).

Registration: lab/confirm/P2f_REGISTRATION.md. As confirm_p2e (fresh seeds 2340-2359, experiment id 6, one split pair F/G per seed), but
task D59 trained with group_train.py for STEPS = 12000 (EXP-072: first test >= 0.9 at median 4575, max 8150 of 10 pilot runs).
Measure (EXP-072 addendum a, the P2d measure in irrep form): X = W_E[:118] (element order of dihedral.py); P_S = projection onto the isotypic
columns (4 per 2-dim irrep k) of dihedral.irrep_basis(59); u_S = P_S X / ||P_S X||, X' = X - delta * u_S, delta = REL_DELTA * ||X|| for every S;
drop_S = mean correct-class logit margin on the pairs in neither split before minus after. N_CTRL control sets of 5 irreps from 1..29 without
own, other targets and fold(2k) of own (RNG [6, 59, seed, arm]).
PRIMARY per seed: D_s = mean over the two arms of (drop_own - mean drop_ctrl). One hypothesis (no family), one-sided t-test, 95 % bootstrap CI;
"bestätigt" = no technical failure (incl. load/forward exceptions), p < 0.05 and CI lower bound >= MIN_EFFECT (0.05 logit units).
Primary sample = ALL planned seeds; the subset with base accuracy >= 0.9 in both arms is reported descriptively without a verdict label,
as is the energy share of the own irreps in W_E.
"""
from __future__ import annotations

import importlib.util
import io
import json
import shlex
import tempfile
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(ROOT / "training"))
import confirm_p1 as c1  # noqa: E402  (read-only reuse: interp, t-test, bootstrap)
import confirm_splits as cs  # noqa: E402
from bound_block import Block, selftest_binding, sha  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

RAW = LAB / "confirm" / "p2f_raw"
BIND = LAB / "confirm" / "p2f_bindings"
SPL = LAB / "confirm" / "p2f_splits"
GT = "lab/experiments/EXP-046-dihedral-steering/group_train.py"
DH_FILE = "lab/experiments/EXP-046-dihedral-steering/dihedral.py"
N = 59
G = 2 * N
ACC_MIN, ALPHA, MIN_EFFECT, REL_DELTA, N_CTRL = 0.9, 0.05, 0.05, 0.02, 4
S1_STEP, S1_PERM = 2000, 20000          # secondary S1 (EXP-072 Nachtrag b): own-irrep share at step 2000 vs grokking step
REGISTERED = {"experiment": 6, "eps": 2.0, "seeds": list(range(2340, 2360)), "task": "D", "n": N, "steps": 12000,
              "device": "cuda", "threads": 1}
CODE_FILES = ("lab/tools/confirm_p2f.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_splits.py",
              "lab/tools/result_loader.py", "lab/tools/trainer_guard.py", "lab/tools/paket_a_device.py", GT, DH_FILE,
              "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/make_split.py")

_dh = None


def dh():
    global _dh
    if _dh is None:
        spec = importlib.util.spec_from_file_location("dihedral", ROOT / DH_FILE)
        _dh = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_dh)
    return _dh


def stem(s: int, arm: str) -> str:
    return f"p2f_D{N}_seed{s}_{arm}"


def write_splits(man: dict) -> None:
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(s, a)}.npy" for s in man["seeds"] for a in "FG"]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("P2f splits exist already: never overwrite")
    for s in man["seeds"]:
        T = cs.target_sets(man["experiment"], "D", N, s)
        for a in "FG":
            idx, targ = cs.build(man["experiment"], "D", N, s, a, man["eps"])
            assert targ == T[a]
            with open(SPL / f"{stem(s, a)}.npy", "xb") as f:
                np.save(f, idx.astype(np.int64))
            with open(SPL / f"{stem(s, a)}.json", "x", encoding="utf-8") as f:
                json.dump({"seed": s, "task": "D", "n": N, "arm": a, "targets": T[a], "other_targets": T["G" if a == "F" else "F"],
                           "n_train": int(len(idx)), "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(man: dict, s: int) -> str | None:
    T = cs.target_sets(man["experiment"], "D", N, s)
    for a in "FG":
        idx, targ = cs.build(man["experiment"], "D", N, s, a, man["eps"])
        f, j = SPL / f"{stem(s, a)}.npy", SPL / f"{stem(s, a)}.json"
        if not f.exists() or not j.exists():
            return f"{stem(s, a)}: split file missing"
        meta = json.loads(j.read_text(encoding="utf-8"))
        if not (np.array_equal(np.load(f), idx.astype(np.int64)) and meta.get("targets") == targ == T[a]
                and meta.get("other_targets") == T["G" if a == "F" else "F"] and meta.get("seed") == s):
            return f"{stem(s, a)}: differs from the deterministic rebuild"
    return None


def trainer_jobs(man: dict) -> list[str]:
    return [f"{c1.interp(man)} {GT} --seed {s} --n {N} --steps {man['steps']} --threads {man['threads']} --device {man['device']} "
            f"--split-file lab/confirm/p2f_splits/{stem(s, a)}.npy --out-root lab/confirm/p2f_raw --save-model"
            for s in man["seeds"] for a in "FG"]


def expected_run_id(cmd: list[str]) -> str:
    """group_train: EXP-046_seed<seed>_<split stem>_dev<device without ':'>."""
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    return f"EXP-046_seed{g('--seed')}_{Path(g('--split-file')).stem}_dev{(g('--device') or 'cpu').replace(':', '')}"


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_p2f", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_p2f.py")


# ---------------------------------------------------------------- measure
def fold(x: int) -> int:
    x %= N
    return min(x, N - x)


def control_sets(own: list[int], other: list[int], key: list[int]) -> list[list[int]]:
    excl = set(own) | set(other) | {fold(2 * k) for k in own}
    pool = [k for k in range(1, dh().n_irrep2(N) + 1) if k not in excl]
    rng = np.random.default_rng(key)
    return [sorted(int(k) for k in rng.choice(pool, 5, replace=False)) for _ in range(N_CTRL)]


def proj(X: np.ndarray, S: list[int]) -> np.ndarray:
    """Projection of the element-ordered rows X [2n, d] onto the isotypic components of the 2-dim irreps S."""
    B, labels = dh().irrep_basis(N)
    Bs = B[:, np.isin(np.array(labels), [f"k{k}" for k in S])]
    if Bs.shape[1] != 4 * len(set(S)):
        raise ValueError(f"irrep set {S} does not select 4 columns per irrep")
    return Bs @ (Bs.T @ X)


def load_model(data: bytes):
    import torch
    torch.set_num_threads(4)
    from grokverse.config import get_config
    from grokverse.models import build_model
    m = build_model(get_config("arch25k", seed=0, steps=10, threads=1, p=G))
    m.load_state_dict(torch.load(io.BytesIO(data), map_location="cpu"))
    m.eval()
    return m


def evaluate(m, rows: np.ndarray | None, idx: np.ndarray) -> dict:
    import torch
    T = dh().compose_table(N)
    with torch.no_grad():
        saved = m.W_E.data.clone()
        try:
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
            margin = float((corr - wrong.max(1).values).mean())
        finally:
            m.W_E.data.copy_(saved)
    return {"acc": acc, "margin": margin}


def measure(s: int, arm: str, T: dict, common: np.ndarray, data: bytes) -> dict:
    m = load_model(data)
    X = m.W_E.detach().numpy().astype(np.float64)[:G]
    other = "G" if arm == "F" else "F"
    ctrl = control_sets(T[arm], T[other], [6, N, s, ord(arm)])
    base = evaluate(m, None, common)
    delta = REL_DELTA * float(np.linalg.norm(X))
    dr = {}
    for k, S in ({"own": T[arm]} | {f"c{i}": c for i, c in enumerate(ctrl)}).items():
        PS = proj(X, S)
        dr[k] = base["margin"] - evaluate(m, X - delta * PS / np.linalg.norm(PS), common)["margin"]
    energy_own = float((proj(X, T[arm]) ** 2).sum() / (X ** 2).sum())
    return {"base": base, "drop_own": dr["own"], "drop_ctrl": [dr[f"c{i}"] for i in range(N_CTRL)], "ctrl_sets": ctrl, "energy_own": energy_own}


# ---------------------------------------------------------------- analysis
def arm_row(man: dict, s: int, arm: str, T: dict, common: np.ndarray) -> dict | str:
    split = SPL / f"{stem(s, arm)}.npy"
    cmd = ["x", GT, "--seed", str(s), "--device", man["device"], "--split-file", str(split)]
    d = run_dir(cmd)
    if not d.exists():
        return "fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"defekt: {why}"
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=man["steps"], split_file=split, config={"p": G},
                           files=("model_final.pt",)))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    if (why := BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(split):
        return f"defekt after load: {why or 'split bytes differ'}"
    try:
        out = measure(s, arm, T, common, BLOCK.bound_bytes(man, L.path / "model_final.pt"))
    except Exception as ex:                    # as P2e (Codex s23 point 1): any load/forward failure is technical, never an abort
        return f"defekt: {type(ex).__name__}: {ex}"
    return {**out, **s1_fields(L.path, L.res, T[arm], man["steps"])}


def s1_fields(d: Path, res: dict, own: list[int], steps: int) -> dict:
    """Secondary S1 inputs, isolated from the primary path (Codex recheck s24): any problem gives None, never a technical failure."""
    gen = res.get("generalization_step")
    try:
        st = np.load(d / "spectra_steps.npy").tolist()
        pw = np.asarray(np.load(d / "spectra.npy")[st.index(S1_STEP)], dtype=np.float64)
        share = float(pw[[k - 1 for k in own]].sum() / pw.sum()) if pw.shape == (dh().n_irrep2(N),) and np.all(np.isfinite(pw)) else None
    except Exception:                                        # noqa: BLE001 (secondary only)
        share = None
    return {"share_own_2000": share, "gen_step": int(gen) if gen is not None else steps + 1}   # never generalised: censored, ranked last


def validity(arms: dict) -> dict:
    vals = [v["drop_own"] for v in arms.values()] + [x for v in arms.values() for x in v["drop_ctrl"]] + [v["base"]["margin"] for v in arms.values()]
    if not all(np.isfinite(x) for x in vals):
        return {"valid": False, "technical": True, "reason": "non-finite margin"}
    D = float(np.mean([v["drop_own"] - np.mean(v["drop_ctrl"]) for v in arms.values()]))
    return {"valid": True, "technical": False, "D": D, "generalised": all(v["base"]["acc"] >= ACC_MIN for v in arms.values())}


def seed_row(man: dict, s: int) -> dict:
    r: dict = {"seed": s, "valid": False}
    T = {a: json.loads((SPL / f"{stem(s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
    trains = [np.load(SPL / f"{stem(s, a)}.npy") for a in "FG"]
    common = np.setdiff1d(np.arange(G * G), np.union1d(*trains))
    arms = {}
    for arm in "FG":
        a = arm_row(man, s, arm, T, common)
        if isinstance(a, str):
            return {**r, "reason": f"{arm}: {a}", "technical": True}
        arms[arm] = a
    return {**r, "arms": arms, **validity(arms)}


def stats(D: np.ndarray, rng: np.random.Generator) -> dict:
    tt = c1.t_test_secondary(D)
    return {"n": int(len(D)), "mean": float(D.mean()), "sd": float(D.std(ddof=1)), "t": tt["t"], "p": tt["p_one_sided"],
            "ci95": c1.boot_ci(D, rng), "n_positive": int((D > 0).sum())}


def rankdata(v: np.ndarray) -> np.ndarray:
    o = np.argsort(v, kind="stable")
    r = np.empty(len(v))
    r[o] = np.arange(len(v))
    for u in np.unique(v):                                   # average ranks for ties
        r[v == u] = r[v == u].mean()
    return r


def secondary_s1(rows: list[dict], n_planned: int, rng: np.random.Generator) -> dict:
    """S1 (secondary, own label, not part of the primary verdict): seeds with a larger own-irrep share at step 2000 grok earlier.
    Per seed x = mean over arms of share_own_2000, y = mean over arms of gen_step (censored = steps + 1); Spearman rho(x, y),
    one-sided permutation p (rho <= observed). "S1 bestätigt" = rho < 0 and p < ALPHA; any technical failure -> nicht auswertbar."""
    if (any(r.get("technical") for r in rows) or len(rows) != n_planned or n_planned < 5
            or any(v.get("share_own_2000") is None for r in rows for v in r["arms"].values())):
        return {"verdict": "nicht auswertbar"}
    x = np.array([np.mean([v["share_own_2000"] for v in r["arms"].values()]) for r in rows])
    y = np.array([np.mean([v["gen_step"] for v in r["arms"].values()]) for r in rows])
    rx, ry = rankdata(x), rankdata(y)
    if np.std(rx) == 0 or np.std(ry) == 0:                   # Codex recheck s24: e.g. every arm censored -> rho undefined
        return {"n": len(rows), "verdict": "nicht auswertbar (Rangstatistik undefiniert)"}
    rho = float(np.corrcoef(rx, ry)[0, 1])
    perm = np.array([np.corrcoef(rng.permutation(rx), ry)[0, 1] for _ in range(S1_PERM)])
    p = float((1 + (perm <= rho).sum()) / (1 + S1_PERM))
    return {"n": len(rows), "rho": rho, "p_perm_one_sided": p, "n_censored_arms": int(sum(v["gen_step"] > REGISTERED["steps"] for r in rows for v in r["arms"].values())),
            "verdict": "S1 bestätigt" if rho < 0 and p < ALPHA else "S1 nicht bestätigt"}


def verdict(rows: list[dict], n_planned: int, rng: np.random.Generator) -> dict:
    n_tech = sum(1 for r in rows if r.get("technical"))
    if n_tech > 0 or len(rows) != n_planned or n_planned < 3:
        return {"n": len(rows), "n_technical": n_tech, "verdict": "nicht auswertbar"}
    out = {**stats(np.array([r["D"] for r in rows]), rng), "n_technical": 0}
    g = np.array([r["D"] for r in rows if r["generalised"]])
    out["n_generalised"] = int(len(g))
    out["descriptive_generalised_only"] = stats(g, rng) if len(g) >= 3 else None     # no verdict label
    out["energy_own_median"] = float(np.median([v["energy_own"] for r in rows for v in r["arms"].values()]))
    out["verdict"] = "bestätigt" if out["p"] < ALPHA and out["ci95"][0] >= MIN_EFFECT else "nicht bestätigt"
    return out


def analyze(manifest: Path) -> None:
    stale = LAB / "confirm" / "P2f_summary.json"            # Codex s24 point 2: an aborted analysis must not leave an older summary behind
    if stale.exists():
        stale.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for m in (split_mismatch(man, s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"P2f splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = [seed_row(man, s) for s in man["seeds"]]
    out = {"manifest_commit": man["commit"], "min_effect": MIN_EFFECT, "rel_delta": REL_DELTA, "n_planned": len(man["seeds"]),
           "D59": verdict(rows, len(man["seeds"]), np.random.default_rng(6)),
           "S1_secondary": secondary_s1(rows, len(man["seeds"]), np.random.default_rng(61)), "rows": rows}
    (LAB / "confirm" / "P2f_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    for bad in ({"seeds": list(range(2340, 2359))}, {"steps": 12000.0}, {"experiment": 5}, {"n": 61}):
        try:
            BLOCK.check_registered({**man, **bad})
            raise AssertionError(f"unregistered manifest accepted: {bad}")
        except SystemExit:
            pass
    tj = trainer_jobs(man)
    assert len(tj) == 40 and len(set(tj)) == 40 and all("p2f_raw" in j and "--save-model" in j and "group_train.py" in j and "\\" not in j for j in tj)
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert ids[0] == "EXP-046_seed2340_p2f_D59_seed2340_F_devcuda", ids[0]
    assert len(set(ids)) == 40
    T = cs.target_sets(6, "D", N, 2340)
    assert T != cs.target_sets(5, "D", N, 2340) and not set(T["F"]) & set(T["G"]) and max(T["F"] + T["G"]) <= 29
    # measure semantics: projector, isotypic columns, control pool
    Xt = np.random.default_rng(0).standard_normal((G, 8))
    P = proj(Xt, [3, 7])
    assert np.allclose(proj(P, [3, 7]), P) and np.allclose(proj(Xt, [3]) + proj(Xt, [7]), P) and np.allclose(proj(Xt - P, [3, 7]), 0, atol=1e-10)
    r3 = dh().rho(N, 3)                                    # a function built from rho_3 entries lies entirely in irrep 3
    f3 = np.stack([r3[:, 0, 0], r3[:, 1, 0]], 1)
    assert np.allclose(proj(f3, [3]), f3, atol=1e-10) and np.allclose(proj(f3, [4]), 0, atol=1e-10)
    c = control_sets([1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [6, 1])
    assert all(len(x) == 5 and not set(x) & set(range(1, 11)) and max(x) <= 29 for x in c)
    harm = {fold(2 * k) for k in range(11, 16)}             # Codex s24 point 3: {22, 24, 26, 28, 29}, outside own and other
    assert harm == {22, 24, 26, 28, 29}
    for key in range(50):
        assert all(not set(x) & (harm | set(range(1, 6)) | set(range(11, 16))) for x in control_sets(list(range(11, 16)), [1, 2, 3, 4, 5], [6, key]))
    good = {a: {"base": {"acc": 1.0, "margin": 5.0}, "drop_own": 0.3, "drop_ctrl": [0.0, 0.01, -0.01, 0.0], "energy_own": 0.9} for a in "FG"}
    v = validity(good)
    assert v["valid"] and v["generalised"] and abs(v["D"] - 0.3) < 1e-12
    assert validity({**good, "F": {**good["F"], "drop_own": float("nan")}})["technical"]
    rng = np.random.default_rng(0)
    mk = lambda D, g=True: {"valid": True, "technical": False, "D": D, "generalised": g, "arms": good}   # noqa: E731
    rows = [mk(0.2 + 0.005 * i) for i in range(20)]
    assert verdict(rows, 20, rng)["verdict"] == "bestätigt"
    assert verdict(rows[:19], 20, rng)["verdict"] == "nicht auswertbar"
    assert verdict(rows[:19] + [{"seed": 1, "valid": False, "technical": True}], 20, rng)["verdict"] == "nicht auswertbar"
    assert verdict([mk(0.0 + 0.004 * i) for i in range(20)], 20, rng)["verdict"] == "nicht bestätigt"
    s1rows = [{"technical": False, "arms": {a: {"share_own_2000": 0.4 + 0.01 * i, "gen_step": 9000 - 200 * i} for a in "FG"}} for i in range(20)]
    s1 = secondary_s1(s1rows, 20, np.random.default_rng(1))
    assert s1["verdict"] == "S1 bestätigt" and s1["rho"] < -0.99, s1
    assert secondary_s1(s1rows[:19], 20, rng)["verdict"] == "nicht auswertbar"
    flat = [{"technical": False, "arms": {a: {"share_own_2000": 0.4 + 0.01 * i, "gen_step": 5000 + 200 * i} for a in "FG"}} for i in range(20)]
    assert secondary_s1(flat, 20, np.random.default_rng(1))["verdict"] == "S1 nicht bestätigt"
    assert list(rankdata(np.array([3.0, 1.0, 3.0]))) == [1.5, 0.0, 1.5]
    cens = [{"technical": False, "arms": {a: {"share_own_2000": 0.4 + 0.01 * i, "gen_step": 12001} for a in "FG"}} for i in range(20)]
    assert secondary_s1(cens, 20, rng)["verdict"].startswith("nicht auswertbar")
    miss = [{**r, "arms": {**r["arms"], "F": {**r["arms"]["F"], "share_own_2000": None}}} if i == 3 else r for i, r in enumerate(s1rows)]
    assert secondary_s1(miss, 20, rng)["verdict"] == "nicht auswertbar"
    with tempfile.TemporaryDirectory() as tmp:               # s1_fields never raises and isolates bad spectra
        td = Path(tmp)
        assert s1_fields(td, {"generalization_step": 5000}, [1, 2], 12000) == {"share_own_2000": None, "gen_step": 5000}
        np.save(td / "spectra_steps.npy", np.array([0, 2000]))
        np.save(td / "spectra.npy", np.ones((2, dh().n_irrep2(N))))
        f = s1_fields(td, {}, [1, 2], 12000)
        assert abs(f["share_own_2000"] - 2 / 29) < 1e-12 and f["gen_step"] == 12001, f
    w = verdict(rows[:15] + [mk(0.0, False)] * 5, 20, rng)
    assert w["n"] == 20 and w["n_generalised"] == 15 and "verdict" not in w["descriptive_generalised_only"]
    import torch                                            # end-to-end measure() on a random model (P2e lesson)
    from grokverse.config import get_config
    from grokverse.models import build_model
    buf = io.BytesIO()
    torch.save(build_model(get_config("arch25k", seed=0, steps=10, threads=1, p=G)).state_dict(), buf)
    r = measure(2340, "F", T, np.arange(0, G * G, 7), buf.getvalue())
    assert len(r["drop_ctrl"]) == N_CTRL and all(np.isfinite([r["drop_own"], *r["drop_ctrl"], r["energy_own"]])), r
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    loaded = {Path(m.__file__).resolve().relative_to(ROOT.resolve()).as_posix() for m in list(sys.modules.values())
              if getattr(m, "__file__", None) and Path(m.__file__).resolve().is_relative_to((ROOT / "lab").resolve())}
    assert loaded <= set(CODE_FILES), sorted(loaded - set(CODE_FILES))
    print("[confirm_p2f] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
