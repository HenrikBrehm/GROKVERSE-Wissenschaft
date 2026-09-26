#!/bin/sh
# EXP-025 queue: quadratic and ReLU two-hot MLP on the study's random splits, seeds 10-19. One job at a time.
# Session 7: EXP-032 (fine switch grid, follow-up of EXP-026) runs first; chained here because queue_s7.sh is running.
sh lab/experiments/EXP-032-early-lockin/queue.sh || exit $?
T=lab/experiments/EXP-024-quadratic-agf-mask/train_twohot.py
O=lab/experiments/EXP-025-utility-random-split/raw
for ACT in quad relu; do
  for S in 10 11 12 13 14 15 16 17 18 19; do
    [ -f "$O/EXP-025_${ACT}_seed${S}_random/result.json" ] && continue
    python lab/tools/guarded_run.py --min-minutes 3 -- python $T --seed $S --act $ACT --random-split --out $O
    rc=$?; if [ $rc -ne 0 ]; then echo "[exp025] stop, rc=$rc"; exit $rc; fi
  done
done
echo "[exp025] all done"
