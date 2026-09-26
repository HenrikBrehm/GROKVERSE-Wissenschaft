#!/bin/sh
# EXP-027 queue: pure x^2 two-hot nets of width 32/64/128 on EXP-016 splits seeds 10-14 arm F (width 512 comes from
# EXP-026 arm t_s = 0). One job at a time through guarded_run.py; stop on nonzero exit; skip only complete runs.
T=lab/experiments/EXP-026-parity-crossover/train_sigma.py
O=lab/experiments/EXP-027-width-selection/raw
for W in 32 64 128; do
  for S in 10 11 12 13 14; do
    grep -q '"complete": true' "$O/EXP-026_a0_w${W}_seed${S}_F/result.json" 2>/dev/null && continue
    python lab/tools/guarded_run.py --min-minutes 3 -- python $T --seed $S --arm F --alpha 0 --width $W --out $O
    rc=$?; if [ $rc -ne 0 ]; then echo "[exp027] stop, rc=$rc"; exit $rc; fi
  done
done
echo "[exp027] all done"
