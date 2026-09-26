"""EXP-027b analysis (Nachtrag b): same statistic and gates as analyze.py, seeds 15-19, widths 64-512, all from raw_b."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("a27", HERE / "analyze.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
A.WIDTHS = (512, 256, 128, 64)
A.SEEDS = (15, 16, 17, 18, 19)


def path(w: int, s: int) -> Path:
    return HERE / "raw_b" / (f"EXP-026_a0_seed{s}_F" if w == 512 else f"EXP-026_a0_w{w}_seed{s}_F") / "result.json"


A.path = path
_orig_valid = A.valid
A.valid = lambda r, w, s: _orig_valid(r, w, s) and r["args"]["switch_step"] == -1
A.HERE = HERE / "b_out"
A.HERE.mkdir(exist_ok=True)
A.main()
