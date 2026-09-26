#!/bin/sh
# EXP-018 queue (prepared session 5, 2026-09-26; NOT yet run). Start only after queue_s4b.sh has finished
# (one job at a time). Every run goes through guarded_run.py; completed runs are skipped by freq_ban.py.
# Resume: start this script again. Order: smoke, then per seed E, D, R (the primary pair E/D first).
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
X=lab/experiments/EXP-018-split-speed
SP=$X/splits
run() {   # $1 = minimum minutes, rest = freq_ban arguments
  mm=$1; shift
  python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@"
  rc=$?
  if [ $rc -ne 0 ]; then echo "[queue18] stop, rc=$rc"; exit $rc; fi   # skip of a completed run exits 0
}
while ps -ef | grep -v grep | grep -q "guarded_run.py"; do sleep 10; done
run 3 --seed 20 --condition baseline --steps 50 --split-file $SP/seed20_train_E.npy \
  --test-file $SP/seed20_test.npy --out-root $X/raw_smoke
for S in 20 21 22 23 24 25 26 27 28 29; do
  for A in E D R; do
    run 19 --seed $S --condition baseline --steps 8000 --stop-after-gen 25 \
      --split-file $SP/seed${S}_train_$A.npy --test-file $SP/seed${S}_test.npy --out-root $X/raw
  done
done
echo "[queue18] all done"
