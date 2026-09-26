#!/bin/sh
# EXP-022 queue (prepared session 5, NOT yet run). One job at a time, every run through guarded_run.py; stops on every
# nonzero exit (completed runs are skipped with exit 0). Resume: start again. Run after queue_s5.sh.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
X=lab/experiments/EXP-022-single-frequency
SP=$X/splits
run() {
  mm=$1; shift
  python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@"
  rc=$?
  if [ $rc -ne 0 ]; then echo "[queue22] stop, rc=$rc"; exit $rc; fi
}
while ps -ef | grep -v grep | grep -q "guarded_run.py"; do sleep 10; done
for S in 40 41 42 43 44; do
  for A in S1 S5 R; do
    run 19 --seed $S --condition baseline --steps 8000 --stop-after-gen 2000 \
      --split-file $SP/seed${S}_train_$A.npy --test-file $SP/seed${S}_test.npy --out-root $X/raw
  done
done
echo "[queue22] all done"
