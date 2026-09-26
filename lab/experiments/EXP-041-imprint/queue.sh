#!/bin/sh
# EXP-041 queue (Nachtrag a): imprint by a 150-step prefix, EXP-018 splits (E engineered, R random, common test), seeds 20-29.
# Per seed: pure R, pure E (2150 steps, spectra also at 50/150; K at 2000 and 2150), E -> R at 150, R -> E at 150 (+2000).
# One job at a time via guarded_run.py; completed runs are skipped (exit 0); any other exit stops. Resume = rerun.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
SP=lab/experiments/EXP-018-split-speed/splits
O=lab/experiments/EXP-041-imprint/raw
run() { mm=$1; shift; python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@" --out-root $O; rc=$?; [ $rc -eq 0 ] || { echo "[exp041] stop, rc=$rc"; exit $rc; }; }
while ps -ef | grep -v grep | grep "guarded_run.py" | grep -v -q -- "--device cuda"; do sleep 10; done   # one job at a time
python lab/tools/guarded_run.py --min-minutes 1 -- python lab/experiments/EXP-041-imprint/analyze.py --selftest || { echo "[exp041] selftest failed"; exit 1; }
for S in ${*:-20 21 22 23 24 25 26 27 28 29}; do
  for A in R E; do
    run 7 --seed $S --condition baseline --steps 2150 --stop-after-gen 8000 --split-file $SP/seed${S}_train_$A.npy --test-file $SP/seed${S}_test.npy --spectra-at 50,150
  done
  for P in E:R:150 R:E:150; do
    A=${P%%:*}; REST=${P#*:}; B=${REST%%:*}; T=${REST#*:}
    run 7 --seed $S --condition baseline --steps $((T + 2000)) --stop-after-gen 8000 --split-file $SP/seed${S}_train_$A.npy \
      --test-file $SP/seed${S}_test.npy --switch-split-file $SP/seed${S}_train_$B.npy --switch-step $T
  done
done
echo "[exp041] all done"
