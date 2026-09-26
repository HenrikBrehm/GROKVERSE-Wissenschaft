#!/bin/sh
# EXP-026 queue: sigma_alpha two-hot MLP on EXP-016 splits seeds 10-14 arm F, alpha grid. One job at a time,
# every run through guarded_run.py; stops on any nonzero exit; completed runs are skipped.
T=lab/experiments/EXP-026-parity-crossover/train_sigma.py
O=lab/experiments/EXP-026-parity-crossover/raw
for AL in 0 0.003 0.03 0.3 3; do
  for S in 10 11 12 13 14; do
    [ -f "$O/EXP-026_a${AL}_seed${S}_F/result.json" ] && continue
    python lab/tools/guarded_run.py --min-minutes 3 -- python $T --seed $S --arm F --alpha $AL
    rc=$?; if [ $rc -ne 0 ]; then echo "[exp026] stop, rc=$rc"; exit $rc; fi
  done
done
echo "[exp026] all done"
