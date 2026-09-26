"""Check of the EXP-022 functional measures on a stored study model (seed 0, 25k): the 'nanda' rule must reproduce the
study's stored key set; keep-only/drop ablations must run. Inference only; run through guarded_run.py."""
import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze as a  # noqa: E402

ROOT = HERE.parents[2]
run = ROOT / "training/runs/txf_add_p113_wd1.0_frac0.3_seed0_arch25k"
cfg = a.get_config("arch25k", seed=0)
model = a.build_model(cfg)
state = torch.load(run / "model_final.pt", map_location="cpu")
model.load_state_dict(state)
kf = a.select_from_arrays("nanda", a.P, W_L=a.neuron_logit_map({k: v.numpy() for k, v in state.items()}, cfg))
stored = json.loads((run / "analysis/key_frequencies/step025000.json").read_text())["results"]
stored = stored if isinstance(stored, dict) else eval(stored, {"__builtins__": {}})
print("nanda:", kf["key_frequencies"], "stored:", sorted(stored["primary_key_frequencies"]))
data = a.make_dataset(cfg)
W0 = model.W_E.detach().clone()
for name, freqs in (("keep top-1 (15)", [15]), ("keep all nanda", kf["key_frequencies"])):
    keep = a.B[:, [0, *a.fb.freq_columns(freqs)]]
    with torch.no_grad():
        model.W_E[:a.P] = torch.tensor(keep @ keep.T, dtype=W0.dtype) @ W0[:a.P]
    print(name, "test acc", round(a.evaluate(model, data["test_x"], data["test_y"], a.P)[1], 4))
    with torch.no_grad():
        model.W_E.copy_(W0)
print("baseline test acc", round(a.evaluate(model, data["test_x"], data["test_y"], a.P)[1], 4))
