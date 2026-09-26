#!/bin/sh
# Session-5 queue (prepared 2026-09-26, NOT yet run; replaces queue_s4b.sh, same runs plus EXP-018/020, new order).
# One job at a time; every run through guarded_run.py; completed runs are skipped (freq_ban.py exits 0), so the
# queue stops on EVERY nonzero exit (guard refusal 3, timeout 124, or a real error). Resume: start this script again.
# Order (priority): EXP-016 seeds 16-19 (decision) -> EXP-003d baselines 18, 19 (EXP-015/019) -> smokes EXP-018/020
# -> EXP-018 seeds 20-24 -> EXP-014 crosses -> EXP-020 -> EXP-023 -> EXP-022 (their own queue scripts)
# -> EXP-018 seeds 25-29 -> EXP-010 swaps 11-19.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
R=lab/experiments
S16=$R/EXP-016-engineered-split/splits
S18=$R/EXP-018-split-speed/splits
S20=$R/EXP-020-data-switch/splits
run() {   # $1 = minimum minutes, rest = freq_ban arguments
  mm=$1; shift
  python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@"
  rc=$?
  if [ $rc -ne 0 ]; then echo "[queue5] stop, rc=$rc"; exit $rc; fi
}
exp018() {
  for S in "$@"; do for A in E D R; do
    run 19 --seed $S --condition baseline --steps 8000 --stop-after-gen 25 --split-file $S18/seed${S}_train_$A.npy \
      --test-file $S18/seed${S}_test.npy --out-root $R/EXP-018-split-speed/raw
  done; done
}
while ps -ef | grep -v grep | grep -q "guarded_run.py"; do sleep 10; done
for S in 16 17 18 19; do
  run 7 --seed $S --condition baseline --steps 2000 --split-file $S16/split_seed${S}_eps2.0.npy --out-root $R/EXP-016-engineered-split/raw
  run 7 --seed $S --condition baseline --steps 2000 --split-file $S16/split_seed${S}_eps2.0_G.npy --out-root $R/EXP-016-engineered-split/raw
done
for S in 18 19; do
  run 33 --seed $S --condition baseline --stop-after-gen 25 --out-root $R/EXP-003-early-prediction/raw_d
done
run 3 --seed 20 --condition baseline --steps 50 --split-file $S18/seed20_train_E.npy --test-file $S18/seed20_test.npy \
  --out-root $R/EXP-018-split-speed/raw_smoke
run 3 --seed 30 --condition baseline --steps 60 --stop-after-gen 8000 --split-file $S20/seed30_train_F.npy \
  --test-file $S20/seed30_test.npy --switch-split-file $S20/seed30_train_G.npy --switch-step 30 \
  --out-root $R/EXP-020-data-switch/raw_smoke
python $R/EXP-020-data-switch/check_smoke.py || { echo "[queue5] EXP-020 smoke check failed"; exit 1; }
# Session 7 (2026-09-26): EXP-020 moved before EXP-018/EXP-014; its no-switch arms also confirm EXP-028.
for S in 30 31 32 33 34; do
  run 19 --seed $S --condition baseline --steps 8000 --stop-after-gen 2000 --split-file $S20/seed${S}_train_F.npy \
    --test-file $S20/seed${S}_test.npy --out-root $R/EXP-020-data-switch/raw
  run 7 --seed $S --condition baseline --steps 2000 --stop-after-gen 8000 --split-file $S20/seed${S}_train_G.npy \
    --test-file $S20/seed${S}_test.npy --out-root $R/EXP-020-data-switch/raw
  for T in 150 50 25 10 400 1000; do   # 10, 25: EXP-020 Nachtrag b
    run 9 --seed $S --condition baseline --steps $((T + 2000)) --stop-after-gen 8000 \
      --split-file $S20/seed${S}_train_F.npy --test-file $S20/seed${S}_test.npy \
      --switch-split-file $S20/seed${S}_train_G.npy --switch-step $T --out-root $R/EXP-020-data-switch/raw
  done
done
exp018 20 21 22 23 24
for P in "10 11" "11 10" "12 13" "13 12" "14 15" "15 14" "16 17" "17 16" "18 19" "19 18"; do
  set -- $P
  run 33 --seed $1 --split-seed $2 --condition baseline --stop-after-gen 25 --out-root $R/EXP-014-split-vs-init/raw
done
sh lab/experiments/EXP-023-split-value/queue.sh || { rc=$?; echo "[queue5] EXP-023 stop, rc=$rc"; exit $rc; }
sh lab/experiments/EXP-022-single-frequency/queue.sh || { rc=$?; echo "[queue5] EXP-022 stop, rc=$rc"; exit $rc; }
exp018 25 26 27 28 29
for S in 11 12 13 14 15 16 17 18 19; do
  run 33 --seed $S --condition init_swap --stop-after-gen 25 --out-root $R/EXP-010-init-swap/raw
done
echo "[queue5] all done"
