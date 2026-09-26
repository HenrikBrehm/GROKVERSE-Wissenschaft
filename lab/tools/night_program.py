#!/usr/bin/env python3
"""night_program.py - the GPU night queue as one Python program (Astra review point 11, session 13). UNTESTED.

Replaces lab/experiments/queue_gpu_s11.sh and its sub-queues (kept as history). Every job - runs, smoke tests,
selftests, analyses - goes through lab/tools/parallel_queue.py and therefore through guarded_run.py. Rules:
  * exit 3 of any job (guard: window, session deadline, STOP) stops the whole program with exit 3, no further starts;
  * an analysis runs only if all runs it evaluates finished with exit 0 ("Auswertungen nur nach erfolgreichen Läufen");
  * a failed experiment is recorded and the program continues with the next one; the program then exits 1;
  * GPU-001 gates everything: without regression, equivalence and throughput PASS no GPU experiment starts.
Completed runs are skipped by the trainers (fingerprint check in freq_ban.py), so resume = rerun the same command.
Status after every experiment: <log-dir>/night_status.json. One instance at a time (lock file with PID).

Usage (project root):
    python lab/tools/night_program.py [--experiments GPU-001,EXP-043,...] [--log-dir DIR]
    python lab/tools/night_program.py --check-smoke EXP-043      # internal: smoke-record checks (run as a guarded job)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import parallel_queue as pq  # noqa: E402

R = "lab/experiments"
GPY = ".venv-gpu/Scripts/python.exe"
PY = "python"
FB = f"{R}/EXP-001-freq-ban/freq_ban.py"
G1 = f"{R}/GPU-001-equivalence"
S16 = f"{R}/EXP-016-engineered-split/splits"
DEFAULT_ORDER = ("GPU-001", "EXP-043", "EXP-046", "EXP-047", "EXP-048", "EXP-049", "EXP-044", "EXP-045")
EXP_DIR = {"EXP-043": "EXP-043-generalize-steering", "EXP-044": "EXP-044-generalize-lockin",
           "EXP-045": "EXP-045-mlp-steering", "EXP-046": "EXP-046-dihedral-steering",
           "EXP-047": "EXP-047-marginal-control", "EXP-048": "EXP-048-intadd-steering",
           "EXP-049": "EXP-049-width-steering", "EXP-050": "EXP-050-phase-dissociation"}
LOCK = ROOT / "lab" / "runner" / "night_program.lock"


class Refused(Exception):
    """A guard refusal (exit 3): stop everything."""


class Failed(Exception):
    """This experiment failed (technically); continue with the next one."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Night:
    def __init__(self, log_dir: Path, dry: bool = False) -> None:
        self.log = log_dir
        self.dry = dry                  # --dry-run: walk the program, print the jobs, run nothing
        self.status: dict = {"started_utc": now(), "experiments": {}}
        self.J = 1

    # -- job helpers -------------------------------------------------------------------------------------------
    def jobs(self, tag: str, cmds: list[list[str]], workers: int, min_minutes: float) -> int:
        if self.dry:
            print(f"[dry] {tag}: {len(cmds)} job(s), workers {workers}, min {min_minutes}; first: {' '.join(cmds[0])}")
            if len(cmds) > 1:
                print(f"[dry]   last: {' '.join(cmds[-1])}")
            return 0
        rc = pq.run_queue(cmds, workers, min_minutes, self.log / tag)
        if rc == pq.EXIT_REFUSED:
            raise Refused(tag)
        return rc

    def must(self, tag: str, cmd: list[str], min_minutes: float = 2) -> None:
        if self.jobs(tag, [cmd], 1, min_minutes) != 0:
            raise Failed(f"{tag} failed")

    def save(self) -> None:
        if self.dry:
            return
        self.status["updated_utc"] = now()
        tmp = self.log / "night_status.json.tmp"
        tmp.write_text(json.dumps(self.status, indent=1), encoding="utf-8")
        os.replace(tmp, self.log / "night_status.json")

    # -- GPU-001 -----------------------------------------------------------------------------------------------
    @staticmethod
    def passed(mode: str) -> bool:
        f = ROOT / G1 / f"verdict_{mode}.json"
        try:
            return json.loads(f.read_text(encoding="utf-8")).get("pass") is True
        except (OSError, ValueError):
            return False

    @staticmethod
    def best_J() -> int:
        t = json.loads((ROOT / G1 / "verdict_throughput.json").read_text(encoding="utf-8"))["levels"]
        ok = {k: v for k, v in t.items() if v["complete"]}
        best = max(ok.items(), key=lambda kv: (round(kv[1]["aggregate_steps_per_s"], 1), -int(kv[0][1:])))
        return int(best[0][1:])

    def gpu001(self) -> None:
        if not self.dry and all(self.passed(m) for m in ("regression", "equivalence", "throughput")):
            self.J = self.best_J()
            return
        self.must("gpu001_env", [GPY, "-c", "import torch; print('[gpu001] torch', torch.__version__, 'hip', "
                                 "torch.version.hip, 'avail', torch.cuda.is_available(), torch.cuda.get_device_name(0) "
                                 "if torch.cuda.is_available() else '-')"])
        self.must("gpu001_regression_run", [PY, FB, "--seed", "10", "--condition", "baseline", "--steps", "50",
                                            "--split-file", f"{S16}/split_seed10_eps2.0.npy",
                                            "--out-root", f"{G1}/raw_cpu_regression", "--force"], 3)
        self.must("gpu001_regression", [PY, f"{G1}/compare.py", "regression"])
        equiv = [[GPY, FB, "--seed", str(s), "--condition", "baseline", "--steps", "2000", "--threads", "1",
                  "--device", "cuda", "--split-file", f"{S16}/split_seed{s}_eps2.0.npy", "--out-root", f"{G1}/raw_equiv"]
                 for s in (10, 11, 12)]
        if self.jobs("gpu001_equiv_runs", equiv, 1, 10) != 0:
            raise Failed("GPU-001 equivalence runs failed")
        self.must("gpu001_equivalence", [PY, f"{G1}/compare.py", "equivalence"])
        if not self.dry:
            shutil.rmtree(ROOT / G1 / "raw_par", ignore_errors=True)   # no stale throughput results
            (ROOT / G1 / "raw_par").mkdir(parents=True)
        for J in (1, 2, 4, 8):
            cmds = [[GPY, FB, "--seed", "10", "--condition", "baseline", "--steps", "500", "--threads", "1",
                     "--device", "cuda", "--split-file", f"{S16}/split_seed10_eps2.0.npy",
                     "--out-root", f"{G1}/raw_par/J{J}_{i}", "--force"] for i in range(1, J + 1)]
            t0 = time.time()
            self.jobs(f"gpu001_tp_J{J}", cmds, J, 5)      # exit 3 -> Refused -> no verdict (Astra 10 / review s13)
            if not self.dry:
                (ROOT / G1 / "raw_par" / f"wall_J{J}.txt").write_text(f"{t0} {time.time()}")
        self.must("gpu001_throughput", [PY, f"{G1}/compare.py", "throughput"])
        self.J = 4 if self.dry else self.best_J()

    # -- experiments -------------------------------------------------------------------------------------------
    def smoke(self, name: str, cmds: list[list[str]], min_minutes: float = 3) -> None:
        e = f"{R}/{EXP_DIR[name]}"
        if not self.dry:
            shutil.rmtree(ROOT / e / "raw_smoke", ignore_errors=True)
        if self.jobs(f"{name}_smoke", cmds, 1, min_minutes) != 0:
            raise Failed(f"{name} smoke run failed")
        self.must(f"{name}_smoke_check", [PY, "lab/tools/night_program.py", "--check-smoke", name])

    def runs_then_analysis(self, name: str, tag: str, cmds: list[list[str]], min_minutes: float) -> None:
        e = f"{R}/{EXP_DIR[name]}"
        if self.jobs(f"{name}_{tag}", cmds, self.J, min_minutes) != 0:
            raise Failed(f"{name} {tag}: some runs failed, analysis not run")
        self.must(f"{name}_{tag}_analysis", [PY, f"{e}/analyze.py"])

    def exp043(self) -> None:
        e = f"{R}/{EXP_DIR['EXP-043']}"
        self.must("EXP-043_selftest", [PY, f"{e}/analyze.py", "--selftest"])
        self.smoke("EXP-043", [[GPY, FB, "--seed", "70", "--condition", "baseline", "--steps", "50", "--threads", "1",
                                "--device", "cuda", "--p", "113", "--task", "mul",
                                "--split-file", f"{e}/splits/split_mul113_seed70_eps2.0_F.npy", "--spectra-at", "50",
                                "--out-root", f"{e}/raw_smoke", "--force"]])

        def job(task: str, p: int, s: int, eps: str, arm: str) -> list[str]:
            return [GPY, FB, "--seed", str(s), "--condition", "baseline", "--steps", "2000", "--threads", "1",
                    "--device", "cuda", "--p", str(p), "--task", task,
                    "--split-file", f"{e}/splits/split_{task}{p}_seed{s}_eps{eps}_{arm}.npy",
                    "--spectra-at", "50,250,500,1000,2000", "--out-root", f"{e}/raw"]
        main = [job(t, p, s, "2.0", a) for s in range(70, 80) for a in "FG" for t, p in (("mul", 113), ("add", 97))]
        self.runs_then_analysis("EXP-043", "main", main, 10)
        rand = [job(t, p, s, "0.0", "R") for s in range(70, 80) for t, p in (("mul", 113), ("add", 97))]
        self.runs_then_analysis("EXP-043", "random", rand, 10)

    def exp044(self) -> None:
        e = f"{R}/{EXP_DIR['EXP-044']}"
        S = f"{e}/splits"
        try:
            tasks = ({"mul113": {"verdict": "steuerbar"}, "add97": {"verdict": "steuerbar"}} if self.dry else
                     json.loads((ROOT / R / EXP_DIR["EXP-043"] / "summary.json").read_text(encoding="utf-8"))["tasks"])
        except (OSError, ValueError, KeyError) as ex:
            raise Failed(f"EXP-044 needs the EXP-043 summary ({type(ex).__name__})")
        run = [k for k, v in tasks.items() if v.get("verdict") == "steuerbar"]
        if not run:
            self.status["experiments"]["EXP-044"] = {"state": "not run by design (no task steuerbar in EXP-043)"}
            return
        self.smoke("EXP-044", [[GPY, FB, "--seed", "80", "--condition", "baseline", "--steps", "60", "--threads", "1",
                                "--device", "cuda", "--p", "113", "--task", "mul",
                                "--split-file", f"{S}/mul113_seed80_train_F.npy", "--test-file", f"{S}/mul113_seed80_test.npy",
                                "--switch-split-file", f"{S}/mul113_seed80_train_G.npy", "--switch-step", "30",
                                "--spectra-at", "30,60", "--out-root", f"{e}/raw_smoke", "--force"]])
        cmds = []
        for tp in run:
            t = tp.rstrip("0123456789")
            p = tp[len(t):]
            for s in range(80, 90):
                st = f"{S}/{tp}_seed{s}"
                for k in ("F", "G", "25", "50", "150"):
                    base = [GPY, FB, "--seed", str(s), "--condition", "baseline", "--threads", "1", "--device", "cuda",
                            "--p", p, "--task", t, "--test-file", f"{st}_test.npy", "--out-root", f"{e}/raw"]
                    if k in ("F", "G"):
                        cmds.append(base + ["--steps", "2000", "--split-file", f"{st}_train_{k}.npy",
                                            "--spectra-at", "50,250,2000"])
                    else:
                        t0 = int(k)
                        cmds.append(base + ["--steps", str(t0 + 2000), "--split-file", f"{st}_train_F.npy",
                                            "--switch-split-file", f"{st}_train_G.npy", "--switch-step", k,
                                            "--spectra-at", f"{t0},{t0 + 250},{t0 + 2000}"])
        self.runs_then_analysis("EXP-044", "main", cmds, 10)

    def exp045(self) -> None:
        e = f"{R}/{EXP_DIR['EXP-045']}"
        self.smoke("EXP-045", [[GPY, FB, "--seed", "90", "--condition", "baseline", "--steps", "50", "--threads", "1",
                                "--device", "cuda", "--arch", "mlp", "--split-file", f"{e}/splits/split_add113_seed90_eps2.0_F.npy",
                                "--spectra-at", "50", "--out-root", f"{e}/raw_smoke", "--force"]])
        cmds = [[GPY, FB, "--seed", str(s), "--condition", "baseline", "--steps", "10000", "--stop-after-gen", "100000",
                 "--threads", "1", "--device", "cuda", "--arch", "mlp",
                 "--split-file", f"{e}/splits/split_add113_seed{s}_eps2.0_{a}.npy",
                 "--spectra-at", "250,2000,5000,10000", "--out-root", f"{e}/raw"] for s in range(90, 100) for a in "FG"]
        self.runs_then_analysis("EXP-045", "main", cmds, 10)

    def exp046(self) -> None:
        e = f"{R}/{EXP_DIR['EXP-046']}"
        self.must("EXP-046_selftest", [PY, f"{e}/analyze.py", "--selftest"])
        self.smoke("EXP-046", [[GPY, f"{e}/group_train.py", "--seed", "140", "--steps", "50", "--device", "cuda",
                                "--split-file", f"{e}/splits/split_D59_seed140_eps2.0_F.npy", "--out-root", f"{e}/raw_smoke",
                                "--force"]])

        def job(s: int, eps: str, arm: str) -> list[str]:
            return [GPY, f"{e}/group_train.py", "--seed", str(s), "--steps", "2000", "--device", "cuda",
                    "--split-file", f"{e}/splits/split_D59_seed{s}_eps{eps}_{arm}.npy", "--out-root", f"{e}/raw"]
        self.runs_then_analysis("EXP-046", "main", [job(s, "2.0", a) for s in range(140, 150) for a in "FG"], 5)
        self.runs_then_analysis("EXP-046", "random", [job(s, "0.0", "R") for s in range(140, 150)], 5)

    def freq_ban_2000(self, e: str, s: int, stem: str) -> list[str]:
        return [GPY, FB, "--seed", str(s), "--condition", "baseline", "--steps", "2000", "--threads", "1", "--device", "cuda",
                "--split-file", f"{e}/splits/{stem}.npy", "--out-root", f"{e}/raw"]

    def exp047(self) -> None:
        e = f"{R}/{EXP_DIR['EXP-047']}"
        self.must("EXP-047_selftest", [PY, f"{e}/analyze.py", "--selftest"])
        cmds = [self.freq_ban_2000(e, s, f"split_add113_seed{s}_{k}_{a}")
                for s in range(150, 160) for k in ("eng", "shuf") for a in "FG"]
        self.runs_then_analysis("EXP-047", "main", cmds, 5)

    def exp048(self) -> None:
        e = f"{R}/{EXP_DIR['EXP-048']}"
        self.must("EXP-048_selftest", [PY, f"{e}/analyze.py", "--selftest"])
        self.smoke("EXP-048", [[GPY, f"{e}/intadd_train.py", "--seed", "160", "--steps", "50", "--device", "cuda",
                                "--split-file", f"{e}/splits/split_intadd113_seed160_eps2.0_F.npy",
                                "--out-root", f"{e}/raw_smoke", "--force"]])

        def job(s: int, eps: str, arm: str) -> list[str]:
            return [GPY, f"{e}/intadd_train.py", "--seed", str(s), "--steps", "2000", "--device", "cuda",
                    "--split-file", f"{e}/splits/split_intadd113_seed{s}_eps{eps}_{arm}.npy", "--out-root", f"{e}/raw"]
        self.runs_then_analysis("EXP-048", "main", [job(s, "2.0", a) for s in range(160, 170) for a in "FG"], 5)
        self.runs_then_analysis("EXP-048", "random", [job(s, "0.0", "R") for s in range(160, 170)], 5)

    def exp049(self) -> None:
        e = f"{R}/{EXP_DIR['EXP-049']}"
        self.must("EXP-049_selftest", [PY, f"{e}/analyze.py", "--selftest"])
        self.smoke("EXP-049", [[GPY, f"{e}/width_train.py", "--seed", "170", "--d-model", str(d), "--steps", "50",
                                "--device", "cuda", "--split-file", f"{e}/splits/split_add113_seed170_eps2.0_F.npy",
                                "--out-root", f"{e}/raw_smoke", "--force"] for d in (128, 512)])
        cmds = [[GPY, f"{e}/width_train.py", "--seed", str(s), "--d-model", str(d), "--steps", "2000", "--device", "cuda",
                 "--split-file", f"{e}/splits/split_add113_seed{s}_eps2.0_{a}.npy", "--out-root", f"{e}/raw"]
                for s in range(170, 180) for d in (128, 512) for a in "FG"]
        self.runs_then_analysis("EXP-049", "main", cmds, 5)

    def exp050(self) -> None:
        e = f"{R}/{EXP_DIR['EXP-050']}"
        self.must("EXP-050_selftest", [PY, f"{e}/analyze.py", "--selftest"])
        cmds = [self.freq_ban_2000(e, s, f"split_add113_seed{s}_{m}_{a}")
                for s in range(180, 190) for m in ("quadlm", "anti", "sym") for a in "FG"]
        self.runs_then_analysis("EXP-050", "main", cmds, 5)

    # -- driver ------------------------------------------------------------------------------------------------
    def run(self, order: list[str]) -> int:
        self.log.mkdir(parents=True, exist_ok=True)
        steps = {"GPU-001": self.gpu001, "EXP-043": self.exp043, "EXP-044": self.exp044, "EXP-045": self.exp045,
                 "EXP-046": self.exp046, "EXP-047": self.exp047, "EXP-048": self.exp048, "EXP-049": self.exp049,
                 "EXP-050": self.exp050}
        failed = False
        for name in order:
            print(f"[night] {now()} {name} start (J={self.J})", flush=True)
            self.status["experiments"][name] = {"state": "running", "start_utc": now()}
            self.save()
            try:
                steps[name]()
                self.status["experiments"][name].setdefault("state", "ok")
                if self.status["experiments"][name]["state"] == "running":
                    self.status["experiments"][name]["state"] = "ok"
            except Refused as ex:
                self.status["experiments"][name]["state"] = f"refused by guard ({ex})"
                self.status["result"] = "stopped by guard (exit 3): rerun the same command in the next window"
                self.save()
                print(f"[night] {name}: guard refused ({ex}), stop", flush=True)
                return 3
            except Failed as ex:
                failed = True
                self.status["experiments"][name]["state"] = f"failed: {ex}"
                print(f"[night] {name} FAILED: {ex}", flush=True)
                if name == "GPU-001":           # the gate: no GPU experiment without a passed GPU-001
                    self.status["result"] = "GPU-001 not passed: no GPU runs"
                    self.save()
                    return 1
            self.status["experiments"][name]["end_utc"] = now()
            self.save()
        self.status["result"] = "done with failures" if failed else "all done"
        self.save()
        print(f"[night] {self.status['result']}", flush=True)
        return 1 if failed else 0


# -- smoke-record checks (run as guarded jobs via --check-smoke) ---------------------------------------------------
def check_smoke(name: str) -> None:
    import glob
    e = ROOT / R / EXP_DIR[name]
    recs = [json.loads(Path(f).read_text(encoding="utf-8")) for f in sorted(glob.glob(str(e / "raw_smoke" / "*" / "result.json")))]
    assert recs, "no smoke record"
    for r in recs:
        assert r["status"] == "completed" and r["device"] == "cuda" and r["run_id"].endswith("_devcuda"), r.get("run_id")
    r = recs[0]
    if name == "EXP-043":
        assert r["config"]["task"] == "mul" and r["config"]["p"] == 113 and r["run_id"].startswith("EXP-043_"), r["run_id"]
        assert r["run_id"].endswith("_mul113_devcuda"), r["run_id"]
    elif name == "EXP-044":
        sw = r["events"]["switch"]
        assert sw["step"] == 30 and r["run_id"].startswith("EXP-044_") and sw["n_G_minus_F"] > 2000, sw
    elif name == "EXP-045":
        assert r["config"]["arch"] == "mlp" and r["run_id"].startswith("EXP-045_"), r["run_id"]
    elif name == "EXP-046":
        assert r["order"] == 118 and r["config"]["p"] == 118 and len(r["final_top_m_irreps"]) == 5, r["run_id"]
    elif name == "EXP-048":
        assert r["n_out"] == 225 and r["config"]["p"] == 225 and len(r["final_top_m_freqs"]) == 5, r["run_id"]
        assert r["steps_completed"] == 50, r["steps_completed"]
    elif name == "EXP-049":
        assert sorted(x["d_model"] for x in recs) == [128, 512], [x["d_model"] for x in recs]
        assert all(x["steps_completed"] == 50 and x["config"]["d_model"] == x["d_model"] for x in recs)
    for x in recs:
        print(f"[{name}] smoke ok {x['run_id']} {x.get('sec_per_step')} s/step {x.get('cuda_max_mem_mb')} MB", flush=True)


def take_lock() -> None:
    """One night program at a time; a lock whose PID no longer runs is taken over (tasklist, no os.kill on Windows)."""
    import subprocess
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        try:
            pid = json.loads(LOCK.read_text()).get("pid")
        except (OSError, ValueError):
            pid = None
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout
        if pid is not None and str(pid) in out:
            raise SystemExit(f"[night] another night program runs (pid {pid}, {LOCK})")
        LOCK.unlink()
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(fd, "w") as f:
        json.dump({"pid": os.getpid(), "start_utc": now()}, f)
    import atexit
    atexit.register(lambda: LOCK.unlink(missing_ok=True))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--experiments", default=",".join(DEFAULT_ORDER))
    ap.add_argument("--log-dir", type=Path, default=None)
    ap.add_argument("--check-smoke", default=None, help=argparse.SUPPRESS)
    ap.add_argument("--dry-run", action="store_true", help="walk the program and print the jobs; run nothing")
    a = ap.parse_args()
    if a.check_smoke:
        check_smoke(a.check_smoke)
        return 0
    order = [x.strip() for x in a.experiments.split(",") if x.strip()]
    unknown = [x for x in order if x != "GPU-001" and x not in EXP_DIR]
    if unknown:
        ap.error(f"unknown experiments {unknown}")
    if "GPU-001" not in order[:1]:
        order = ["GPU-001"] + [x for x in order if x != "GPU-001"]   # the gate always runs first (skips if passed)
    if a.dry_run:
        return Night(Path("."), dry=True).run(order)
    take_lock()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    log_dir = a.log_dir or ROOT / "lab" / "runner" / "logs" / f"night_{stamp}"
    return Night(log_dir).run(order)


if __name__ == "__main__":
    sys.exit(main())
