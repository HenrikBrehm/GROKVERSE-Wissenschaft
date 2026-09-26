#!/bin/sh
# EXP-023 queue (design after Nachtrag a, Codex review 2026-09-26; NOT yet run). Fresh seeds 50-59, three arms
# (plain baseline, --split-value rand, --split-value copy), all exactly 3000 steps without early stop.
# One job at a time, every run through guarded_run.py; stops on every nonzero exit (completed runs exit 0).
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
X=lab/experiments/EXP-023-split-value
run() {
  mm=$1; shift
  python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@"
  rc=$?
  if [ $rc -ne 0 ]; then echo "[queue23] stop, rc=$rc"; exit $rc; fi
}
while ps -ef | grep -v grep | grep -q "guarded_run.py"; do sleep 10; done
run 3 --seed 50 --condition baseline --steps 50 --split-value rand --out-root $X/raw_smoke
COMMON="--condition baseline --steps 3000 --stop-after-gen 100000 --out-root $X/raw"
for S in 50 51 52 53 54 55 56 57 58 59; do
  run 9 --seed $S $COMMON
  run 9 --seed $S $COMMON --split-value rand
  run 9 --seed $S $COMMON --split-value copy
done
echo "[queue23] all done"
