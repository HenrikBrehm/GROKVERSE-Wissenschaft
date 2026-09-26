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


def test_timeout_is_refusal(log: Path) -> None:
    """Session 17: a job cut by the guard's time limit (124) stops the program like a refusal instead of failing it."""
    real = npg.pq.run_queue

    def fake_queue(results: list[int]):
        def run_queue(cmds, workers, mm, log_dir):
            log_dir.mkdir(parents=True, exist_ok=True)
            (log_dir / "summary.json").write_text(npg.json.dumps(
                {"results": [{"job": i, "exit_code": rc} for i, rc in enumerate(results, 1)]}), encoding="utf-8")
            return 0 if all(rc == 0 for rc in results) else 1
        return run_queue
    try:
        night = npg.Night(log / "e")
        npg.pq.run_queue = fake_queue([0, 124])
        try:
            night.jobs("cut", [["x"]], 1, 5)
            raise AssertionError("124 was not turned into a refusal")
        except npg.Refused:
            pass
        npg.pq.run_queue = fake_queue([0, 1])                 # an ordinary failure stays a failure
        assert night.jobs("fail", [["x"]], 1, 5) == 1
        assert not npg.Night.cut_by_time_limit(log / "missing")
    finally:
        npg.pq.run_queue = real


def test_gpu001_stage_skip(log: Path) -> None:
    """Session 17: a resumed GPU-001 redoes only the stages without a sealed PASS."""
    night = npg.Night(log / "f")
    ran: list[str] = []
    passed = {"regression": True, "equivalence": False, "throughput": False}
    night.passed = lambda mode: passed[mode]
    night.jobs = lambda tag, cmds, w, mm: ran.append(tag) or 0
    night.gpu001_regression = lambda: ran.append("regression")
    night.gpu001_equivalence = lambda: ran.append("equivalence")
    night.gpu001_throughput = lambda: ran.append("throughput")
    night.best_J = lambda: 2
    night.gpu001()
    assert ran == ["gpu001_env", "equivalence", "throughput"] and night.J == 2, ran


def main() -> int:
    with tempfile.TemporaryDirectory() as t:
        log = Path(t)
        for fn in (test_refusal_stops_all, test_failure_continues, test_gate, test_unexpected_error,
                   test_timeout_is_refusal, test_gpu001_stage_skip):
            fn(log)
            print(f"[test_night_program] {fn.__name__} ok", flush=True)
    print("[test_night_program] all ok", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
