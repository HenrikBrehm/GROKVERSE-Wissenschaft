"""GPU-001 stage 0 "components" (Astra point 9, rule 18b2). UNTESTED (written out of window, session 18).

Astra 9: the native Windows ROCm path stays experimental until forward, backward, AdamW, repetition and a long run agree
with the CPU. The equivalence stage (compare.py) covers the long run (3 x 2000 steps incl. generalization); this stage
checks the pieces one by one, in ONE process with ONE torch build (the GPU venv), so only the device differs:

  C1 forward   logits of the full train batch: max |cpu - gpu| / max |cpu| <= 1e-4; loss rel. diff <= 1e-4
  C2 backward  every parameter: ||g_cpu - g_gpu|| / ||g_cpu|| <= 1e-3
  C3 AdamW     one full-batch step from identical weights and gradients (the CPU gradients are copied to the GPU, so the
               optimizer alone is compared): every parameter ||dθ_cpu - dθ_gpu|| / ||dθ_cpu|| <= 1e-3
  C4 short     50 full training steps on each device: max rel. train-loss diff over steps 1..50 <= max(1e-2, 10 x the
               same diff between CPU runs with 1 and 4 threads, i.e. the CPU's own reduction-order noise)
  C5 repeat    the same 200 GPU steps twice from the same init: rel. train-loss diff at step 200 <= 1e-3 and parameters
               max |Δ| / max |θ| <= 1e-3 (bitwise equality is reported, not required: ROCm embedding backward may use atomics)
Thresholds fixed before any GPU run (session 18, 2026-09-27 00:45 Berlin, measured). Model/data exactly as freq_ban.py
(arch25k, seed 10, EXP-016 split seed10 eps2.0, lr/wd/betas from the config), fp32.

Run (window only):  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/GPU-001-equivalence/components.py
Writes verdict_components.json (with the GPU-001 seal); exit 1 if a criterion fails.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "training"))
sys.path.insert(0, str(HERE))

from compare import seal  # noqa: E402
from grokverse.config import get_config  # noqa: E402
from grokverse.data import make_dataset  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.seed import set_seed  # noqa: E402

SEED = 10
SPLIT = ROOT / "lab/experiments/EXP-016-engineered-split/splits/split_seed10_eps2.0.npy"
TOL = {"C1_logits": 1e-4, "C1_loss": 1e-4, "C2_grad": 1e-3, "C3_update": 1e-3, "C4_loss": 1e-2,
       "C5_loss": 1e-3, "C5_param": 1e-3}
SHORT_STEPS, REPEAT_STEPS = 50, 200


def setup() -> tuple:
    cfg = get_config("arch25k", seed=SEED, steps=REPEAT_STEPS, threads=1)
    torch.set_num_threads(1)
    set_seed(cfg.seed)
    data = make_dataset(cfg)
    tr = torch.from_numpy(np.load(SPLIT).astype(np.int64))
    x, y = data["all_x"][tr], data["all_y"][tr]
    model = build_model(cfg)            # built on the CPU, as in freq_ban.py
    return cfg, model, x, y


def make_opt(cfg, model: torch.nn.Module) -> torch.optim.AdamW:
    return torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay, betas=(cfg.beta1, cfg.beta2))


def loss_of(model: torch.nn.Module, x: torch.Tensor, y: torch.Tensor, p: int) -> tuple[torch.Tensor, torch.Tensor]:
    logits = model.logits_last(x)[:, :p]
    return logits, F.cross_entropy(logits, y)


def rel(a: torch.Tensor, b: torch.Tensor) -> float:
    a, b = a.detach().double().cpu(), b.detach().double().cpu()
    return float((a - b).norm() / max(float(a.norm()), 1e-30))


def train(cfg, model: torch.nn.Module, x: torch.Tensor, y: torch.Tensor, steps: int) -> list[float]:
    opt, losses = make_opt(cfg, model), []
    for _ in range(steps):
        _, loss = loss_of(model, x, y, cfg.p)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        losses.append(float(loss))
    return losses


def main() -> None:
    if not torch.cuda.is_available():
        raise SystemExit("[components] torch.cuda.is_available() is False")
    gpu = torch.device("cuda")
    cfg, m_cpu, x, y = setup()
    init = copy.deepcopy(m_cpu.state_dict())
    m_gpu = copy.deepcopy(m_cpu).to(gpu)
    xg, yg = x.to(gpu), y.to(gpu)
    res: dict = {"torch": torch.__version__, "hip": torch.version.hip, "device_name": torch.cuda.get_device_name(0),
                 "tolerances": TOL}

    # C1 forward, C2 backward
    lc, loss_c = loss_of(m_cpu, x, y, cfg.p)
    lg, loss_g = loss_of(m_gpu, xg, yg, cfg.p)
    c1_logits = float((lc.detach() - lg.detach().cpu()).abs().max() / lc.detach().abs().max())
    c1_loss = abs(float(loss_c) - float(loss_g)) / abs(float(loss_c))
    loss_c.backward()
    loss_g.backward()
    grads = {n: rel(pc.grad, pg.grad) for (n, pc), (_, pg) in zip(m_cpu.named_parameters(), m_gpu.named_parameters())}
    res["C1"] = {"logits_rel_max": c1_logits, "loss_rel": c1_loss,
                 "pass": c1_logits <= TOL["C1_logits"] and c1_loss <= TOL["C1_loss"]}
    res["C2"] = {"grad_rel_by_param": grads, "max": max(grads.values()), "pass": max(grads.values()) <= TOL["C2_grad"]}

    # C3 one AdamW step, same gradients on both devices (CPU gradients copied to the GPU)
    for pc, pg in zip(m_cpu.parameters(), m_gpu.parameters()):
        pg.grad = pc.grad.detach().clone().to(gpu)
    before = [q.detach().clone() for q in m_cpu.parameters()]
    make_opt(cfg, m_cpu).step()
    make_opt(cfg, m_gpu).step()
    upd = {n: rel(pc.detach() - b0, pg.detach().cpu() - b0)
           for (n, pc), (_, pg), b0 in zip(m_cpu.named_parameters(), m_gpu.named_parameters(), before)}
    res["C3"] = {"update_rel_by_param": upd, "max": max(upd.values()), "pass": max(upd.values()) <= TOL["C3_update"]}

    # C4 50 training steps on each device from the same init
    def fresh(dev: torch.device) -> torch.nn.Module:
        m = copy.deepcopy(m_cpu)
        m.load_state_dict(init)
        return m.to(dev)
    l_cpu = np.asarray(train(cfg, fresh(torch.device("cpu")), x, y, SHORT_STEPS))
    l_gpu = np.asarray(train(cfg, fresh(gpu), xg, yg, SHORT_STEPS))
    torch.set_num_threads(4)            # reference noise: the same CPU run with another reduction order (4 threads)
    try:
        l_cpu4 = np.asarray(train(cfg, fresh(torch.device("cpu")), x, y, SHORT_STEPS))
    finally:
        torch.set_num_threads(1)
    r4 = np.abs(l_gpu - l_cpu) / np.abs(l_cpu)
    r4ref = np.abs(l_cpu4 - l_cpu) / np.abs(l_cpu)
    lim4 = max(TOL["C4_loss"], 10 * float(r4ref.max()))   # GPU may not be worse than 10x CPU reduction-order noise
    res["C4"] = {"max_rel_loss_diff": float(r4.max()), "rel_at_step": {s: float(r4[s - 1]) for s in (1, 10, 50)},
                 "cpu_thr4_vs_thr1_max_rel": float(r4ref.max()), "limit": lim4, "pass": float(r4.max()) <= lim4}

    # C5 repeat on the GPU
    ma, mb = fresh(gpu), fresh(gpu)
    la, lb = train(cfg, ma, xg, yg, REPEAT_STEPS), train(cfg, mb, xg, yg, REPEAT_STEPS)
    loss5 = abs(la[-1] - lb[-1]) / abs(la[-1])
    pmax = max(float((pa - pb).abs().max() / pa.abs().max()) for pa, pb in zip(ma.parameters(), mb.parameters()))
    bitwise = all(torch.equal(pa, pb) for pa, pb in zip(ma.parameters(), mb.parameters()))
    res["C5"] = {"loss_rel_at_200": loss5, "param_rel_max": pmax, "bitwise_equal": bitwise,
                 "pass": loss5 <= TOL["C5_loss"] and pmax <= TOL["C5_param"]}
    res["cuda_max_mem_mb"] = torch.cuda.max_memory_allocated() / 2**20

    ok = all(res[k]["pass"] for k in ("C1", "C2", "C3", "C4", "C5"))
    res["pass"] = bool(ok)
    res["seal"] = seal()
    (HERE / "verdict_components.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps({k: (v["pass"] if isinstance(v, dict) and "pass" in v else v) for k, v in res.items()}, indent=1))
    print(f"[gpu001] components: {'PASS' if ok else 'FAIL'}", flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
