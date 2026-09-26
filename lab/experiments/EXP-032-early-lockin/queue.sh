#!/bin/sh
# EXP-032 queue: alpha 3 -> 0 at t_s in 1 5 10 20, EXP-016 splits seeds 10-14 F. One job at a time via guarded_run.py.
T=lab/experiments/EXP-026-parity-crossover/train_sigma.py
O=lab/experiments/EXP-032-early-lockin/raw
for TS in 20 5 10 1; do
  for S in 10 11 12 13 14; do
    grep -q '"complete": true' "$O/EXP-026_a3_sw${TS}to0_seed${S}_F/result.json" 2>/dev/null && continue
    python lab/tools/guarded_run.py --min-minutes 3 -- python $T --seed $S --arm F --alpha 3 --switch-step $TS --alpha-after 0 --out $O
    rc=$?; if [ $rc -ne 0 ]; then echo "[exp032] stop, rc=$rc"; exit $rc; fi
  done
done
echo "[exp032] all done"
