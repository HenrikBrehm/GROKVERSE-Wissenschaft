#!/bin/sh
# EXP-034: fresh EXP-016-style splits, seeds 60-69 (plus pilot 70), eps 2, arm F.
for S in 60 61 62 63 64 65 66 67 68 69 70; do
  python lab/experiments/EXP-016-engineered-split/make_split.py --seed $S --eps 2.0 --out lab/experiments/EXP-034-phase2-optimizer/splits || exit 1
done
