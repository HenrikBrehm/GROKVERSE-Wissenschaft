"""Night report (session 10): summarise a queue log and the current verdicts, read-only (no training, no tests).

Lists guard refusals, failed/stopped parts, completed runs per experiment prefix and the verdict fields of each
experiment's summary.json, so a new session sees in one call what the night queue produced.
Usage: python lab/tools/night_report.py [lab/runner/logs/queue_s10.log]
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
EXPS = ("EXP-035-warmup-lockin", "EXP-038-where-lockin", "EXP-036-init-conflict", "EXP-039-lr-clock",
        "EXP-040-we-init-scale", "EXP-034-phase2-optimizer", "EXP-042-bias-strength", "EXP-041-imprint",
        # session 13: GPU queue (queue_gpu_s11.sh); GPU-001 writes verdict_*.json instead of summary.json
        "GPU-001-equivalence", "EXP-043-generalize-steering", "EXP-046-dihedral-steering", "EXP-047-marginal-control",
        "EXP-048-intadd-steering", "EXP-049-width-steering", "EXP-044-generalize-lockin", "EXP-045-mlp-steering")
# run-completion lines: freq_ban.py "[exp]", group_train.py "[g]", intadd_train.py "[i]", width_train.py "[w]"
DONE = re.compile(r"\[(?:exp|g|i|w)\] (\S+) completed:")
PROBLEM = re.compile(r"REFUSED|failed|stop|Traceback|Error|nan", re.I)


def log_summary(path: Path) -> None:
    if not path.exists():
        print(f"[log] {path} not found")
        return
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    done = Counter()
    for ln in lines:
        m = DONE.match(ln)
        if m:
            done[re.split(r"_baseline|_seed|_d\d", m.group(1))[0]] += 1
    print(f"[log] {path.name}: {len(lines)} lines; completed runs by exp_id prefix: {dict(done)}")
    for ln in lines:
        if PROBLEM.search(ln) and "completed (exit 0)" not in ln:
            print("  !", ln[:200])
    print("  last line:", lines[-1][:200] if lines else "(empty)")


def verdicts(obj, prefix: str = "") -> list[str]:
    """All keys named like a verdict/class anywhere in a summary (without the per-run rows)."""
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "rows":
                continue
            if any(w in k.lower() for w in ("verdict", "class", "p36b", "n_", "successes", "pass")) and not isinstance(v, (dict, list)):
                out.append(f"{prefix}{k} = {v}")
            elif isinstance(v, (dict, list)) and k not in ("rows",):
                out += verdicts(v, f"{prefix}{k}.")
    return out


def program_status() -> None:
    """Session 13: newest night_program status files (GPU: night_*, CPU: night_cpu_*)."""
    logs = LAB / "runner" / "logs"
    for prefix in ("night_2", "night_cpu_"):
        dirs = sorted(d for d in logs.glob(f"{prefix}*") if (d / "night_status.json").exists())
        if not dirs:
            print(f"[program] no {prefix.rstrip('_2') or 'night'} status yet")
            continue
        st = json.loads((dirs[-1] / "night_status.json").read_text(encoding="utf-8"))
        print(f"[program] {dirs[-1].name}: {st.get('result', 'running')} (updated {st.get('updated_utc')})")
        for name, e in st.get("experiments", {}).items():
            print(f"  {name}: {e.get('state')}")


def main() -> None:
    program_status()
    log_summary(Path(sys.argv[1]) if len(sys.argv) > 1 else LAB / "runner" / "logs" / "queue_s10.log")
    for e in EXPS:
        d = LAB / "experiments" / e
        files = sorted(d.glob("summary*.json")) + sorted(d.glob("verdict*.json"))
        for f in files:
            try:
                v = verdicts(json.loads(f.read_text(encoding="utf-8")))
            except (OSError, ValueError) as ex:
                v = [f"unreadable: {type(ex).__name__}"]
            print(f"[{e}/{f.name}] " + ("; ".join(v[:12]) if v else "(no verdict fields)"))
        if not files:
            print(f"[{e}] no summary yet")


if __name__ == "__main__":
    main()
