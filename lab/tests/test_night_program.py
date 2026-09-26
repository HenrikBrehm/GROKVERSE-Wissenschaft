"""Control-flow tests for lab/tools/night_program.py (session 13): no job is started; Night.jobs is replaced by a script.
Checks: guard refusal (exit 3) stops everything; a failed experiment does not stop the next one and gives exit 1;
a failed GPU-001 stops all GPU experiments; an analysis never runs after failed runs.

Run through the guard in the window:  python lab/tools/guarded_run.py -- python lab/tests/test_night_program.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lab" / "tools"))
import night_program as npg  # noqa: E402

npg.shutil.rmtree = lambda *args, **kw: None   # smoke() would delete real raw_smoke directories


def make(script: dict[str, int], log: Path) -> tuple[npg.Night, list[str]]:
    """Night whose jobs() returns script[tag] (default 0) and records every tag; GPU-001 treated as not yet passed."""
    calls: list[str] = []
    night = npg.Night(log)

    def jobs(tag: str, cmds: list, workers: int, mm: float) -> int:
        calls.append(tag)
        rc = script.get(tag, 0)
        if rc == 3:
            raise npg.Refused(tag)
        return rc
    night.jobs = jobs

    def gpu001_stub() -> None:        # the real gpu001() deletes/creates GPU-001 directories: never in a test
        night.must("gpu001_equivalence", ["stub"])
        night.J = 4
    night.gpu001 = gpu001_stub
    return night, calls


def test_refusal_stops_all(log: Path) -> None:
    night, calls = make({"EXP-046_main": 3}, log / "a")
    assert night.run(["GPU-001", "EXP-046", "EXP-047"]) == 3
    assert "EXP-046_main_analysis" not in calls and not any(c.startswith("EXP-047") for c in calls), calls


def test_failure_continues(log: Path) -> None:
    night, calls = make({"EXP-046_main": 1}, log / "b")
    assert night.run(["GPU-001", "EXP-046", "EXP-047"]) == 1
    assert "EXP-046_main_analysis" not in calls and "EXP-046_random" not in calls, calls
    assert "EXP-047_main" in calls and "EXP-047_main_analysis" in calls, calls
    assert night.status["experiments"]["EXP-046"]["state"].startswith("failed")
    assert night.status["experiments"]["EXP-047"]["state"] == "ok"


def test_gate(log: Path) -> None:
    night, calls = make({"gpu001_equivalence": 1}, log / "c")
    assert night.run(["GPU-001", "EXP-046"]) == 1
    assert not any(c.startswith("EXP-046") for c in calls), calls


def test_unexpected_error(log: Path) -> None:
    night, calls = make({}, log / "d")
    night.exp046 = lambda: (_ for _ in ()).throw(KeyError("boom"))
    rc = night.run(["GPU-001", "EXP-046", "EXP-047"])
    assert rc == 1 and "unexpected KeyError" in night.status["experiments"]["EXP-046"]["state"], night.status
    assert "EXP-047_main_analysis" in calls


def main() -> int:
    with tempfile.TemporaryDirectory() as t:
        log = Path(t)
        for fn in (test_refusal_stops_all, test_failure_continues, test_gate, test_unexpected_error):
            fn(log)
            print(f"[test_night_program] {fn.__name__} ok", flush=True)
    print("[test_night_program] all ok", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
