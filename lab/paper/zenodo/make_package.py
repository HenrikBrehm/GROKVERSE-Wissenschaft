"""Build the Zenodo package (rule 20d) from git-tracked files at a given commit. NEVER uploads anything.

  python lab/paper/zenodo/make_package.py --dry-run            # list files, sizes and totals, write nothing
  python lab/paper/zenodo/make_package.py --commit <sha>       # ZIP + SHA256SUMS under lab/paper/zenodo/out/ (untracked)

Only files tracked by git at the commit are packed (git archive semantics via `git show <sha>:<path>`), so untracked raw runs,
user runner files and lab/external are excluded by construction. Patterns below follow README.md in this folder.
"""
from __future__ import annotations

import fnmatch
import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INCLUDE = ("lab/paper/draft_short.md", "lab/paper/draft.md", "lab/paper/related_work.md", "lab/paper/repro/*.py",
           "lab/paper/repro/README.md", "lab/paper/figures/*", "lab/confirm/*REGISTRATION*.md", "lab/confirm/*_manifest.json",
           "lab/confirm/*_summary.json", "lab/confirm/*_splits/*", "lab/confirm/splits/*", "lab/tools/confirm_*.py",
           "lab/tools/bound_block.py", "lab/tools/result_loader.py", "lab/tools/trainer_guard.py", "lab/tools/paket_a_device.py",
           "lab/experiments/EXP-001-freq-ban/freq_ban.py", "training/grokverse/*.py", "training/grokverse/*/*.py", "lab/FINDINGS.md",
           # s49: experiment modules the confirm_* tools and repro scripts import (split construction, group power, ablations)
           "lab/experiments/EXP-043-generalize-steering/analyze.py", "lab/experiments/EXP-043-generalize-steering/make_split.py",
           "lab/experiments/EXP-046-dihedral-steering/dihedral.py", "lab/experiments/EXP-046-dihedral-steering/group_train.py",
           "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-051-functional-ablation/analyze.py",
           "lab/experiments/EXP-053-p3-overlap-design/overlap_split.py",
           "lab/experiments/EXP-053-p3-overlap-design/calibration.json", "lab/experiments/EXP-055-ablation-dose/analyze.py",
           # s51: generated manuscript + references; LM1 block (appendix K): trainer, loader, split design, analyses
           "lab/paper/manuscript.md", "lab/paper/build_manuscript.py", "lab/paper/references.md",
           "lab/confirm/confirm_lm1.py", "lab/confirm/LM1_independent_recompute.py",
           "lab/experiments/EXP-105-lm-ladder-stage2/lm_stage2.py", "lab/experiments/EXP-105-lm-ladder-stage2/analyze_pilot.py",
           "lab/experiments/EXP-102-lm-ladder-stage1/design.py", "lab/experiments/EXP-102-lm-ladder-stage1/analyze.py",
           # s52: untested LaTeX export of the manuscript (Overleaf)
           "lab/paper/build_tex.py", "lab/paper/tex/*",
           # s54: LM1-F (functional ablation of the LM1 models) and its independent recompute
           "lab/confirm/confirm_lm1f.py", "lab/confirm/LM1F_independent_recompute.py")
EXCLUDE = ("*/__pycache__/*", "lab/runner/*", "lab/external/*", "*_raw/*", "*/raw/*", "lab/paper/repro/out/*", "lab/paper/outreach/*")


def tracked(commit: str) -> list[str]:
    out = subprocess.run(["git", "ls-tree", "-r", "--name-only", commit], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    files = [f for f in out.splitlines() if any(fnmatch.fnmatch(f, pat) for pat in INCLUDE)]
    return sorted(f for f in files if not any(fnmatch.fnmatch(f, pat) for pat in EXCLUDE))


def blob(commit: str, path: str) -> bytes:
    return subprocess.run(["git", "show", f"{commit}:{path}"], cwd=ROOT, capture_output=True, check=True).stdout


def main(argv: list[str]) -> None:
    dry = "--dry-run" in argv
    commit = argv[argv.index("--commit") + 1] if "--commit" in argv else "HEAD"
    files = tracked(commit)
    sizes = {f: len(blob(commit, f)) for f in files}
    total = sum(sizes.values())
    print(f"[package] commit {commit}: {len(files)} files, {total / 2**20:.1f} MB")
    if dry:
        for f in files[:40]:
            print(f"  {sizes[f]:>10}  {f}")
        if len(files) > 40:
            print(f"  ... {len(files) - 40} more")
        return
    out = ROOT / "lab/paper/zenodo/out"
    out.mkdir(exist_ok=True)
    sha = subprocess.run(["git", "rev-parse", "--short", commit], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    zp = out / f"grokverse_lab_{sha}.zip"
    lines = []
    with zipfile.ZipFile(zp, "x", compression=zipfile.ZIP_DEFLATED) as z:
        for f in files:
            b = blob(commit, f)
            z.writestr(f, b)
            lines.append(f"{hashlib.sha256(b).hexdigest()}  {f}")
        z.writestr("SHA256SUMS", "\n".join(lines) + "\n")
        z.writestr("COMMIT", sha + "\n")
    print(f"[package] wrote {zp} (not uploaded)")


if __name__ == "__main__":
    main(sys.argv[1:])
