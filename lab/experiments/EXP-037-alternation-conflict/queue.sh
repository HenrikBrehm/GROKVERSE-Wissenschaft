#!/bin/sh
# EXP-037 queue (Nachtrag a): EXP-020 splits/inits of seeds 30-32. Arms: F/G blocks of A steps (A = 5 primary, 25
# secondary) for steps 1..200 then G for 2000 (--alternate-every A --switch-step 200); control C_F100: F for 100 steps,
# then G for 2100 (--switch-step 100, total 2200). Fresh behavioural smoke first (fail-closed).
# One job at a time via guarded_run.py; completed runs are skipped (exit 0); any other exit stops. Resume = rerun.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
S20=lab/experiments/EXP-020-data-switch/splits
O=lab/experiments/EXP-037-alternation-conflict/raw
SM=lab/experiments/EXP-037-alternation-conflict/raw_smoke
run() { mm=$1; shift; python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@" --out-root $O; rc=$?; [ $rc -eq 0 ] || { echo "[exp037] stop, rc=$rc"; exit $rc; }; }
# smoke (always fresh, --force): 30 steps, A = 5, switch at 20 -> training set after steps 5, 10, 15 must be G, F, G
python lab/tools/guarded_run.py --min-minutes 2 -- python $F --seed 30 --condition baseline --steps 30 --stop-after-gen 8000 \
  --split-file $S20/seed30_train_F.npy --test-file $S20/seed30_test.npy --switch-split-file $S20/seed30_train_G.npy \
  --switch-step 20 --alternate-every 5 --force --out-root $SM || { echo "[exp037] smoke failed"; exit 1; }
python lab/experiments/EXP-037-alternation-conflict/check_smoke.py || { echo "[exp037] smoke check failed"; exit 1; }
for S in 30 31 32; do
  run 7 --seed $S --condition baseline --steps 2200 --stop-after-gen 8000 --split-file $S20/seed${S}_train_F.npy \
    --test-file $S20/seed${S}_test.npy --switch-split-file $S20/seed${S}_train_G.npy --switch-step 200 --alternate-every 5
done
for S in 30 31 32; do   # control C_F100
  run 7 --seed $S --condition baseline --steps 2200 --stop-after-gen 8000 --split-file $S20/seed${S}_train_F.npy \
    --test-file $S20/seed${S}_test.npy --switch-split-file $S20/seed${S}_train_G.npy --switch-step 100
done
for S in 30 31 32; do
  run 7 --seed $S --condition baseline --steps 2200 --stop-after-gen 8000 --split-file $S20/seed${S}_train_F.npy \
    --test-file $S20/seed${S}_test.npy --switch-split-file $S20/seed${S}_train_G.npy --switch-step 200 --alternate-every 25
done
echo "[exp037] all done"
