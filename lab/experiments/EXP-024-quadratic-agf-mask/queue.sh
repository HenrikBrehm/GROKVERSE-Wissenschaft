#!/bin/sh
# EXP-024 queue: quadratic (Q) then ReLU (R) two-hot MLP on the EXP-016 splits (seed 12/G excluded, = seed 19/F).
# Every run through guarded_run.py; stops on any nonzero exit; completed runs are skipped (result.json exists).
T=lab/experiments/EXP-024-quadratic-agf-mask/train_twohot.py
O=lab/experiments/EXP-024-quadratic-agf-mask/raw
for ACT in quad relu; do
  for S in 10 11 12 13 14 15 16 17 18 19; do
    for A in F G; do
      [ "$S$A" = "12G" ] && continue
      [ -f "$O/EXP-024_${ACT}_seed${S}_${A}/result.json" ] && continue
      python lab/tools/guarded_run.py --min-minutes 3 -- python $T --seed $S --arm $A --act $ACT
      rc=$?; if [ $rc -ne 0 ]; then echo "[exp024] stop, rc=$rc"; exit $rc; fi
    done
  done
done
echo "[exp024] all done"
