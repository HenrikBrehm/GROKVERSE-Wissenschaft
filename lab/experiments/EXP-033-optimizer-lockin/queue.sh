#!/bin/sh
# EXP-033 queue (Nachtrag a). One job at a time via guarded_run.py; completed runs are skipped.
# 1) GD lr pilot (split 10, init 99, phase 1 only) + select_lr.py -> lr.json
# 2) per split 10-19 at level t_s = 10: AdamW-reset (target r := its own r at the switch), GD, sign; retained AdamW
#    (EXP-032 protocol, train_sigma.py) for 15-19. rc 4 (target not reached / NaN) is data only if result.json says so.
T=lab/experiments/EXP-033-optimizer-lockin/train_opt.py
E=lab/experiments/EXP-033-optimizer-lockin
O=$E/raw
G="python lab/tools/guarded_run.py"
done_() { grep -q '"complete": true' "$1/result.json" 2>/dev/null; }
stop() { echo "[exp033] stop: $1"; exit 1; }
if [ ! -f $E/lr.json ]; then
  for L in 0.3 1 3 10 30; do
    done_ "$E/raw_smoke/EXP-033_gd_r0.0167_lr${L}_seed10_init99_p1" && continue
    $G --min-minutes 3 -- python $T --seed 10 --init-seed 99 --opt1 gd --switch-r 0.0167 --gd-lr $L --max-phase1 5000 --phase1-only --out $E/raw_smoke
    rc=$?; [ $rc -eq 0 ] || [ $rc -eq 4 ] || stop "pilot lr $L rc=$rc"
  done
  python $E/select_lr.py || stop "no admissible lr"
fi
LR=$(python -c "import json;print(json.load(open('$E/lr.json'))['lr'])")
[ "$LR" != "None" ] || stop "lr.json has no lr"
gdrun() {  # $1 opt, $2 seed, $3 target r, rest extra args
  opt=$1; S=$2; R=$3; shift 3
  RID=$(python -c "print('EXP-033_$opt' + f'_r{$R:g}' + ('_lr' + f'{$LR:g}' if '$opt' == 'gd' else '') + '_seed$S')")
  done_ "$O/$RID" && return 0
  $G --min-minutes 6 -- python $T --seed $S --opt1 $opt --switch-r $R "$@" --out $O
  rc=$?
  [ $rc -eq 0 ] && return 0
  [ $rc -eq 4 ] && python -c "import json,sys;r=json.load(open('$O/$RID/result.json'));sys.exit(0 if (not r['reached'] or not r['finite']) else 1)" \
    && { echo "[exp033] $RID did not reach target (data)"; return 0; }
  stop "$RID rc=$rc"
}
for S in 10 11 12 13 14 15 16 17 18 19; do
  done_ "$O/EXP-033_adamw_t10_seed$S" || { $G --min-minutes 3 -- python $T --seed $S --opt1 adamw --switch-step 10 --out $O || stop "adamw seed $S"; }
  R=$(python -c "import json;print(json.load(open('$O/EXP-033_adamw_t10_seed$S/result.json'))['r_switch'])")
  gdrun gd $S $R --gd-lr $LR
  gdrun sign $S $R
  if [ $S -ge 15 ]; then
    done_ "$O/EXP-026_a3_sw10to0_seed${S}_F" || { $G --min-minutes 3 -- python lab/experiments/EXP-026-parity-crossover/train_sigma.py --seed $S --arm F --alpha 3 --switch-step 10 --alpha-after 0 --out $O || stop "retained seed $S"; }
  fi
done
echo "[exp033] all done"
