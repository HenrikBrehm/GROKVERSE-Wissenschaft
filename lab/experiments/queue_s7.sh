#!/bin/sh
# Session 7 chain: EXP-026 smoke (alpha 3, never switch, EXP-024 smoke split seed 9; not analysed), EXP-026, EXP-025,
# then queue_s5.sh. Waits (max 45 min) until the EXP-024 queue log reports its end, so only one job runs. Each sub-queue runs every job through guarded_run.py and skips completed runs; stop on nonzero exit.
L=lab/runner/logs/queue_exp024.log; n=0
while ! grep -q "^\[exp024\]" $L; do n=$((n+1)); [ $n -gt 135 ] && { echo "[s7] EXP-024 queue did not end"; exit 1; }; sleep 20; done
grep "^\[exp024\]" $L
if [ ! -f lab/experiments/EXP-026-parity-crossover/raw_smoke/EXP-026_a3_seed9_F/result.json ]; then
  python lab/tools/guarded_run.py --min-minutes 3 -- python lab/experiments/EXP-026-parity-crossover/train_sigma.py \
    --seed 9 --arm F --alpha 3 --split-dir lab/experiments/EXP-024-quadratic-agf-mask/smoke_splits \
    --out lab/experiments/EXP-026-parity-crossover/raw_smoke || { echo "[s7] smoke failed rc=$?"; exit 1; }
fi
sh lab/experiments/EXP-026-parity-crossover/queue.sh || exit $?
sh lab/experiments/EXP-025-utility-random-split/queue.sh || exit $?
sh lab/experiments/queue_s5.sh || exit $?
echo "[s7] all done"
