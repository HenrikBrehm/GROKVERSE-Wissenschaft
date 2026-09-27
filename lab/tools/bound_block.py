"""Shared freezing and run binding for confirmation blocks registered from session 22 on (N28, P2b). Session 22, UNTESTED.

The logic is the one of confirm_p3 (session 21, Codex-reviewed), parametrised by a Block instead of module globals, so that new blocks
do not copy it a third time. confirm_p1/confirm_p3 stay unchanged (they are frozen with P1-P3).

A Block names its own raw directory, bindings, code-file list, registered manifest fields, job list and run-directory rule.
  freeze:  check_manifest = manifest committed unchanged at man['commit'] + type-strict registered fields + current code hashes
  run:     run_bound = only a job of the frozen list, never on top of leftovers, code gate every POLL_S s while the trainer runs,
           binding record (sha256 of every result file) only after exit 0 with a fresh result.json
  load:    unbound(d) before and after loading; bound_bytes returns exactly the hashed bytes
"""
from __future__ import annotations

import hashlib
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
POLL_S = 2.0
UNBOUND_NAMES = ("run.lock",)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def bindable(p: Path) -> bool:
    return p.is_file() and p.name not in UNBOUND_NAMES and not p.name.endswith(".tmp")


def same_typed(a: object, b: object) -> bool:
    """Type-strict equality (1050.0, 0, True must not pass for 1050, 0.0, 1; Codex recheck s21)."""
    if type(a) is not type(b):
        return False
    if isinstance(a, list):
        return len(a) == len(b) and all(same_typed(x, y) for x, y in zip(a, b))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same_typed(a[k], b[k]) for k in a)
    return a == b


@dataclass
class Block:
    name: str
    raw: Path
    bind: Path
    code_files: tuple[str, ...]
    registered: dict
    trainer_jobs: Callable[[dict], list[str]]
    run_dir: Callable[[list[str]], Path]
    script: str                                   # repo-relative path of the block's CLI (for the job lines)
    _bound: dict = field(default_factory=dict)

    # ------------------------------------------------------------ freezing
    def code_hashes(self) -> dict[str, str]:
        files = list(self.code_files) + sorted(q.relative_to(ROOT).as_posix() for q in (ROOT / "training/grokverse").rglob("*.py")
                                               if "__pycache__" not in q.parts)
        return {f: sha(ROOT / f) for f in files}

    def check_code(self, man: dict) -> None:
        want, have = man.get("code_sha256") or {}, self.code_hashes()
        if not want:
            raise SystemExit(f"{self.name} manifest has no code_sha256")
        diff = sorted(set(want) ^ set(have)) + sorted(f for f in set(want) & set(have) if want[f] != have[f])
        if diff:
            raise SystemExit(f"executed code differs from the frozen {self.name} manifest: {diff[:5]}")

    def check_registered(self, man: dict) -> None:
        for k, v in self.registered.items():
            if not same_typed(man.get(k), v):
                raise SystemExit(f"{self.name} manifest field {k!r} differs from the registration: {man.get(k)!r} != {v!r}")

    def check_manifest(self, manifest: Path, man: dict) -> None:
        c = str(man.get("commit", "")).strip()
        if not c:
            raise SystemExit(f"{self.name} manifest has no 'commit'")
        rel = manifest.resolve().relative_to(ROOT.resolve()).as_posix()
        got = subprocess.run(["git", "show", f"{c}:{rel}"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        if got.returncode != 0:
            raise SystemExit(f"{self.name} manifest not found at commit {c}")
        strip = lambda d: {k: v for k, v in d.items() if k != "commit"}   # noqa: E731
        if strip(json.loads(got.stdout)) != strip(man):
            raise SystemExit(f"{self.name} manifest differs from its frozen version")
        self.check_registered(man)
        self.check_code(man)

    # ------------------------------------------------------------ jobs and binding
    def jobs(self, man: dict, manifest: str) -> list[str]:
        return [f"python {self.script} --run {manifest} -- {j}" for j in self.trainer_jobs(man)]

    def check_job(self, man: dict, cmd: list[str]) -> None:
        if cmd not in [shlex.split(j) for j in self.trainer_jobs(man)]:
            raise SystemExit(f"not a job of the frozen {self.name} manifest: {' '.join(cmd)[:120]}")

    @staticmethod
    def code_digest(man: dict) -> str:
        return hashlib.sha256(json.dumps(man["code_sha256"], sort_keys=True).encode()).hexdigest()

    def bound_files(self, man: dict) -> set[tuple[str, str]]:
        key = f"{man['commit']}:{self.code_digest(man)}"
        if key not in self._bound:
            ok: set[tuple[str, str]] = set()
            for b in sorted(self.bind.glob("*.json")) if self.bind.exists() else []:
                r = json.loads(b.read_text(encoding="utf-8"))
                if r.get("exit") == 0 and r.get("code_digest") == self.code_digest(man) and r.get("manifest_commit") == man["commit"]:
                    ok |= set(r.get("files", {}).items())
            self._bound[key] = ok
        return self._bound[key]

    def unbound(self, man: dict, d: Path) -> str | None:
        ok = self.bound_files(man)
        bad = [q.name for q in sorted(d.rglob("*")) if bindable(q) and (q.relative_to(ROOT).as_posix(), sha(q)) not in ok]
        return f"not bound to the frozen {self.name} code: {bad[:3]}" if bad else None

    def bound_bytes(self, man: dict, f: Path) -> bytes:
        data = f.read_bytes()
        if (f.relative_to(ROOT).as_posix(), hashlib.sha256(data).hexdigest()) not in self.bound_files(man):
            raise ValueError(f"{f.name} not bound to the frozen {self.name} code")
        return data

    @staticmethod
    def _completed(d: Path) -> bool:
        try:
            return json.loads((d / "result.json").read_text(encoding="utf-8")).get("status") == "completed"
        except (OSError, ValueError, AttributeError):
            return False

    def _run_gated(self, man: dict, cmd: list[str], check: bool = True) -> tuple[int, str | None]:
        pyc = str(Path(tempfile.gettempdir()) / f"confirm_pyc_{self.code_digest(man)[:16]}")
        proc = subprocess.Popen(cmd, cwd=ROOT, env={**os.environ, "PYTHONPYCACHEPREFIX": pyc})
        try:
            while True:
                try:
                    rc = proc.wait(timeout=POLL_S)
                    break
                except subprocess.TimeoutExpired:
                    if not check:
                        continue
                    try:
                        self.check_code(man)
                    except SystemExit as ex:
                        proc.kill()
                        return proc.wait(), str(ex)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
        if not check:
            return rc, None
        try:
            self.check_code(man)
        except SystemExit as ex:
            return rc, str(ex)
        return rc, None

    def run_bound(self, manifest: Path, cmd: list[str], gates: bool = True) -> int:
        """gates=False only in selftests (skips manifest, job and code checks)."""
        tag = f"[{self.name}]"
        man = json.loads(manifest.read_text(encoding="utf-8"))
        if gates:
            self.check_manifest(manifest, man)
            self.check_job(man, cmd)
        d = self.run_dir(cmd)
        if (d / "result.json").exists():
            if self.unbound(man, d) is None and self._completed(d):
                print(f"{tag} {d.name} already bound, skipped", flush=True)
                return 0
            try:
                done = json.loads((d / "result.json").read_text(encoding="utf-8")).get("status") == "completed"
            except (OSError, ValueError):
                done = False
            if done:
                print(f"{tag} {d.name}: completed but not bound; refused", file=sys.stderr, flush=True)
                return 4
        if (d / "run.lock").exists():
            print(f"{tag} {d.name}: run.lock present (live or crashed trainer); refused, check by hand", file=sys.stderr, flush=True)
            return 4
        if d.exists():
            aside = d.with_name(f"{d.name}.stale_{time.time_ns()}")
            d.rename(aside)
            print(f"{tag} unfinished/unbound leftover moved to {aside.name}", file=sys.stderr, flush=True)
        t0 = time.time_ns()
        rc, changed = self._run_gated(man, cmd, check=gates)
        if changed:
            print(f"{tag} code changed during the run, no binding: {changed}", file=sys.stderr, flush=True)
            return 4
        files = ({q.relative_to(ROOT).as_posix(): sha(q) for q in sorted(d.rglob("*")) if bindable(q)}
                 if rc == 0 and d.exists() else {})
        if rc == 0 and not any(k.endswith("/result.json") for k in files):
            print(f"{tag} {d.name}: no new result.json, nothing usable bound", file=sys.stderr, flush=True)
            rc = 4
        if rc == 0 and not self._completed(d):             # Codex s22: bind only runs the trainer marked completed
            print(f"{tag} {d.name}: result.json not 'completed', nothing bound", file=sys.stderr, flush=True)
            rc = 4
        self.bind.mkdir(parents=True, exist_ok=True)
        rec = {"code_digest": self.code_digest(man), "manifest_commit": man["commit"], "cmd": cmd, "exit": rc, "t0_ns": t0,
               "t1_ns": time.time_ns(), "run_dir": d.name, "files": files if rc == 0 else {}}
        with open(self.bind / f"{hashlib.sha256(' '.join(cmd).encode()).hexdigest()[:16]}_{t0}_{os.getpid()}.json", "x", encoding="utf-8") as f:
            json.dump(rec, f, indent=1)
        self._bound.clear()
        return rc

    # ------------------------------------------------------------ CLI
    def cli(self, argv: list[str], analyze: Callable[[Path], None], write_splits: Callable[[dict], None], selftest: Callable[[], None]) -> None:
        if argv == ["--selftest"]:
            selftest()
        elif argv == ["--hash-code"]:
            print(json.dumps(self.code_hashes(), indent=1))
        elif len(argv) == 2 and argv[0] in ("--splits", "--jobs", "--analyze"):
            if argv[0] == "--analyze":
                analyze(Path(argv[1]))
                return
            m = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
            self.check_manifest(Path(argv[1]), m)
            if argv[0] == "--splits":
                write_splits(m)
            else:
                print("\n".join(self.jobs(m, Path(argv[1]).resolve().relative_to(ROOT.resolve()).as_posix())))
        elif len(argv) >= 4 and argv[0] == "--run" and argv[2] == "--":
            raise SystemExit(self.run_bound(Path(argv[1]), argv[3:]))
        else:
            raise SystemExit("usage: --selftest | --hash-code | --splits M | --jobs M | --analyze M | --run M -- <trainer command>")


def selftest_binding(block: Block, job_a: str, job_b: str, job_c: str) -> None:
    """Binding behaviour on fake trainers in a temporary raw/bind directory (three distinct job lines of the block)."""
    keep = block.raw, block.bind, block.run_dir
    old_raw = block.raw
    try:
        with tempfile.TemporaryDirectory(dir=LAB / "confirm") as tmp:
            block.raw, block.bind = Path(tmp) / "raw", Path(tmp) / "b"
            block.run_dir = lambda cmd, f=keep[2]: block.raw / f(cmd).relative_to(old_raw)   # noqa: E731
            m2 = {"commit": "c0", "code_sha256": {"a": "1"}}
            mf = Path(tmp) / "m.json"
            mf.write_text(json.dumps(m2))
            mk = "import pathlib, sys; d = pathlib.Path(sys.argv[1]); d.mkdir(parents=True); (d / 'result.json').write_text('{\"status\": \"completed\"}')"
            cmd = shlex.split(job_a)
            d = block.run_dir(cmd)
            fake = [sys.executable, "-c", mk, d.as_posix()] + cmd[2:]
            assert block.run_dir(fake) == d
            assert block.run_bound(mf, fake, gates=False) == 0
            assert block.unbound(m2, d) is None
            assert block.run_bound(mf, fake, gates=False) == 0                         # already bound -> skipped
            (d / "result.json").write_text('{"status": "completed", "x": 1}')
            block._bound.clear()
            assert "result.json" in block.unbound(m2, d) and block.run_bound(mf, fake, gates=False) == 4
            assert block.run_bound(mf, [sys.executable, "-c", "pass"] + shlex.split(job_b)[2:], gates=False) == 4   # no result.json
            half = "import pathlib, sys; d = pathlib.Path(sys.argv[1]); d.mkdir(parents=True); (d / 'result.json').write_text('{}')"
            hb = block.run_dir(shlex.split(job_b))
            assert block.run_bound(mf, [sys.executable, "-c", half, hb.as_posix()] + shlex.split(job_b)[2:], gates=False) == 4   # not completed
            assert block.unbound(m2, hb) is not None
            for q in hb.rglob("*"):
                q.unlink()
            hb.rmdir()
            last = max(block.bind.glob("*.json"), key=lambda q: int(q.name.split("_")[1]))
            assert json.loads(last.read_text())["exit"] == 4
            left = block.run_dir(shlex.split(job_c))                                    # unfinished leftover -> moved aside
            left.mkdir(parents=True)
            (left / "result.json").write_text('{"status": "running"}')
            assert block.run_bound(mf, [sys.executable, "-c", mk, left.as_posix()] + shlex.split(job_c)[2:], gates=False) == 0
            assert list(block.raw.glob(left.name + ".stale_*")) and block.unbound(m2, left) is None
            locked = block.run_dir(shlex.split(job_b))                                  # run.lock -> refused, nothing renamed
            if locked.exists():
                for q in locked.rglob("*"):
                    q.unlink()
            locked.mkdir(parents=True, exist_ok=True)
            (locked / "run.lock").write_text("{}")
            assert block.run_bound(mf, [sys.executable, "-c", "pass"] + shlex.split(job_b)[2:], gates=False) == 4 and locked.exists()
            data = (left / "result.json").read_bytes()
            assert block.bound_bytes(m2, left / "result.json") == data
            try:
                block.bound_bytes(m2, locked / "run.lock")
                raise AssertionError("unbound bytes accepted")
            except ValueError:
                pass
    finally:
        block.raw, block.bind, block.run_dir = keep
        block._bound.clear()
    assert same_typed([1, [2, 3]], [1, [2, 3]]) and not same_typed([1.0], [1]) and not same_typed(True, 1) and not same_typed({"a": 1}, {"a": 1.0})
