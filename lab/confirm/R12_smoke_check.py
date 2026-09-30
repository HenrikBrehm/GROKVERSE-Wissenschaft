"""R12 smoke (session 57): the two real smoke runs (seed 4299, unit-0 splits) through the R12 loader measure() (technical check)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import confirm_r12 as r  # noqa: E402

S = r.LAB / "confirm" / "r12_smoke"
for task, p, arm in (("add", 97, "E2_0"), ("mul", 113, "D_1")):
    cmd = ["x", r.FB, "--seed", "4299", "--threads", "1", "--device", "cuda", "--p", str(p), "--task", task,
           "--split-file", f"lab/confirm/r12_smoke/splits/smoke_{task}{p}_{arm}.npy"]
    d = S / "raw" / r.expected_run_id(cmd)
    m = r.measure(d, 4299, task, p, "cuda", r.CAP, S / "splits" / f"smoke_{task}{p}_{arm}.npy", S / "splits" / f"smoke_{task}{p}_test.npy",
                  r.arm_targets(task, p, 0, arm))
    assert isinstance(m, dict), m
    print(task, p, arm, "loader ok; dense grid valid; event observed:", m["event"][1], "; we_share_250 is None:", m["we_share_250"] is None)
    bad = r.measure(d, 4299, task, p, "cuda", r.CAP, S / "splits" / f"smoke_{task}{p}_test.npy", S / "splits" / f"smoke_{task}{p}_test.npy",
                    r.arm_targets(task, p, 0, arm))
    assert isinstance(bad, str), "wrong split file accepted"
print("R12 smoke ok")
