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

CPU mode (--cpu): EXP-014 (from queue_s5) and the CPU night queue (queue_s10.sh minus EXP-034) as the same kind of program, own lock, so it
can run next to the GPU program. CPU runs keep --threads 4 (run ids and finished runs depend on it); workers default to
max(1, (12 - J_gpu) // 4) so that all CPU threads stay <= 12 (rule 17). EXP-034 (dependent job chain) is not ported yet.

Usage (project root):
    python lab/tools/night_program.py [--experiments GPU-001,EXP-043,...] [--log-dir DIR]
    python lab/tools/night_program.py --cpu [--experiments EXP-035,...] [--cpu-workers N]
    python lab/tools/night_program.py --check-smoke EXP-043      # internal: smoke-record checks (run as a guarded job)
    python lab/tools/night_program.py --paket-a-cpu --experiments EXP-043,... [--cpu-workers N]   # fallback if GPU-001 fails

--paket-a-cpu (session 15, UNTESTED): programme-A experiments on the CPU with the global python (--device cpu, --threads 1, J = --cpu-workers,
default 3), no GPU-001 gate; sets LAB_PAKET_A_DEVICE=cpu so that the analyses (lab/tools/paket_a_device.py) read only the CPU runs.
Rule 16d: never mix devices inside one experiment. Keep the CPU thread sum <= 12 (rule 17) if the --cpu program runs at the same time.
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
EXIT_TIMEOUT = 124            # guarded_run.py: job killed at its hard time limit
PY = "python"
DEVA, PYA = "cuda", GPY       # programme-A device/interpreter; main() switches to ("cpu", PY) with --paket-a-cpu
FB = f"{R}/EXP-001-freq-ban/freq_ban.py"
G1 = f"{R}/GPU-001-equivalence"
S16 = f"{R}/EXP-016-engineered-split/splits"
DEFAULT_ORDER = ("GPU-001", "EXP-043", "EXP-046", "EXP-047", "EXP-051", "EXP-048", "EXP-049", "EXP-044", "EXP-045")
# EXP-014 first (programme A, Astra 5: crossed split x init; triage s13), then the queue_s10 order; EXP-034 not ported
CPU_ORDER = ("EXP-014", "EXP-035", "EXP-038", "EXP-041", "EXP-036", "EXP-039", "EXP-040", "EXP-042")
S20 = f"{R}/EXP-020-data-switch/splits"
EXP_DIR = {"EXP-043": "EXP-043-generalize-steering", "EXP-044": "EXP-044-generalize-lockin",
           "EXP-045": "EXP-045-mlp-steering", "EXP-046": "EXP-046-dihedral-steering",
           "EXP-047": "EXP-047-marginal-control", "EXP-048": "EXP-048-intadd-steering",
           "EXP-049": "EXP-049-width-steering", "EXP-050": "EXP-050-phase-dissociation",
           "EXP-051": "EXP-051-functional-ablation",
           "EXP-035": "EXP-035-warmup-lockin", "EXP-036": "EXP-036-init-conflict", "EXP-038": "EXP-038-where-lockin",
           "EXP-039": "EXP-039-lr-clock", "EXP-040": "EXP-040-we-init-scale", "EXP-041": "EXP-041-imprint",
           "EXP-042": "EXP-042-bias-strength", "EXP-014": "EXP-014-split-vs-init"}
CPU_EXPS = set(CPU_ORDER)
LOCK = ROOT / "lab" / "runner" / "night_program.lock"
LOCK_CPU = ROOT / "lab" / "runner" / "night_program_cpu.lock"


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
        if rc != 0 and self.cut_by_time_limit(self.log / tag):
            raise Refused(f"{tag}: a job was cut at the session deadline or 13:00 (exit {EXIT_TIMEOUT})")
        return rc

    @staticmethod
    def cut_by_time_limit(log_dir: Path) -> bool:
        """Session 17: pq passes no --job-minutes, so a guard timeout (124) always means the session deadline or the
        window end fired. That is 'out of time' (resume next session), not a technical failure of the experiment."""
        try:
            s = json.loads((log_dir / "summary.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return False
        return any(r.get("exit_code") == EXIT_TIMEOUT for r in s.get("results", []))

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
        """PASS and sealed to the current trainer/checker/GPU torch (Astra 10); a stale verdict does not count."""
        f = ROOT / G1 / f"verdict_{mode}.json"
        try:
            v = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return False
        sys.path.insert(0, str(ROOT / G1))
        import compare  # noqa: E402  (pure python, no torch)
        return v.get("pass") is True and v.get("seal") == compare.seal()

    @staticmethod
    def best_J() -> int:
        t = json.loads((ROOT / G1 / "verdict_throughput.json").read_text(encoding="utf-8"))["levels"]
        ok = {k: v for k, v in t.items() if v["complete"]}
        best = max(ok.items(), key=lambda kv: (round(kv[1]["aggregate_steps_per_s"], 1), -int(kv[0][1:])))
        return int(best[0][1:])

    def gpu001(self) -> None:
        if not self.dry and all(self.passed(m) for m in ("components", "regression", "equivalence", "throughput")):
            self.J = self.best_J()
            return
        self.must("gpu001_env", [GPY, "-c", "import torch; print('[gpu001] torch', torch.__version__, 'hip', "
                                 "torch.version.hip, 'avail', torch.cuda.is_available(), torch.cuda.get_device_name(0) "
                                 "if torch.cuda.is_available() else '-')"])
        # session 17: each stage is skipped if its own verdict already PASSes with the current seal, so a session that
        # ends in the middle of GPU-001 does not force the next one to redo the finished stages
        if self.dry or not self.passed("components"):   # session 18, Astra 9: forward/backward/AdamW/repeat first (cheap)
            self.gpu001_components()
        if self.dry or not self.passed("regression"):
            self.gpu001_regression()
        if self.dry or not self.passed("equivalence"):
            self.gpu001_equivalence()
        if self.dry or not self.passed("throughput"):
            self.gpu001_throughput()
        self.J = 4 if self.dry else self.best_J()

    def gpu001_components(self) -> None:
        self.must("gpu001_components", [GPY, f"{G1}/components.py"], 3)

    def gpu001_regression(self) -> None:
        self.must("gpu001_regression_run", [PY, FB, "--seed", "10", "--condition", "baseline", "--steps", "50",
                                            "--split-file", f"{S16}/split_seed10_eps2.0.npy",
                                            "--out-root", f"{G1}/raw_cpu_regression", "--force"], 3)
        self.must("gpu001_regression", [PY, f"{G1}/compare.py", "regression"])

    def gpu001_equivalence(self) -> None:
        if not self.dry:                  # review s13: a re-gate must not reuse runs made with older code
            for d_ in ("raw_equiv", "raw_equiv_cpu_venv"):
                shutil.rmtree(ROOT / G1 / d_, ignore_errors=True)
        equiv = [[GPY, FB, "--seed", str(s), "--condition", "baseline", "--steps", "2000", "--threads", "1",
                  "--device", "cuda", "--split-file", f"{S16}/split_seed{s}_eps2.0.npy", "--out-root", f"{G1}/raw_equiv"]
                 for s in (10, 11, 12)]
        if self.jobs("gpu001_equiv_runs", equiv, 1, 10) != 0:
            raise Failed("GPU-001 equivalence runs failed")
        # Astra 10 diagnostic: the same CPU run with the GPU venv's torch (version vs device); failure is reported, not fatal
        self.jobs("gpu001_venv_cpu_run", [[GPY, FB, "--seed", "10", "--condition", "baseline", "--steps", "2000",
                                           "--split-file", f"{S16}/split_seed10_eps2.0.npy",
                                           "--out-root", f"{G1}/raw_equiv_cpu_venv"]], 1, 10)
        self.must("gpu001_equivalence", [PY, f"{G1}/compare.py", "equivalence"])

    def gpu001_throughput(self) -> None:
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
        self.smoke("EXP-043", [[PYA, FB, "--seed", "70", "--condition", "baseline", "--steps", "50", "--threads", "1",
                                "--device", DEVA, "--p", "113", "--task", "mul",
                                "--split-file", f"{e}/splits/split_mul113_seed70_eps2.0_F.npy", "--spectra-at", "50",
                                "--out-root", f"{e}/raw_smoke", "--force"]])

        def job(task: str, p: int, s: int, eps: str, arm: str) -> list[str]:
            return [PYA, FB, "--seed", str(s), "--condition", "baseline", "--steps", "2000", "--threads", "1",
                    "--device", DEVA, "--p", str(p), "--task", task,
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
        self.smoke("EXP-044", [[PYA, FB, "--seed", "80", "--condition", "baseline", "--steps", "60", "--threads", "1",
                                "--device", DEVA, "--p", "113", "--task", "mul",
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
                    base = [PYA, FB, "--seed", str(s), "--condition", "baseline", "--threads", "1", "--device", DEVA,
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
        self.smoke("EXP-045", [[PYA, FB, "--seed", "90", "--condition", "baseline", "--steps", "50", "--threads", "1",
                                "--device", DEVA, "--arch", "mlp", "--split-file", f"{e}/splits/split_add113_seed90_eps2.0_F.npy",
                                "--spectra-at", "50", "--out-root", f"{e}/raw_smoke", "--force"]])
        cmds = [[PYA, FB, "--seed", str(s), "--condition", "baseline", "--steps", "10000", "--stop-after-gen", "100000",
                 "--threads", "1", "--device", DEVA, "--arch", "mlp",
                 "--split-file", f"{e}/splits/split_add113_seed{s}_eps2.0_{a}.npy",
                 "--spectra-at", "250,2000,5000,10000", "--out-root", f"{e}/raw"] for s in range(90, 100) for a in "FG"]
        self.runs_then_analysis("EXP-045", "main", cmds, 10)

    def exp046(self) -> None:
        e = f"{R}/{EXP_DIR['EXP-046']}"
        self.must("EXP-046_selftest", [PY, f"{e}/analyze.py", "--selftest"])
        self.smoke("EXP-046", [[PYA, f"{e}/group_train.py", "--seed", "140", "--steps", "50", "--device", DEVA,
                                "--split-file", f"{e}/splits/split_D59_seed140_eps2.0_F.npy", "--out-root", f"{e}/raw_smoke",
                                "--force"]])

        def job(s: int, eps: str, arm: str) -> list[str]:
            return [PYA, f"{e}/group_train.py", "--seed", str(s), "--steps", "2000", "--device", DEVA,
                    "--split-file", f"{e}/splits/split_D59_seed{s}_eps{eps}_{arm}.npy", "--out-root", f"{e}/raw"]
        self.runs_then_analysis("EXP-046", "main", [job(s, "2.0", a) for s in range(140, 150) for a in "FG"], 5)
        self.runs_then_analysis("EXP-046", "random", [job(s, "0.0", "R") for s in range(140, 150)], 5)

    def freq_ban_2000(self, e: str, s: int, stem: str, *extra: str) -> list[str]:
        return [PYA, FB, "--seed", str(s), "--condition", "baseline", "--steps", "2000", "--threads", "1", "--device", DEVA,
                "--split-file", f"{e}/splits/{stem}.npy", "--out-root", f"{e}/raw", *extra]

    def exp047(self) -> None:
        e = f"{R}/{EXP_DIR['EXP-047']}"
        self.must("EXP-047_selftest", [PY, f"{e}/analyze.py", "--selftest"])
        cmds = [self.freq_ban_2000(e, s, f"split_add113_seed{s}_{k}_{a}", "--save-model")   # models for EXP-051 (P2)
                for s in range(150, 160) for k in ("eng", "shuf") for a in "FG"]
        self.runs_then_analysis("EXP-047", "main", cmds, 5)

    def exp051(self) -> None:
        """P2: ablation on the saved EXP-047 models, no training (own step, so a failure here does not mark EXP-047)."""
        e51 = f"{R}/EXP-051-functional-ablation"
        if not self.dry and self.status["experiments"].get("EXP-047", {}).get("state") != "ok":
            raise Failed("EXP-047 did not finish ok in this program run")
        self.must("EXP-051_selftest", [PY, f"{e51}/analyze.py", "--selftest"])
        self.must("EXP-051_analysis", [PY, f"{e51}/analyze.py"], 5)

    def exp048(self) -> None:
        e = f"{R}/{EXP_DIR['EXP-048']}"
        self.must("EXP-048_selftest", [PY, f"{e}/analyze.py", "--selftest"])
        self.smoke("EXP-048", [[PYA, f"{e}/intadd_train.py", "--seed", "160", "--steps", "50", "--device", DEVA,
                                "--split-file", f"{e}/splits/split_intadd113_seed160_eps2.0_F.npy",
                                "--out-root", f"{e}/raw_smoke", "--force"]])

        def job(s: int, eps: str, arm: str) -> list[str]:
            return [PYA, f"{e}/intadd_train.py", "--seed", str(s), "--steps", "2000", "--device", DEVA,
                    "--split-file", f"{e}/splits/split_intadd113_seed{s}_eps{eps}_{arm}.npy", "--out-root", f"{e}/raw"]
        self.runs_then_analysis("EXP-048", "main", [job(s, "2.0", a) for s in range(160, 170) for a in "FG"], 5)
        self.runs_then_analysis("EXP-048", "random", [job(s, "0.0", "R") for s in range(160, 170)], 5)

    def exp049(self) -> None:
        e = f"{R}/{EXP_DIR['EXP-049']}"
        self.must("EXP-049_selftest", [PY, f"{e}/analyze.py", "--selftest"])
        self.smoke("EXP-049", [[PYA, f"{e}/width_train.py", "--seed", "170", "--d-model", str(d), "--steps", "50",
                                "--device", DEVA, "--split-file", f"{e}/splits/split_add113_seed170_eps2.0_F.npy",
                                "--out-root", f"{e}/raw_smoke", "--force"] for d in (128, 512)])
        cmds = [[PYA, f"{e}/width_train.py", "--seed", str(s), "--d-model", str(d), "--steps", "2000", "--device", DEVA,
                 "--split-file", f"{e}/splits/split_add113_seed{s}_eps2.0_{a}.npy", "--out-root", f"{e}/raw"]
                for s in range(170, 180) for d in (128, 512) for a in "FG"]
        self.runs_then_analysis("EXP-049", "main", cmds, 5)

    def exp050(self) -> None:
        e = f"{R}/{EXP_DIR['EXP-050']}"
        self.must("EXP-050_selftest", [PY, f"{e}/analyze.py", "--selftest"])
        cmds = [self.freq_ban_2000(e, s, f"split_add113_seed{s}_{m}_{a}")
                for s in range(180, 190) for m in ("quadlm", "anti", "sym") for a in "FG"]
        self.runs_then_analysis("EXP-050", "main", cmds, 5)

    # -- CPU experiments (queue_s10 minus EXP-034; freq_ban default --threads 4, global python) -----------------------
    def fb(self, *args: str) -> list[str]:
        return [PY, FB, "--condition", "baseline", *args]

    def exp014(self) -> None:
        """queue_s5.sh: crossed init a x split b, disjoint pairs both directions (EXP-014 Nachtrag a); default 15000 steps."""
        o = f"{R}/{EXP_DIR['EXP-014']}"
        pairs = ((10, 11), (11, 10), (12, 13), (13, 12), (14, 15), (15, 14), (16, 17), (17, 16), (18, 19), (19, 18))
        cmds = [self.fb("--seed", str(a), "--split-seed", str(b), "--stop-after-gen", "25", "--out-root", f"{o}/raw")
                for a, b in pairs]
        self.runs_then_analysis("EXP-014", "main", cmds, 33)

    def exp035(self) -> None:
        o = f"{R}/{EXP_DIR['EXP-035']}"
        self.smoke("EXP-035", [self.fb("--seed", "30", "--steps", "60", "--stop-after-gen", "8000",
                                       "--split-file", f"{S20}/seed30_train_F.npy", "--test-file", f"{S20}/seed30_test.npy",
                                       "--switch-split-file", f"{S20}/seed30_train_G.npy", "--switch-step", "30",
                                       "--warmup", "200", "--out-root", f"{o}/raw_smoke")], 2)
        only_f, switch = [], []
        for sd in (30, 31, 32, 34):
            base = ["--seed", str(sd), "--test-file", f"{S20}/seed{sd}_test.npy", "--warmup", "200", "--out-root", f"{o}/raw"]
            only_f.append(self.fb(*base, "--steps", "8000", "--stop-after-gen", "2000", "--split-file", f"{S20}/seed{sd}_train_F.npy"))
            for t in (50, 150, 100, 25, 10, 250):
                switch.append(self.fb(*base, "--steps", str(t + 2000), "--stop-after-gen", "8000",
                                      "--split-file", f"{S20}/seed{sd}_train_F.npy",
                                      "--switch-split-file", f"{S20}/seed{sd}_train_G.npy", "--switch-step", str(t)))
        if self.jobs("EXP-035_onlyF", only_f, self.J, 19) != 0:
            raise Failed("EXP-035 only-F runs failed, analysis not run")
        self.runs_then_analysis("EXP-035", "switch", switch, 9)

    def exp038(self) -> None:
        o = f"{R}/{EXP_DIR['EXP-038']}"
        if not self.dry:
            shutil.rmtree(ROOT / o / "raw_smoke", ignore_errors=True)
        sm = [self.fb("--seed", "30", "--steps", "40", "--stop-after-gen", "8000", "--split-file", f"{S20}/seed30_train_F.npy",
                      "--test-file", f"{S20}/seed30_test.npy", "--switch-split-file", f"{S20}/seed30_train_G.npy",
                      "--switch-step", "30", "--reset-at-switch", rs, "--force", "--out-root", f"{o}/raw_smoke") for rs in ("we", "rest")]
        if self.jobs("EXP-038_smoke", sm, 1, 2) != 0:
            raise Failed("EXP-038 smoke failed")
        self.must("EXP-038_smoke_check", [PY, f"{o}/check_smoke.py"])
        cmds = [self.fb("--seed", str(sd), "--steps", "2150", "--stop-after-gen", "8000", "--split-file", f"{S20}/seed{sd}_train_F.npy",
                        "--test-file", f"{S20}/seed{sd}_test.npy", "--switch-split-file", f"{S20}/seed{sd}_train_G.npy",
                        "--switch-step", "150", "--reset-at-switch", rs, "--save-model", "--out-root", f"{o}/raw")
                for rs in ("we", "rest") for sd in range(30, 35)]
        self.runs_then_analysis("EXP-038", "main", cmds, 7)

    def exp041(self) -> None:
        o = f"{R}/{EXP_DIR['EXP-041']}"
        sp = f"{R}/EXP-018-split-speed/splits"
        self.must("EXP-041_selftest", [PY, f"{o}/analyze.py", "--selftest"], 1)
        cmds = []
        for sd in range(20, 30):
            for a in "RE":
                cmds.append(self.fb("--seed", str(sd), "--steps", "2150", "--stop-after-gen", "8000",
                                    "--split-file", f"{sp}/seed{sd}_train_{a}.npy", "--test-file", f"{sp}/seed{sd}_test.npy",
                                    "--spectra-at", "50,150", "--out-root", f"{o}/raw"))
            for a, b in (("E", "R"), ("R", "E")):
                cmds.append(self.fb("--seed", str(sd), "--steps", "2150", "--stop-after-gen", "8000",
                                    "--split-file", f"{sp}/seed{sd}_train_{a}.npy", "--test-file", f"{sp}/seed{sd}_test.npy",
                                    "--switch-split-file", f"{sp}/seed{sd}_train_{b}.npy", "--switch-step", "150",
                                    "--out-root", f"{o}/raw"))
        self.runs_then_analysis("EXP-041", "main", cmds, 7)

    def exp036(self) -> None:
        o = f"{R}/{EXP_DIR['EXP-036']}"
        sa = "5,10,15,20,25,30,40,50,75,100,150,200"
        self.smoke("EXP-036", [self.fb("--seed", "130", "--steps", "30", "--stop-after-gen", "8000",
                                       "--split-file", f"{S20}/seed30_train_F.npy", "--test-file", f"{S20}/seed30_test.npy",
                                       "--spectra-at", "5,10,20", "--force", "--out-root", f"{o}/raw_smoke")], 2)
        cmds = []
        for sd, init in ((30, 130), (31, 131), (32, 132), (33, 133), (34, 134), (30, 230), (31, 231)):
            base = ["--seed", str(init), "--stop-after-gen", "8000", "--test-file", f"{S20}/seed{sd}_test.npy",
                    "--spectra-at", sa, "--out-root", f"{o}/raw"]
            for arm in "FG":
                cmds.append(self.fb(*base, "--steps", "2000", "--split-file", f"{S20}/seed{sd}_train_{arm}.npy"))
            for t in (25, 50, 10):
                cmds.append(self.fb(*base, "--steps", str(t + 2000), "--split-file", f"{S20}/seed{sd}_train_F.npy",
                                    "--switch-split-file", f"{S20}/seed{sd}_train_G.npy", "--switch-step", str(t)))
        self.runs_then_analysis("EXP-036", "main", cmds, 7)
        self.must("EXP-036_p36b", [PY, f"{o}/analyze_p36b.py"])

    def clock_like(self, name: str, flag: str, levels: tuple[str, str], ts: dict, seeds: tuple[int, ...], g_only: bool) -> None:
        o = f"{R}/{EXP_DIR[name]}"
        sa = "5,10,12,15,20,25,30,40,50,75,100,150,200"
        g_runs, f_runs, s_runs = [], [], []      # the shell queues gave them 7 / 19 / 9 minimum minutes
        for sd in seeds:
            for c in levels:
                base = ["--seed", str(sd), "--test-file", f"{S20}/seed{sd}_test.npy", flag, c, "--spectra-at", sa,
                        "--out-root", f"{o}/raw"]
                if g_only:
                    g_runs.append(self.fb(*base, "--steps", "2000", "--stop-after-gen", "8000",
                                          "--split-file", f"{S20}/seed{sd}_train_G.npy"))
                f_runs.append(self.fb(*base, "--steps", "8000", "--stop-after-gen", "2000", "--split-file", f"{S20}/seed{sd}_train_F.npy"))
                for t in ts[c]:
                    s_runs.append(self.fb(*base, "--steps", str(t + 2000), "--stop-after-gen", "8000",
                                          "--split-file", f"{S20}/seed{sd}_train_F.npy",
                                          "--switch-split-file", f"{S20}/seed{sd}_train_G.npy", "--switch-step", str(t)))
        for tag, runs, mm in (("onlyG", g_runs, 7), ("onlyF", f_runs, 19)):
            if runs and self.jobs(f"{name}_{tag}", runs, self.J, mm) != 0:
                raise Failed(f"{name} {tag} runs failed, analysis not run")
        self.runs_then_analysis(name, "switch", s_runs, 9)

    def exp039(self) -> None:
        o = f"{R}/{EXP_DIR['EXP-039']}"
        self.smoke("EXP-039", [self.fb("--seed", "30", "--steps", "60", "--stop-after-gen", "8000",
                                       "--split-file", f"{S20}/seed30_train_F.npy", "--test-file", f"{S20}/seed30_test.npy",
                                       "--switch-split-file", f"{S20}/seed30_train_G.npy", "--switch-step", "30",
                                       "--lr-scale", "2", "--out-root", f"{o}/raw_smoke")], 2)
        self.clock_like("EXP-039", "--lr-scale", ("2", "0.5"), {"2": (25, 12, 10, 50), "0.5": (50, 25, 100, 150)},
                        (30, 32, 34, 31), g_only=False)

    def exp040(self) -> None:
        o = f"{R}/{EXP_DIR['EXP-040']}"
        self.must("EXP-040_selftest", [PY, f"{o}/analyze.py", "--selftest"], 1)
        self.smoke("EXP-040", [self.fb("--seed", "30", "--steps", "60", "--stop-after-gen", "8000",
                                       "--split-file", f"{S20}/seed30_train_F.npy", "--test-file", f"{S20}/seed30_test.npy",
                                       "--switch-split-file", f"{S20}/seed30_train_G.npy", "--switch-step", "30",
                                       "--we-init-scale", "0.5", "--out-root", f"{o}/raw_smoke")], 2)
        self.clock_like("EXP-040", "--we-init-scale", ("0.5", "2"), {"0.5": (25, 12, 10, 50), "2": (50, 25, 100, 150)},
                        (30, 32, 34, 31), g_only=True)

    def exp042(self) -> None:
        x = f"{R}/{EXP_DIR['EXP-042']}"
        self.must("EXP-042_selftest", [PY, f"{x}/analyze.py", "--selftest"], 1)
        seeds = (30, 31, 32, 34)
        first = [self.fb("--seed", str(sd), "--steps", "8000", "--stop-after-gen", "2000",
                         "--split-file", f"{x}/eps8/splits/seed{sd}_train_F.npy", "--test-file", f"{x}/eps8/splits/seed{sd}_test.npy",
                         "--out-root", f"{x}/eps8/raw") for sd in seeds]
        if self.jobs("EXP-042_onlyF", first, self.J, 19) != 0:
            raise Failed("EXP-042 only-F runs failed, analysis not run")
        cmds = []
        for e, ts in (("8", (50, 100, 25, 150)), ("1", (25, 10, 50))):
            sp, o = f"{x}/eps{e}/splits", f"{x}/eps{e}/raw"
            for sd in seeds:
                cmds.append(self.fb("--seed", str(sd), "--steps", "2000", "--stop-after-gen", "8000",
                                    "--split-file", f"{sp}/seed{sd}_train_G.npy", "--test-file", f"{sp}/seed{sd}_test.npy", "--out-root", o))
                for t in ts:
                    cmds.append(self.fb("--seed", str(sd), "--steps", str(t + 2000), "--stop-after-gen", "8000",
                                        "--split-file", f"{sp}/seed{sd}_train_F.npy", "--test-file", f"{sp}/seed{sd}_test.npy",
                                        "--switch-split-file", f"{sp}/seed{sd}_train_G.npy", "--switch-step", str(t), "--out-root", o))
        self.runs_then_analysis("EXP-042", "main", cmds, 7)

    # -- driver ------------------------------------------------------------------------------------------------
    def run(self, order: list[str]) -> int:
        self.log.mkdir(parents=True, exist_ok=True)
        steps = {"GPU-001": self.gpu001, "EXP-043": self.exp043, "EXP-044": self.exp044, "EXP-045": self.exp045,
                 "EXP-046": self.exp046, "EXP-047": self.exp047, "EXP-048": self.exp048, "EXP-049": self.exp049,
                 "EXP-050": self.exp050, "EXP-051": self.exp051, "EXP-035": self.exp035, "EXP-036": self.exp036, "EXP-038": self.exp038,
                 "EXP-039": self.exp039, "EXP-040": self.exp040, "EXP-041": self.exp041, "EXP-042": self.exp042,
                 "EXP-014": self.exp014}
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
            except Exception as ex:          # review s13: unexpected errors fail this experiment, not the program
                if isinstance(ex, Failed):
                    msg = str(ex)
                else:
                    msg = f"unexpected {type(ex).__name__}: {ex}"
                ex = Failed(msg)
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
        if name in CPU_EXPS:
            assert r["status"] == "completed" and r.get("device", "cpu") == "cpu", r.get("run_id")
        else:
            assert r["status"] == "completed" and r["device"] == DEVA, r.get("run_id")
            assert r["run_id"].endswith("_devcuda") if DEVA == "cuda" else "_devcuda" not in r["run_id"], r.get("run_id")
    r = recs[0]
    if name == "EXP-043":
        assert r["config"]["task"] == "mul" and r["config"]["p"] == 113 and r["run_id"].startswith("EXP-043_"), r["run_id"]
        assert r["run_id"].endswith("_mul113" + ("_devcuda" if DEVA == "cuda" else "")), r["run_id"]
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
    elif name == "EXP-035":
        e_ = r["events"]
        assert r["warmup"] == 200 and e_.get("switch", {}).get("step") == 30 and e_.get("displacement_at_switch", {}).get("W_E", 0) > 0
    elif name == "EXP-036":
        import numpy as np
        d = e / "raw_smoke" / "EXP-018_baseline_seed130_thr4_seed30_train_F"
        assert r["spectra_at"] == [5, 10, 20] and r["steps_completed"] == 30, r["run_id"]
        assert np.load(d / "spectra_steps.npy").tolist() == [0, 5, 10, 20, 30]
    elif name == "EXP-039":
        e_ = r["events"]
        assert r["lr_scale"] == 2.0 and r["lr_scale_until"] == 250 and e_.get("switch", {}).get("step") == 30
        assert e_.get("displacement_at_switch", {}).get("W_E", 0) > 0
    elif name == "EXP-040":
        import numpy as np
        d = e / "raw_smoke" / "EXP-020_baseline_seed30_thr4_seed30_train_F_to_seed30_train_G_at30_wes0.5"
        ref = ROOT / R / "EXP-035-warmup-lockin/raw/EXP-018_baseline_seed30_thr4_seed30_train_F_wu200"
        a_, b_ = np.load(d / "spectra.npy")[0], np.load(ref / "spectra.npy")[0]
        assert r["we_init_scale"] == 0.5 and r["events"].get("switch", {}).get("step") == 30 and np.allclose(a_, 0.25 * b_, rtol=1e-5)
    for x in recs:
        print(f"[{name}] smoke ok {x['run_id']} {x.get('sec_per_step')} s/step {x.get('cuda_max_mem_mb')} MB", flush=True)


def take_lock(lock: Path) -> None:
    """One program per mode at a time; a lock whose PID no longer runs is taken over (tasklist, no os.kill on Windows)."""
    import subprocess
    LOCK = lock  # noqa: N806
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
    ap.add_argument("--cpu", action="store_true", help="CPU night queue (EXP-035..042 without 034), own lock")
    ap.add_argument("--cpu-workers", type=int, default=None, help="default max(1, (12 - J_gpu) // 4); with --paket-a-cpu: 3")
    ap.add_argument("--paket-a-cpu", action="store_true", help="programme A on the CPU (fallback if GPU-001 fails), no GPU-001 gate")
    a = ap.parse_args()
    global DEVA, PYA
    if a.paket_a_cpu and a.cpu:
        ap.error("--paket-a-cpu and --cpu exclude each other")
    if a.paket_a_cpu:
        os.environ["LAB_PAKET_A_DEVICE"] = "cpu"          # inherited by every guarded job (analyses, --check-smoke)
    DEVA = os.environ.get("LAB_PAKET_A_DEVICE", "cuda")
    if DEVA not in ("cuda", "cpu"):
        ap.error(f"LAB_PAKET_A_DEVICE must be cuda or cpu, not {DEVA!r}")
    PYA = GPY if DEVA == "cuda" else PY
    if a.check_smoke:
        check_smoke(a.check_smoke)
        return 0
    if a.cpu:
        order = [x.strip() for x in a.experiments.split(",") if x.strip()] if a.experiments != ",".join(DEFAULT_ORDER) \
            else list(CPU_ORDER)
        bad = [x for x in order if x not in CPU_EXPS]
        if bad:
            ap.error(f"not CPU experiments: {bad}")
        workers = a.cpu_workers
        if workers is None:               # review s13: before GPU-001 has chosen J assume the worst case J = 8 -> 1 worker
            j = Night.best_J() if Night.passed("throughput") else 8
            workers = max(1, (12 - j) // 4)
        night = Night(Path(".") if a.dry_run else (a.log_dir or ROOT / "lab" / "runner" / "logs" /
                      f"night_cpu_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')}"), dry=a.dry_run)
        night.J = workers
        if not a.dry_run:
            take_lock(LOCK_CPU)
        return night.run(order)
    order = [x.strip() for x in a.experiments.split(",") if x.strip()]
    unknown = [x for x in order if x != "GPU-001" and (x not in EXP_DIR or x in CPU_EXPS)]
    if unknown:
        ap.error(f"unknown or CPU experiments {unknown} (use --cpu)")
    if DEVA == "cpu":
        order = [x for x in order if x != "GPU-001"]                 # CPU fallback: no GPU gate
    elif "GPU-001" not in order[:1]:
        order = ["GPU-001"] + [x for x in order if x != "GPU-001"]   # the gate always runs first (skips if passed)
    if a.dry_run:
        night = Night(Path("."), dry=True)
        if DEVA == "cpu":
            night.J = a.cpu_workers or 3
        return night.run(order)
    take_lock(LOCK)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    log_dir = a.log_dir or ROOT / "lab" / "runner" / "logs" / (f"night_{stamp}" if DEVA == "cuda" else f"night_pakA_cpu_{stamp}")
    night = Night(log_dir)
    if DEVA == "cpu":
        night.J = a.cpu_workers or 3
    return night.run(order)


if __name__ == "__main__":
    sys.exit(main())
