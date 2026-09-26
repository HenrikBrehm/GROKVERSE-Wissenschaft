#!/bin/sh
# EXP-038 queue: EXP-020 protocol at t = 150 (F committed in 5/5 seeds), but at the switch either W_E ("we") or all
# other parameters ("rest") are reset to their init incl. AdamW state (freq_ban.py --reset-at-switch). Seeds 30-34.
# Fresh smoke first (fail-closed). One job at a time via guarded_run.py; completed runs skipped; any other exit stops.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
S20=lab/experiments/EXP-020-data-switch/splits
O=lab/experiments/EXP-038-where-lockin/raw
SM=lab/experiments/EXP-038-where-lockin/raw_smoke
run() { mm=$1; shift; python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@" --out-root $O; rc=$?; [ $rc -eq 0 ] || { echo "[exp038] stop, rc=$rc"; exit $rc; }; }
for R in we rest; do
  python lab/tools/guarded_run.py --min-minutes 2 -- python $F --seed 30 --condition baseline --steps 40 --stop-after-gen 8000 \
    --split-file $S20/seed30_train_F.npy --test-file $S20/seed30_test.npy --switch-split-file $S20/seed30_train_G.npy \
    --switch-step 30 --reset-at-switch $R --force --out-root $SM || { echo "[exp038] smoke $R failed"; exit 1; }
done
python lab/experiments/EXP-038-where-lockin/check_smoke.py || { echo "[exp038] smoke check failed"; exit 1; }
for R in we rest; do
  for S in 30 31 32 33 34; do
    run 7 --seed $S --condition baseline --steps 2150 --stop-after-gen 8000 --split-file $S20/seed${S}_train_F.npy \
      --test-file $S20/seed${S}_test.npy --switch-split-file $S20/seed${S}_train_G.npy --switch-step 150 \
      --reset-at-switch $R --save-model
  done
done
echo "[exp038] all done"
