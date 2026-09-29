"""resume_wrapper.py - run lm_stage2.py with a fixed RNG restore, without changing lm_stage2.py.

Why (session 49, 2026-09-29): lm_stage2.py loads its checkpoint with map_location=cuda, which moves the saved CPU
RNG ByteTensors onto the GPU; torch.set_rng_state / torch.cuda.set_rng_state then raise
"RNG state must be a torch.ByteTensor". The checkpoint self-test ran on CPU and did not catch it.
Editing lm_stage2.py would change its sha256, which is part of the run id, so the pilot's checkpoints could not be
resumed. This wrapper moves the state back to the CPU before restoring it (same values) and runs the unchanged
script via runpy, so __file__ and therefore the run id stay the same.

Usage: <python> lab/experiments/EXP-105-lm-ladder-stage2/resume_wrapper.py <lm_stage2.py arguments>
"""
import runpy
import sys
from pathlib import Path

import torch

_set_cpu, _set_cuda = torch.set_rng_state, torch.cuda.set_rng_state
torch.set_rng_state = lambda state: _set_cpu(state.cpu())
torch.cuda.set_rng_state = lambda state, device="cuda": _set_cuda(state.cpu(), device)

script = Path(__file__).resolve().parent / "lm_stage2.py"
sys.argv = [str(script)] + sys.argv[1:]
runpy.run_path(str(script), run_name="__main__")
