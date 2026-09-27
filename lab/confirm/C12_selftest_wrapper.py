"""Run the C1 / C2 selftests without touching gated files (session 32; corrected session 35 before its first run).

rank_tools.selftest(), C1_analyze.selftest() and C2_analyze.selftest() use rng.permutation(5.0); current numpy rejects a float there
(AxisError), so C1_analyze.py --selftest and C2_analyze.py --selftest fail although the analysis code is unaffected. rank_tools.py,
C1_analyze.py and C2_analyze.py are hashed by the C1-C4 code gates (C4 is bound to the frozen P2f manifest 15539d8), so they must NOT be
edited. This wrapper patches only in-memory copies of the three selftest functions and then runs them; the analysis functions they call
are the unchanged ones.

Session 35 (static reading, before any run): permutation(5) alone is not enough in rank_tools.selftest. There y = 2 x + c with x, c
permutations of 0..4 has a tie in 57 % of the blocks (exact count 8160/14400), and cranks() raises TieError on ties, so the 50-block
check would fail with probability 1 - 0.433**50. rank_tools gets continuous draws rng.random(5) instead (no ties; the checks keep their
meaning: y follows x and c jointly, and y = c gives x no weight). C1/C2 build y = permutation + Gaussian noise, so permutation(5)
(integer values, no ties within a draw) suffices there.
  python lab/tools/guarded_run.py -- python lab/confirm/C12_selftest_wrapper.py
"""
import importlib.util
import inspect
import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rank_tools as rt  # noqa: E402


def patched(fn, old: str, new: str, count: int, globs: dict):
    """Recompile fn from its source with old -> new (exactly `count` occurrences), in the module's own globals."""
    src = textwrap.dedent(inspect.getsource(fn))
    assert src.count(old) == count, f"{fn.__module__}.{fn.__name__} changed; re-check this wrapper"
    ns: dict = {}
    exec(compile(src.replace(old, new), f"{fn.__module__}_selftest_patched", "exec"), globs, ns)
    return ns[fn.__name__]


rt.selftest = patched(rt.selftest, "rng.permutation(5.0)", "rng.random(5)", 4, rt.__dict__)

for name in ("C1_analyze", "C2_analyze"):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    assert mod.rt is rt, f"{name} imported another rank_tools"
    patched(mod.selftest, "rng.permutation(5.0)", "rng.permutation(5)", 3, mod.__dict__)()
    print(f"[C12 wrapper] {name} selftest ok (selftests patched in memory only)", flush=True)
