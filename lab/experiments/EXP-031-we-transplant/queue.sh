#!/bin/sh
# EXP-031 queue: smoke (20 steps, raw_smoke), then transplant/control for B in 0 2 4 6 8 (A = B + 1). One job at a time,
# every run through guarded_run.py; stop on nonzero exit; skip only complete runs.
X=lab/experiments/EXP-031-we-transplant
if [ ! -f $X/raw_smoke/EXP-031_transplant_B0_A1/result.json ]; then
  python lab/tools/guarded_run.py --min-minutes 2 -- python $X/transplant.py --seed-b 0 --seed-a 1 --steps 20 --out $X/raw_smoke || exit $?
fi
for B in 0 2 4 6 8; do
  A=$((B + 1))
  for ARM in transplant control; do
    if [ $ARM = transplant ]; then ID=EXP-031_transplant_B${B}_A${A}; EXTRA="--seed-a $A"; else ID=EXP-031_control_B${B}; EXTRA=""; fi
    grep -q '"complete": true' "$X/raw/$ID/result.json" 2>/dev/null && continue
    python lab/tools/guarded_run.py --min-minutes 8 -- python $X/transplant.py --seed-b $B $EXTRA
    rc=$?; if [ $rc -ne 0 ]; then echo "[exp031] stop, rc=$rc"; exit $rc; fi
  done
done
echo "[exp031] all done"
