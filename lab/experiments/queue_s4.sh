#!/bin/sh
# Session-4 job queue (one job at a time, every run through guarded_run.py).
# Order (scheduling only, no criteria change): remaining EXP-003d baselines first, because
# EXP-010, EXP-012 phase 2 and EXP-014 all need them; then EXP-014 crosses; then EXP-010 swaps.
# A run starts only if the guard grants >= 33 min; when refused, EXP-013 (≈ 7 min) gets the rest.
# Completed runs are skipped by freq_ban.py (exit 1 "already completed").
# Resume: start this script again.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
R=lab/experiments
tail_job() {
  python lab/tools/guarded_run.py --min-minutes 12 -- python $R/EXP-013-lockin-curve/lockin.py \
    > lab/runner/logs/lockin_s4.log 2>&1
  echo "[queue] lockin rc=$?"
}
run() {
  python lab/tools/guarded_run.py --min-minutes 33 -- python $F "$@"
  rc=$?
  if [ $rc -eq 3 ] || [ $rc -eq 124 ]; then echo "[queue] stop, rc=$rc"; tail_job; exit $rc; fi
}
# wait for a run that is still in progress from the previous loop (one job at a time)
while ps -ef | grep -v grep | grep -q "guarded_run.py"; do sleep 10; done
for S in 11 12 13 14 15 16 17 18 19; do
  run --seed $S --condition baseline --stop-after-gen 25 --out-root $R/EXP-003-early-prediction/raw_d
done
for S in 10 11 12 13 14 15 16 17 18 19; do
  J=$(( S == 19 ? 10 : S + 1 ))
  run --seed $S --split-seed $J --condition baseline --stop-after-gen 25 --out-root $R/EXP-014-split-vs-init/raw
done
for S in 11 12 13 14 15 16 17 18 19; do
  run --seed $S --condition init_swap --stop-after-gen 25 --out-root $R/EXP-010-init-swap/raw
done
echo "[queue] all done"
tail_job
