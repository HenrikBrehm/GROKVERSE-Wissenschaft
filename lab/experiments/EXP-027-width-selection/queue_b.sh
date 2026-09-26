#!/bin/sh
# EXP-027b queue: pure x^2 two-hot nets, widths 64/128/256/512, EXP-016 splits seeds 15-19 F. Via guarded_run.py.
T=lab/experiments/EXP-026-parity-crossover/train_sigma.py
O=lab/experiments/EXP-027-width-selection/raw_b
for W in 64 128 256 512; do
  for S in 15 16 17 18 19; do
    if [ $W = 512 ]; then ID=EXP-026_a0_seed${S}_F; else ID=EXP-026_a0_w${W}_seed${S}_F; fi
    grep -q '"complete": true' "$O/$ID/result.json" 2>/dev/null && continue
    python lab/tools/guarded_run.py --min-minutes 3 -- python $T --seed $S --arm F --alpha 0 --width $W --out $O
    rc=$?; if [ $rc -ne 0 ]; then echo "[exp027b] stop, rc=$rc"; exit $rc; fi
  done
done
echo "[exp027b] all done"
