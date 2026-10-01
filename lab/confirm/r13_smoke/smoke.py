"""R13 smoke (session 67, before freezing): one real trainer run outside the block (seed 4399, not reserved) through the R13 loader
fields; checks run id, Expect, optimizer fields, spectra at 250/2000. Not part of the confirmation."""
import json, shlex, subprocess, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, "lab/tools")
import confirm_r13 as r
from result_loader import load_run
smoke = Path("lab/confirm/r13_smoke")
idx, T = r.build(4399, "F")
sp = smoke / "splits" / "r13_c01_seed4399_F.npy"
if not sp.exists():
    np.save(sp, idx.astype(np.int64))
man = {**r.REGISTERED, "python": ".venv-gpu/Scripts/python.exe", "seeds": {}}
cmd = r.job(man, "c01", 4399, "F").replace("lab/confirm/r13_splits/", "lab/confirm/r13_smoke/splits/").replace(
    "--out-root lab/confirm/r13_raw", "--out-root lab/confirm/r13_smoke/raw")
args = shlex.split(cmd)
if "--run-trainer" in sys.argv:
    sys.exit(subprocess.call(args))
d = smoke / "raw" / r.expected_run_id(args)
print("dir exists:", d.exists(), d.name)
L = load_run(d, r.expect(man, 4399, sp))
print("load:", L.status, L.reason)
res = L.res
print("optimizer", res.get("optimizer"), res.get("sgd_lr"), res.get("sgd_momentum"), (res["events"].get("sgd_clip") or {}).get("max_norm"))
print("fp split sha ok:", res["fingerprint_fields"].get("split_file_sha256") == r.sha(sp))
print("spectra shapes:", np.asarray(L.spectrum(2000)).shape, np.asarray(L.spectrum(250)).shape, "final_acc", res.get("final_acc"))
