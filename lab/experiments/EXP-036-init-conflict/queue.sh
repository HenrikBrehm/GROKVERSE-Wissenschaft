#!/bin/sh
# EXP-036 queue: EXP-020 splits of seeds 30-32 with a NEW init (seed + 100); runs only F, only G (2000 steps each)
# and switches F -> G at t = 10, 25, 50 (+2000 G steps). One job at a time via guarded_run.py; completed runs are
# skipped (exit 0); any other exit stops. Resume = rerun.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
S20=lab/experiments/EXP-020-data-switch/splits
O=lab/experiments/EXP-036-init-conflict/raw
run() { mm=$1; shift; python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@" --out-root $O; rc=$?; [ $rc -eq 0 ] || { echo "[exp036] stop, rc=$rc"; exit $rc; }; }
for S in 30 31 32; do
  I=$((S + 100))
  run 7 --seed $I --condition baseline --steps 2000 --stop-after-gen 8000 --split-file $S20/seed${S}_train_F.npy --test-file $S20/seed${S}_test.npy
  run 7 --seed $I --condition baseline --steps 2000 --stop-after-gen 8000 --split-file $S20/seed${S}_train_G.npy --test-file $S20/seed${S}_test.npy
  for T in 25 50 10; do
    run 7 --seed $I --condition baseline --steps $((T + 2000)) --stop-after-gen 8000 --split-file $S20/seed${S}_train_F.npy \
      --test-file $S20/seed${S}_test.npy --switch-split-file $S20/seed${S}_train_G.npy --switch-step $T
  done
done
echo "[exp036] all done"
