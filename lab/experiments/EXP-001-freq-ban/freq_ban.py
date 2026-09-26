#!/usr/bin/env python3
"""EXP-001 — training-time frequency ban ("Frequenzverbot").

Question: are the Fourier frequencies that emerge in the transformer's embedding
DURING the memorization plateau causally needed for the grokking transition, or
does the network route around a ban with little delay?

From step ``t0`` on, after every optimizer step, the token rows ``W_E[:p]`` are
projected onto the orthogonal complement of the real-DFT subspace of a banned
frequency set K (each frequency k spans cos(2πka/p) and sin(2πka/p) over a).
The '=' row is left alone. Everything else mirrors ``grokverse.train``
(same preset ``arch25k``, same seed order, full-batch AdamW), so up to ``t0``
the trajectory is the baseline's.

Conditions
  baseline       no ban
  ban_emerging   K = the m frequencies with the largest W_E power at t0
  ban_random     K = m frequencies drawn (seeded) from power ranks > 2m at t0
  ban_destined   K = top-m W_E frequencies of the STORED 25k baseline model of
                 the same seed, banned from step 1 (t0 is ignored)
  shrink_matched (amendment, secondary control) at t0, ONCE, scale the non-constant
                 Fourier part of W_E[:p] so that the removed power equals the power a
                 top-m ban would remove at t0. No persistent constraint.
  init_swap      (EXP-010) no ban. At init, the DFT coefficients of W_E[:p] of the m
                 strongest frequencies T are swapped with those of m weak frequencies S
                 (drawn like ban_random, seed + SWAP_SALT). Norm and distribution of the
                 iid-normal init are preserved; data split and all other weights are
                 identical to the baseline of the same seed. t0 is ignored.
  init_magswap   (EXP-011) like init_swap, but only the block NORMS of each pair (t, s) are
                 exchanged; each frequency keeps its own coefficient direction. The power
                 spectrum after the swap equals init_swap's; only the directions differ.

Run ONLY through lab/tools/guarded_run.py (run window). Example, from the root:
    python lab/tools/guarded_run.py -- python lab/experiments/EXP-001-freq-ban/freq_ban.py \
        --seed 0 --condition ban_emerging
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "training"))

from grokverse.config import THRESHOLD_SETS, get_config  # noqa: E402
from grokverse.data import make_dataset, split_hash  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.seed import set_seed  # noqa: E402
from grokverse.train import all_transitions, evaluate  # noqa: E402
from grokverse.utils import git_commit, lib_versions  # noqa: E402

CONDITIONS = ("baseline", "ban_emerging", "ban_random", "ban_destined", "init_swap",
              "shrink_matched", "init_magswap")
INIT_CONDITIONS = ("init_swap", "init_magswap")   # init-only interventions, no ban
EXP_ID = "EXP-001"
EXP_ID_BY_CONDITION = {"init_swap": "EXP-010", "init_magswap": "EXP-011"}
SWAP_SALT = 20_011            # init_swap draws S with seed + salt
RANDOM_SALT = 10_007          # ban_random draws with seed + salt, never the run seed itself
SPECTRUM_EVERY = 250          # steps between stored W_E power spectra
PARTIAL_WRITE_EVERY = 500     # steps between partial result.json writes
STORED_RUN = "txf_add_p113_wd1.0_frac0.3_seed{seed}_arch25k"


# --------------------------------------------------------------------------- #
# Fourier helpers (pure; tested in test_freq_ban.py)
# --------------------------------------------------------------------------- #
def fourier_basis(p: int) -> np.ndarray:
    """Orthonormal real DFT basis over Z_p as a [p, p] matrix, columns
    [const, cos_1, sin_1, ..., cos_K, sin_K] with K = (p-1)//2 (p odd)."""
    if p % 2 == 0:
        raise ValueError("fourier_basis assumes odd p (no Nyquist column)")
    a = np.arange(p)
    cols = [np.ones(p) / np.sqrt(p)]
    for k in range(1, (p - 1) // 2 + 1):
        cols.append(np.cos(2 * np.pi * k * a / p) * np.sqrt(2 / p))
        cols.append(np.sin(2 * np.pi * k * a / p) * np.sqrt(2 / p))
    return np.stack(cols, axis=1)


def freq_columns(freqs) -> list[int]:
    """Column indices of frequencies ``freqs`` (1-based) in ``fourier_basis``."""
    return [c for k in freqs for c in (2 * k - 1, 2 * k)]


def freq_power(W: np.ndarray, basis: np.ndarray) -> np.ndarray:
    """Power of W [p, d] per frequency k = 1..(p-1)//2 (index k-1)."""
    coef = basis.T @ W                               # [p, d]
    sq = (coef ** 2).sum(axis=1)
    return sq[1::2] + sq[2::2]


def top_frequencies(power: np.ndarray, m: int) -> list[int]:
    """1-based frequencies of the m largest entries; ties broken by lower k."""
    order = np.lexsort((np.arange(len(power)), -power))
    return sorted(int(i) + 1 for i in order[:m])


def random_frequencies(power: np.ndarray, m: int, rng_seed: int) -> list[int]:
    """m frequencies drawn from power ranks strictly below 2m (i.e. far from the top)."""
    order = np.lexsort((np.arange(len(power)), -power))
    pool = np.sort(order[2 * m:]) + 1
    rng = np.random.default_rng(rng_seed)
    return sorted(int(k) for k in rng.choice(pool, size=m, replace=False))


def swap_pairs(power: np.ndarray, m: int, rng_seed: int) -> list[tuple[int, int]]:
    """Pairs (t, s): the m strongest frequencies (by descending power) with m weak ones
    drawn from power ranks >= 2m (ascending k), both 1-based."""
    order = np.lexsort((np.arange(len(power)), -power))
    strong = [int(i) + 1 for i in order[:m]]
    weak = random_frequencies(power, m, rng_seed)
    return list(zip(strong, weak))


def swap_frequency_coefficients(W: np.ndarray, basis: np.ndarray,
                                pairs: list[tuple[int, int]]) -> np.ndarray:
    """New W [p, d] with the (cos, sin) DFT coefficient rows of each pair (k, j) exchanged.
    Orthonormal basis: Frobenius norm and all other frequencies are unchanged."""
    coef = basis.T @ W
    new = coef.copy()
    for k, j in pairs:
        ck, cj = freq_columns([k]), freq_columns([j])
        new[ck], new[cj] = coef[cj], coef[ck]
    return basis @ new


def magswap_frequency_coefficients(W: np.ndarray, basis: np.ndarray,
                                   pairs: list[tuple[int, int]]) -> np.ndarray:
    """New W [p, d] where, for each pair (k, j), the (cos, sin) coefficient block of k is
    rescaled to the norm of j's block and vice versa. Directions stay with their frequency;
    power per frequency equals that of ``swap_frequency_coefficients``; Frobenius norm kept."""
    coef = basis.T @ W
    new = coef.copy()
    for k, j in pairs:
        ck, cj = freq_columns([k]), freq_columns([j])
        nk, nj = np.linalg.norm(coef[ck]), np.linalg.norm(coef[cj])
        new[ck], new[cj] = coef[ck] * (nj / nk), coef[cj] * (nk / nj)
    return basis @ new


def shrink_factor(power: np.ndarray, m: int) -> float:
    """Amplitude factor that removes the same power as banning the top-m frequencies."""
    top = np.sort(power)[::-1][:m].sum()
    return float(np.sqrt(1.0 - top / power.sum()))


def shrink_nonconstant(W: np.ndarray, basis: np.ndarray, factor: float) -> np.ndarray:
    """W with all non-constant DFT coefficients scaled by ``factor`` (constant row kept)."""
    coef = basis.T @ W
    coef[1:] *= factor
    return basis @ coef


def ban_projector(basis: np.ndarray, freqs) -> np.ndarray:
    """[p, p] projector onto the orthogonal complement of the banned frequencies."""
    B = basis[:, freq_columns(freqs)]
    return np.eye(basis.shape[0]) - B @ B.T


# --------------------------------------------------------------------------- #
# the run
# --------------------------------------------------------------------------- #
def _stored_final_W_E(seed: int, p: int) -> np.ndarray:
    path = ROOT / "training" / "runs" / STORED_RUN.format(seed=seed) / "model_final.pt"
    if not path.exists():
        raise FileNotFoundError(f"ban_destined needs the stored baseline model: {path}")
    state = torch.load(path, map_location="cpu", weights_only=True)
    return state["W_E"].numpy().astype(np.float64)[:p]


def _choose_ban(cond: str, W_E: np.ndarray, basis: np.ndarray, m: int, seed: int) -> list[int]:
    power = freq_power(W_E, basis)
    if cond == "ban_emerging":
        return top_frequencies(power, m)
    if cond == "ban_random":
        return random_frequencies(power, m, seed + RANDOM_SALT)
    raise ValueError(cond)


def run(a: argparse.Namespace) -> dict:
    cfg = get_config("arch25k", seed=a.seed, steps=a.steps, threads=a.threads)
    p = cfg.p
    exp_id = EXP_ID_BY_CONDITION.get(a.condition, EXP_ID)
    if a.split_seed is not None:     # EXP-014: data split from another seed, init from --seed
        exp_id = "EXP-014"
    run_id = f"{exp_id}_{a.condition}_t{a.t0}_m{a.m}_seed{a.seed}_thr{a.threads}"
    if a.split_seed is not None:
        run_id += f"_split{a.split_seed}"
    if a.split_file is not None:     # EXP-016: engineered train split from a .npy of flat indices a*p+b
        if a.split_seed is not None:
            raise SystemExit("--split-file and --split-seed are exclusive")
        exp_id = "EXP-016" if a.test_file is None else "EXP-018"
        run_id = f"{exp_id}_{a.condition}_seed{a.seed}_thr{a.threads}_{Path(a.split_file).stem}"
        if a.switch_split_file is not None:      # EXP-020: change the train set once at --switch-step
            if a.test_file is None or a.switch_step is None or a.switch_step < 1:
                raise SystemExit("--switch-split-file needs --test-file and --switch-step >= 1")
            exp_id = "EXP-020"
            run_id = (f"{exp_id}_{a.condition}_seed{a.seed}_thr{a.threads}_{Path(a.split_file).stem}"
                      f"_to_{Path(a.switch_split_file).stem}_at{a.switch_step}")
    elif a.test_file is not None or a.switch_split_file is not None:
        raise SystemExit("--test-file / --switch-split-file need --split-file")
    if a.split_value:                # EXP-023: position 1 gets its own attention value matrix
        exp_id = "EXP-023"
        run_id = run_id.replace(run_id.split("_")[0], exp_id, 1) + "_sv"
    out_dir = Path(a.out_root) / run_id
    if (out_dir / "result.json").exists() and not a.force:
        prev = json.loads((out_dir / "result.json").read_text())
        if prev.get("status") == "completed":
            print(f"[exp] {run_id} already completed; use --force to overwrite", flush=True)
            raise SystemExit(0)           # skip is not an error (EXP-020 queue stops on every other failure)
    out_dir.mkdir(parents=True, exist_ok=True)

    # identical order to grokverse.train.train(): threads, seed, data, model, optimizer
    torch.set_num_threads(cfg.threads)
    set_seed(cfg.seed)
    # make_dataset uses its own torch.Generator (seeded with cfg.seed), not the global RNG,
    # so a foreign split leaves the model init unchanged
    data = make_dataset(cfg if a.split_seed is None
                        else get_config("arch25k", seed=a.split_seed, steps=a.steps, threads=a.threads))
    if a.split_file is not None:
        raw = np.load(a.split_file)       # fail closed (Codex review 2026-09-26)
        n_expected = int(round(cfg.train_frac * p * p))
        if (raw.ndim != 1 or not np.issubdtype(raw.dtype, np.integer) or len(raw) != n_expected
                or len(np.unique(raw)) != len(raw) or raw.min() < 0 or raw.max() >= p * p):
            raise SystemExit(f"[exp] invalid split file {a.split_file}: need {n_expected} unique ints in [0, p*p)")
        tr = torch.from_numpy(raw.astype(np.int64))
        te = torch.from_numpy(np.setdiff1d(np.arange(p * p), tr.numpy()))
        if a.test_file is not None:       # EXP-018: common held-out test set instead of the complement
            rt = np.load(a.test_file)
            if (rt.ndim != 1 or not np.issubdtype(rt.dtype, np.integer) or len(rt) == 0
                    or len(np.unique(rt)) != len(rt) or rt.min() < 0 or rt.max() >= p * p
                    or np.intersect1d(rt, raw).size):
                raise SystemExit(f"[exp] invalid test file {a.test_file}: need unique ints in [0, p*p) disjoint from train")
            te = torch.from_numpy(np.sort(rt).astype(np.int64))
        data = {**data, "train_x": data["all_x"][tr], "train_y": data["all_y"][tr],
                "test_x": data["all_x"][te], "test_y": data["all_y"][te], "train_idx": tr, "test_idx": te}
    trx, try_, tex, tey = data["train_x"], data["train_y"], data["test_x"], data["test_y"]
    switch_idx = None
    if a.switch_split_file is not None:
        rs = np.load(a.switch_split_file)
        if (rs.ndim != 1 or not np.issubdtype(rs.dtype, np.integer) or len(rs) != len(data["train_idx"])
                or len(np.unique(rs)) != len(rs) or rs.min() < 0 or rs.max() >= p * p
                or np.intersect1d(rs, data["test_idx"].numpy()).size):
            raise SystemExit(f"[exp] invalid switch file {a.switch_split_file}: same size, unique, disjoint from test")
        switch_idx = torch.from_numpy(rs.astype(np.int64))
    model = build_model(cfg)
    if a.split_value:                # after the baseline init (identical weights), before the optimizer
        if cfg.arch != "transformer":
            raise SystemExit("--split-value needs the transformer")
        sys.path.insert(0, str(HERE.parent / "EXP-023-split-value"))
        from split_value import convert
        model = convert(model, a.seed)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay,
                            betas=(cfg.beta1, cfg.beta2))
    basis = fourier_basis(p)

    events: dict = {}
    if a.condition in INIT_CONDITIONS:   # numpy only: consumes no torch RNG, so data/weights match baseline
        W0 = model.W_E.detach().numpy().astype(np.float64)[:p]
        pw0 = freq_power(W0, basis)
        pairs = swap_pairs(pw0, a.m, a.seed + SWAP_SALT)
        swap_fn = (swap_frequency_coefficients if a.condition == "init_swap"
                   else magswap_frequency_coefficients)
        with torch.no_grad():
            model.W_E[:p] = torch.tensor(swap_fn(W0, basis, pairs), dtype=model.W_E.dtype)
        events[a.condition] = {"pairs": pairs, "power_before": pw0.tolist(),
                               "power_after": freq_power(
                                   model.W_E.detach().numpy().astype(np.float64)[:p], basis).tolist()}

    ban_from = 1 if a.condition == "ban_destined" else a.t0
    banned: list[int] | None = None
    proj: torch.Tensor | None = None
    if a.condition == "ban_destined":
        banned = top_frequencies(freq_power(_stored_final_W_E(a.seed, p), basis), a.m)
        proj = torch.tensor(ban_projector(basis, banned), dtype=model.W_E.dtype)

    dense = {"train_steps": [], "train_acc": [], "train_loss": [], "test_steps": [],
             "test_acc": [], "test_loss": [], "eval_every_train": cfg.eval_every_train,
             "eval_every_test": cfg.eval_every_test}
    spectra, spectra_steps = [], []
    res = {"exp_id": exp_id, "run_id": run_id, "status": "running",
           "condition": a.condition, "seed": a.seed, "t0": a.t0, "m": a.m,
           "ban_from_step": None if a.condition in ("baseline",) + INIT_CONDITIONS else ban_from,
           "amendment": "2026-09-25b: projected grad + exp_avg; shrink_matched control",
           "stop_after_generalization": a.stop_after_gen, "split_seed": a.split_seed, "split_file": a.split_file, "test_file": a.test_file, "switch_split_file": a.switch_split_file,
           "switch_step": a.switch_step, "split_value": a.split_value, "max_steps": a.steps,
           "config": cfg.to_dict(), "split_hash": split_hash(data["train_idx"]),
           "test_hash": split_hash(data["test_idx"]),
           "switch_hash": None if switch_idx is None else split_hash(switch_idx),
           "git_commit": git_commit(), "versions": lib_versions(),
           "platform": platform.platform(), "argv": sys.argv,
           "start_utc": datetime.now(timezone.utc).isoformat()}

    def dense_eval(step: int) -> None:
        if step % cfg.eval_every_train == 0:
            loss, acc = evaluate(model, trx, try_, p)
            dense["train_steps"].append(step); dense["train_acc"].append(acc); dense["train_loss"].append(loss)
        if step % cfg.eval_every_test == 0:
            loss, acc = evaluate(model, tex, tey, p)
            dense["test_steps"].append(step); dense["test_acc"].append(acc); dense["test_loss"].append(loss)

    def spectrum(step: int) -> None:
        spectra_steps.append(step)
        spectra.append(freq_power(model.W_E.detach().numpy().astype(np.float64)[:p], basis))

    def write(status: str) -> None:
        res.update({"status": status, "steps_completed": step, "banned_freqs": banned,
                    "events": events, "dense": dense,
                    "transitions": all_transitions(dense) if dense["test_steps"] else None,
                    "elapsed_s": round(time.perf_counter() - t_start, 1),
                    "sec_per_step": round((time.perf_counter() - t_start) / max(step, 1), 5)})
        np.save(out_dir / "spectra.npy", np.asarray(spectra))
        np.save(out_dir / "spectra_steps.npy", np.asarray(spectra_steps))
        (out_dir / "result.json").write_text(json.dumps(res, indent=1))

    step, t_start = 0, time.perf_counter()
    dense_eval(0); spectrum(0)
    gen_thr = THRESHOLD_SETS["primary"][1]
    stop_at = a.steps
    for step in range(1, a.steps + 1):
        model.train()
        loss = F.cross_entropy(model.logits_last(trx)[:, :p], try_)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        if proj is not None and step > ban_from:   # amendment 2026-09-25: projected gradient
            with torch.no_grad():
                model.W_E.grad[:p] = proj @ model.W_E.grad[:p]
        opt.step()
        if a.condition not in ("baseline",) + INIT_CONDITIONS and step == ban_from:
            W_now = model.W_E.detach().numpy().astype(np.float64)[:p]
            if banned is None and a.condition != "shrink_matched":
                banned = _choose_ban(a.condition, W_now, basis, a.m, a.seed)
                proj = torch.tensor(ban_projector(basis, banned), dtype=model.W_E.dtype)
            events["pre_ban_acc"] = {"train": evaluate(model, trx, try_, p)[1],
                                     "test": evaluate(model, tex, tey, p)[1]}
            events["power_at_ban"] = freq_power(W_now, basis).tolist()
            if a.condition == "shrink_matched":     # one-time, energy matched to a top-m ban
                factor = shrink_factor(np.asarray(events["power_at_ban"]), a.m)
                with torch.no_grad():
                    model.W_E[:p] = torch.tensor(shrink_nonconstant(W_now, basis, factor),
                                                 dtype=model.W_E.dtype)
                events["shrink_factor"] = factor
                events["post_ban_acc"] = {"train": evaluate(model, trx, try_, p)[1],
                                          "test": evaluate(model, tex, tey, p)[1]}
        if proj is not None and step >= ban_from:
            with torch.no_grad():
                model.W_E[:p] = proj @ model.W_E[:p]
                if step == ban_from:                # first-moment state into the allowed subspace
                    m1 = opt.state[model.W_E]["exp_avg"]
                    m1[:p] = proj @ m1[:p]
            if step == ban_from:
                events["post_ban_acc"] = {"train": evaluate(model, trx, try_, p)[1],
                                          "test": evaluate(model, tex, tey, p)[1]}
        if switch_idx is not None and step == a.switch_step:     # EXP-020: new train set from the next step on
            old = data["train_idx"].numpy()
            sub = {"G_minus_F": np.setdiff1d(switch_idx.numpy(), old), "F_minus_G": np.setdiff1d(old, switch_idx.numpy()),
                   "F_and_G": np.intersect1d(old, switch_idx.numpy())}    # Codex review: new pairs separately
            events["switch"] = {"step": step, "train_acc_before": evaluate(model, trx, try_, p)[1],
                                "new_train_hash": split_hash(switch_idx),
                                **{f"acc_{k}": evaluate(model, data["all_x"][torch.from_numpy(v)],
                                                        data["all_y"][torch.from_numpy(v)], p)[1]
                                   for k, v in sub.items() if len(v)},
                                **{f"n_{k}": int(len(v)) for k, v in sub.items()}}
            trx, try_ = data["all_x"][switch_idx], data["all_y"][switch_idx]
        dense_eval(step)
        if step % SPECTRUM_EVERY == 0:
            spectrum(step)
        if ("generalization_step" not in events and step % cfg.eval_every_test == 0
                and dense["test_acc"][-1] >= gen_thr):
            events["generalization_step"] = step
            stop_at = min(a.steps, step + a.stop_after_gen)
        if step % PARTIAL_WRITE_EVERY == 0:
            write("running")
        if step >= stop_at:
            break
    if step % SPECTRUM_EVERY:
        spectrum(step)
    final_power = freq_power(model.W_E.detach().numpy().astype(np.float64)[:p], basis)
    res["final_top_m_freqs"] = top_frequencies(final_power, a.m)
    res["final_acc"] = {"train": evaluate(model, trx, try_, p)[1],
                        "test": evaluate(model, tex, tey, p)[1]}
    res["end_utc"] = datetime.now(timezone.utc).isoformat()
    if a.save_model:
        torch.save(model.state_dict(), out_dir / "model_final.pt")
    write("completed")
    print(f"[exp] {run_id} completed: steps {step}, gen {events.get('generalization_step')}, "
          f"banned {banned}, final top-{a.m} {res['final_top_m_freqs']}, "
          f"{res['sec_per_step']} s/step", flush=True)
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description="EXP-001 training-time frequency ban")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--condition", choices=CONDITIONS, required=True)
    ap.add_argument("--t0", type=int, default=2000, help="first banned step (not ban_destined)")
    ap.add_argument("--m", type=int, default=5, help="number of banned frequencies")
    ap.add_argument("--steps", type=int, default=15000, help="hard step cap")
    ap.add_argument("--stop-after-gen", type=int, default=2000,
                    help="continue this many steps after the generalization crossing, then stop")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--out-root", default=str(HERE / "raw"))
    ap.add_argument("--split-seed", type=int, default=None,
                    help="EXP-014: take the train/test split of this seed (init stays from --seed)")
    ap.add_argument("--split-file", default=None,
                    help="EXP-016: .npy with flat train indices a*p+b (test = complement)")
    ap.add_argument("--test-file", default=None,
                    help="EXP-018: .npy with flat test indices (disjoint from --split-file) instead of the complement")
    ap.add_argument("--switch-split-file", default=None,
                    help="EXP-020: .npy train set that replaces --split-file after --switch-step (needs --test-file)")
    ap.add_argument("--switch-step", type=int, default=None, help="EXP-020: last step trained on --split-file")
    ap.add_argument("--split-value", action="store_true",
                    help="EXP-023: position 1 gets its own attention value matrix W_V1 (separate generator)")
    ap.add_argument("--save-model", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if a.t0 < 1:
        ap.error("--t0 must be >= 1 (the loop starts at step 1; t0=0 would silently ban nothing)")
    run(a)


if __name__ == "__main__":
    main()
