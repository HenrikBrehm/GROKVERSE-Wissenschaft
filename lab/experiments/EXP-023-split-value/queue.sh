#!/bin/sh
# EXP-023 queue (prepared session 5, NOT yet run). Needs the EXP-003d baselines (queue_s5.sh runs 18, 19).
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
run 3 --seed 10 --condition baseline --steps 50 --split-value --out-root $X/raw_smoke
for S in 10 11 12 13 14 15 16 17 18 19; do
  run 33 --seed $S --condition baseline --stop-after-gen 25 --split-value --out-root $X/raw
done
echo "[queue23] all done"
