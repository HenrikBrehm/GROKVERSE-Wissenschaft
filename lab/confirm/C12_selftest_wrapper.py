"""Run the C1 / C2 selftests without touching gated files (session 32).

rank_tools.selftest() uses rng.permutation(5.0); current numpy rejects a float there (AxisError), so C1_analyze.py --selftest and
C2_analyze.py --selftest fail although the analysis code is unaffected. rank_tools.py is hashed by the C1-C4 code gates (C4 is bound to
the frozen P2f manifest 15539d8), so it must NOT be edited. This wrapper patches only the in-memory copy of rank_tools.selftest
(permutation(5.0) -> permutation(5), same values) and then runs the unchanged C1 and C2 selftests.
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

src = textwrap.dedent(inspect.getsource(rt.selftest))
assert src.count("permutation(5.0)") == 4, "rank_tools.selftest changed; re-check this wrapper"
ns: dict = {}
exec(compile(src.replace("permutation(5.0)", "permutation(5)"), "rank_tools_selftest_patched", "exec"), rt.__dict__, ns)
rt.selftest = ns["selftest"]

for name in ("C1_analyze", "C2_analyze"):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.rt is rt, f"{name} imported another rank_tools"
    mod.selftest()
    print(f"[C12 wrapper] {name} selftest ok (rank_tools.selftest patched in memory only)", flush=True)
