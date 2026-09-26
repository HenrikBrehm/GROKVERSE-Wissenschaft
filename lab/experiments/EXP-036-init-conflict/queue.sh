#!/bin/sh
# EXP-036 queue (Nachtrag a): 7 (split, new init) pairs: splits 30-34 with init s+100, splits 30, 31 with init s+200;
# runs only F, only G (2000 steps each)
# and switches F -> G at t = 10, 25, 50 (+2000 G steps). One job at a time via guarded_run.py; completed runs are
# skipped (exit 0); any other exit stops. Resume = rerun.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
S20=lab/experiments/EXP-020-data-switch/splits
O=lab/experiments/EXP-036-init-conflict/raw
run() { mm=$1; shift; python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@" --spectra-at $SA --out-root $O; rc=$?; [ $rc -eq 0 ] || { echo "[exp036] stop, rc=$rc"; exit $rc; }; }
# Nachtrag d: early W_E spectra (logging only) for the calibrated P36b test; fail-closed smoke of --spectra-at first
SA=5,10,15,20,25,30,40,50,75,100,150,200
python lab/tools/guarded_run.py --min-minutes 2 -- python $F --seed 130 --condition baseline --steps 30 --stop-after-gen 8000   --split-file $S20/seed30_train_F.npy --test-file $S20/seed30_test.npy --spectra-at 5,10,20 --force   --out-root lab/experiments/EXP-036-init-conflict/raw_smoke || { echo "[exp036] smoke failed"; exit 1; }
python -c "import numpy as n,glob,sys;s=n.load(glob.glob('lab/experiments/EXP-036-init-conflict/raw_smoke/*/spectra_steps.npy')[0]).tolist();sys.exit(0 if s==[0,5,10,20,30] else 1)"   || { echo "[exp036] smoke check failed"; exit 1; }
for P in 30:130 31:131 32:132 33:133 34:134 30:230 31:231; do
  S=${P%%:*}; I=${P##*:}
  run 7 --seed $I --condition baseline --steps 2000 --stop-after-gen 8000 --split-file $S20/seed${S}_train_F.npy --test-file $S20/seed${S}_test.npy
  run 7 --seed $I --condition baseline --steps 2000 --stop-after-gen 8000 --split-file $S20/seed${S}_train_G.npy --test-file $S20/seed${S}_test.npy
  for T in 25 50 10; do
    run 7 --seed $I --condition baseline --steps $((T + 2000)) --stop-after-gen 8000 --split-file $S20/seed${S}_train_F.npy \
      --test-file $S20/seed${S}_test.npy --switch-split-file $S20/seed${S}_train_G.npy --switch-step $T
  done
done
echo "[exp036] all done"
