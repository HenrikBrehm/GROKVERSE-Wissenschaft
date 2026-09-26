#!/bin/sh
# EXP-026 queue (Nachtrag a): alpha = 3 until switch step t_s, then alpha = 0 (pure x^2); t_s = -1 means never.
# EXP-016 splits seeds 10-14 arm F. One job at a time, every run through guarded_run.py; stops on any nonzero exit;
# only runs whose result.json says complete are skipped.
T=lab/experiments/EXP-026-parity-crossover/train_sigma.py
O=lab/experiments/EXP-026-parity-crossover/raw
for TS in 0 -1 250 1000 50 2500; do
  for S in 10 11 12 13 14; do
    if [ "$TS" = "-1" ]; then ID="EXP-026_a3_seed${S}_F"; else ID="EXP-026_a3_sw${TS}to0_seed${S}_F"; fi
    grep -q '"complete": true' "$O/$ID/result.json" 2>/dev/null && continue
    python lab/tools/guarded_run.py --min-minutes 3 -- python $T --seed $S --arm F --alpha 3 --switch-step $TS --alpha-after 0
    rc=$?; if [ $rc -ne 0 ]; then echo "[exp026] stop, rc=$rc"; exit $rc; fi
  done
done
echo "[exp026] all done"
