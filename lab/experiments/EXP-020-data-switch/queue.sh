#!/bin/sh
# EXP-020 queue (prepared session 5, NOT yet run). One job at a time, every run through guarded_run.py;
# completed runs are skipped by freq_ban.py. Resume: start again. Order: smoke, then per seed t = inf, 0, 150, 50, 400, 1000.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
X=lab/experiments/EXP-020-data-switch
SP=$X/splits
run() {
  mm=$1; shift
  python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@"
  rc=$?
  if [ $rc -eq 3 ] || [ $rc -eq 124 ]; then echo "[queue20] stop, rc=$rc"; exit $rc; fi
}
while ps -ef | grep -v grep | grep -q "guarded_run.py"; do sleep 10; done
COMMON="--condition baseline --steps 2000 --stop-after-gen 2000 --out-root $X/raw"
run 3 --seed 30 --condition baseline --steps 60 --stop-after-gen 2000 --split-file $SP/seed30_train_F.npy \
  --test-file $SP/seed30_test.npy --switch-split-file $SP/seed30_train_G.npy --switch-step 30 --out-root $X/raw_smoke
for S in 30 31 32 33 34; do
  run 7 --seed $S $COMMON --split-file $SP/seed${S}_train_F.npy --test-file $SP/seed${S}_test.npy
  run 7 --seed $S $COMMON --split-file $SP/seed${S}_train_G.npy --test-file $SP/seed${S}_test.npy
  for T in 150 50 400 1000; do
    run 7 --seed $S $COMMON --split-file $SP/seed${S}_train_F.npy --test-file $SP/seed${S}_test.npy \
      --switch-split-file $SP/seed${S}_train_G.npy --switch-step $T
  done
done
echo "[queue20] all done"
