#!/bin/sh
# EXP-035 queue: EXP-020 protocol with linear lr warmup over 200 steps (freq_ban.py --warmup 200), seeds from $@
# (default 30 31 32). One job at a time via guarded_run.py; completed runs are skipped (exit 0); any other exit stops.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
S20=lab/experiments/EXP-020-data-switch/splits
O=lab/experiments/EXP-035-warmup-lockin/raw
W=200
SEEDS=${*:-30 31 32}
run() { mm=$1; shift; python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@" --warmup $W --out-root $O; rc=$?; [ $rc -eq 0 ] || { echo "[exp035] stop, rc=$rc"; exit $rc; }; }
for S in $SEEDS; do
  run 19 --seed $S --condition baseline --steps 8000 --stop-after-gen 2000 --split-file $S20/seed${S}_train_F.npy --test-file $S20/seed${S}_test.npy
  run 7 --seed $S --condition baseline --steps 2000 --stop-after-gen 8000 --split-file $S20/seed${S}_train_G.npy --test-file $S20/seed${S}_test.npy
  for T in 50 150 100 25 250; do
    run 9 --seed $S --condition baseline --steps $((T + 2000)) --stop-after-gen 8000 --split-file $S20/seed${S}_train_F.npy \
      --test-file $S20/seed${S}_test.npy --switch-split-file $S20/seed${S}_train_G.npy --switch-step $T
  done
done
echo "[exp035] all done"
