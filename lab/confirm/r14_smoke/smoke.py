"""R14 smoke (session 67, before freezing): one real 2000-step trainer run outside the block (seed 4499, not reserved), R14
construction; checks the run id rule, config fields and the snapshot list. Not part of the confirmation."""
import shlex, subprocess, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "lab/tools")
import confirm_r14 as r
from result_loader import Expect, load_run
sm = Path("lab/confirm/r14_smoke")
idx, T = r.build(4499, "F")
sp = sm / "splits" / "r14_add307_seed4499_F.npy"
if not sp.exists():
    np.save(sp, idx.astype(np.int64))
man = {**r.REGISTERED, "python": ".venv-gpu/Scripts/python.exe", "seeds": []}
cmd = r.job(man, 4499, "F").replace("lab/confirm/r14_splits/", "lab/confirm/r14_smoke/splits/").replace(
    "--out-root lab/confirm/r14_raw", "--out-root lab/confirm/r14_smoke/raw").replace("--steps 30000", "--steps 2000")
args = shlex.split(cmd)
if "--run-trainer" in sys.argv:
    sys.exit(subprocess.call(args))
d = sm / "raw" / r.expected_run_id(args)
print("dir exists:", d.exists(), d.name)
L = load_run(d, Expect(seed=4499, device="cuda", max_steps=2000, min_steps_completed=1, split_file=sp,
                       config={"p": 307, "task": "add", "arch": "transformer", "train_frac": 0.1}, snapshots_at=(2000,)))
print("load:", L.status, L.reason)
print("snapshot shape:", L.snapshot(2000).shape if L.status == "ok" else None, "steps:", np.load(d / "we_snapshot_steps.npy").tolist()[:6])
print("gen:", ((L.res.get("transitions") or {}).get("primary") or {}).get("generalization", {}).get("first_crossing_step"))
