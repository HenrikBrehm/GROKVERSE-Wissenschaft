#!/bin/sh
# Session-4 queue, version b (03:30 Berlin): reorder only, no criteria change.
# 1) EXP-003d baselines 12-17 (with 10, 11 done: 8 baselines -> EXP-012/015 phase 2 evaluable)
# 2) EXP-016 smoke (50 steps), then EXP-016 arms F and G for seeds 10-19 (2000 steps each)
# 3) EXP-003d baselines 18, 19; EXP-014 crosses (disjoint pairs, both directions); EXP-010 swaps 11-19
# 4) EXP-013 lock-in curve when the guard refuses long runs.
# One job at a time; each run through guarded_run.py; completed runs are skipped by freq_ban.py.
# Resume: start this script again.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
R=lab/experiments
SP=$R/EXP-016-engineered-split/splits
tail_job() {
  python lab/tools/guarded_run.py --min-minutes 12 -- python $R/EXP-013-lockin-curve/lockin.py \
    > lab/runner/logs/lockin_s4.log 2>&1
  echo "[queue] lockin rc=$?"
}
run() {   # $1 = minimum minutes, rest = freq_ban arguments
  mm=$1; shift
  python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@"
  rc=$?
  if [ $rc -eq 3 ] || [ $rc -eq 124 ]; then echo "[queue] stop, rc=$rc"; tail_job; exit $rc; fi
}
while ps -ef | grep -v grep | grep -q "guarded_run.py"; do sleep 10; done
for S in 12 13 14 15 16 17; do
  run 33 --seed $S --condition baseline --stop-after-gen 25 --out-root $R/EXP-003-early-prediction/raw_d
done
run 3 --seed 10 --condition baseline --steps 50 --split-file $SP/split_seed10_eps2.0.npy \
  --out-root $R/EXP-016-engineered-split/raw_smoke
for S in 10 11 12 13 14 15 16 17 18 19; do
  run 7 --seed $S --condition baseline --steps 2000 --split-file $SP/split_seed${S}_eps2.0.npy --out-root $R/EXP-016-engineered-split/raw
  run 7 --seed $S --condition baseline --steps 2000 --split-file $SP/split_seed${S}_eps2.0_G.npy --out-root $R/EXP-016-engineered-split/raw
done
for S in 18 19; do
  run 33 --seed $S --condition baseline --stop-after-gen 25 --out-root $R/EXP-003-early-prediction/raw_d
done
for P in "10 11" "11 10" "12 13" "13 12" "14 15" "15 14" "16 17" "17 16" "18 19" "19 18"; do
  set -- $P
  run 33 --seed $1 --split-seed $2 --condition baseline --stop-after-gen 25 --out-root $R/EXP-014-split-vs-init/raw
done
for S in 11 12 13 14 15 16 17 18 19; do
  run 33 --seed $S --condition init_swap --stop-after-gen 25 --out-root $R/EXP-010-init-swap/raw
done
echo "[queue] all done"
tail_job
