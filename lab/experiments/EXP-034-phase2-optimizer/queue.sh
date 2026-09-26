#!/bin/sh
# EXP-034 queue: part A (level 5, AdamW phase 2), pilot B (lr2), part B (GD phase 2). One job at a time via guarded_run.py.
# Completed runs are skipped; any nonzero exit stops, except rc 4 of a GD phase 1 whose result.json says not reached.
T=lab/experiments/EXP-033-optimizer-lockin/train_opt.py
E=lab/experiments/EXP-034-phase2-optimizer
O=$E/raw
SD="--split-dir $E/splits --out $O"
G="python lab/tools/guarded_run.py"
done_() { grep -q '"complete": true' "$O/$1/result.json" 2>/dev/null; }
stop() { echo "[exp034] stop: $1"; exit 1; }
rsw() { python -c "import json;print(json.load(open('$O/$1/result.json'))['r_switch'])"; }
gid() { python -c "print(f'EXP-033_gd_r{$1:g}_lr3_seed$2_bt$3')"; }
for S in 60 61 62 63 64 65 66 67 68 69; do          # part A
  for TS in 0 5; do
    done_ "EXP-033_adamw_t${TS}_seed$S" || { $G --min-minutes 3 -- python $T --seed $S --opt1 adamw --switch-step $TS $SD || stop "A adamw t$TS seed $S"; }
  done
  R=$(rsw "EXP-033_adamw_t5_seed$S")
  done_ "$(gid $R $S '')" || { $G --min-minutes 3 -- python $T --seed $S --opt1 gd --switch-r $R --gd-lr 3 --backtrack $SD || stop "A gd seed $S"; }
done
if [ ! -f $E/lr2.json ]; then                          # pilot B
  for L in 1 3 10; do
    done_ "EXP-033_adamw_t0_seed70_p2gd${L}_n10000" && continue
    $G --min-minutes 8 -- python $T --seed 70 --opt1 adamw --switch-step 0 --opt2 gd --gd2-lr $L --after-steps 10000 $SD
    rc=$?; [ $rc -eq 0 ] || [ $rc -eq 4 ] || stop "pilot lr2 $L rc=$rc"
  done
  python $E/select_lr2.py || { echo "[exp034] part B not feasible (no admissible lr2)"; exit 0; }
fi
L=$(python -c "import json;print(f\"{json.load(open('$E/lr2.json'))['lr2']:g}\")")
P2="--opt2 gd --gd2-lr $L --after-steps 10000"
for S in 60 61 62 63 64 65 66 67 68 69; do          # part B
  for TS in 0 10; do
    done_ "EXP-033_adamw_t${TS}_seed${S}_p2gd${L}_n10000" || { $G --min-minutes 8 -- python $T --seed $S --opt1 adamw --switch-step $TS $P2 $SD || stop "B adamw t$TS seed $S"; }
  done
  R=$(rsw "EXP-033_adamw_t10_seed${S}_p2gd${L}_n10000")
  done_ "$(gid $R $S _p2gd${L}_n10000)" || { $G --min-minutes 8 -- python $T --seed $S --opt1 gd --switch-r $R --gd-lr 3 --backtrack $P2 $SD || stop "B gd seed $S"; }
done
echo "[exp034] all done"
