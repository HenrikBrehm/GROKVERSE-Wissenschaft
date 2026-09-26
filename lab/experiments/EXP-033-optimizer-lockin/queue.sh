#!/bin/sh
# EXP-033 queue: $1 = GD learning rate (chosen by the phase-1 smoke, README). One job at a time via guarded_run.py.
# Target r per split/level = EXP-032 r at the switch step. Completed runs are skipped; stops on any nonzero exit.
[ -n "$1" ] || { echo "usage: queue.sh <gd_lr>"; exit 2; }
LR=$1
T=lab/experiments/EXP-033-optimizer-lockin/train_opt.py
O=lab/experiments/EXP-033-optimizer-lockin/raw
done_() { grep -q '"complete": true' "$O/$1/result.json" 2>/dev/null; }
for TS in 5 10 20; do
  for S in 10 11 12 13 14; do
    if ! done_ "EXP-033_adamw_t${TS}_seed${S}"; then
      python lab/tools/guarded_run.py --min-minutes 3 -- python $T --seed $S --opt1 adamw --switch-step $TS --out $O
      rc=$?; if [ $rc -ne 0 ]; then echo "[exp033] stop, rc=$rc"; exit $rc; fi
    fi
    R=$(python -c "import json;print(next(x['r_at_switch']['median'] for x in json.load(open('lab/experiments/EXP-032-early-lockin/summary.json'))['rows'] if x['ts']==$TS and x['seed']==$S))")
    RID=$(python -c "print(f'EXP-033_gd_r{$R:g}_lr{$LR:g}_seed$S')")
    if ! done_ "$RID"; then
      python lab/tools/guarded_run.py --min-minutes 6 -- python $T --seed $S --opt1 gd --switch-r $R --gd-lr $LR --out $O
      rc=$?   # rc 4 = target r not reached / NaN: that is data, continue; guard refusal or timeout: stop
      if [ $rc -eq 3 ] || [ $rc -eq 124 ]; then echo "[exp033] stop (gd), rc=$rc"; exit $rc; fi
      [ $rc -ne 0 ] && echo "[exp033] gd seed $S level $TS incomplete, rc=$rc"
    fi
  done
done
echo "[exp033] all done"
