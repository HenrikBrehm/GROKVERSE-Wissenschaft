#!/bin/sh
# EXP-034 queue (Nachtrag a after Codex): A = anchor/AR5/GD5/AR10/GD10 with AdamW phase 2; pilot B on split 70 from
# anchor, AR10 and GD10 states; B = anchor/AR10/GD10 with GD phase 2. One job at a time via guarded_run.py.
# Completed runs are skipped; every nonzero exit stops (all units must be valid). Idempotent: lr2.json is re-validated.
T=lab/experiments/EXP-033-optimizer-lockin/train_opt.py
E=lab/experiments/EXP-034-phase2-optimizer
O=$E/raw
SD="--split-dir $E/splits --out $O"
G="python lab/tools/guarded_run.py"
done_() { grep -q '"complete": true' "$O/$1/result.json" 2>/dev/null; }
stop() { echo "[exp034] stop: $1"; exit 1; }
rsw() { python -c "import json;print(json.load(open('$O/$1/result.json'))['r_switch'])"; }
gid() { python -c "print(f'EXP-033_gd_r{$1:g}_lr3_seed$2_bt$3')"; }
trio() {   # $1 seed, $2 phase-2 suffix, $3... phase-2 args; runs anchor, AR10, GD10 (+ AR5, GD5 if suffix empty)
  S=$1; SUF=$2; shift 2
  LV="0 10"; [ -z "$SUF" ] && LV="0 5 10"
  for TS in $LV; do
    done_ "EXP-033_adamw_t${TS}_seed${S}$SUF" || { $G --min-minutes 3 -- python $T --seed $S --opt1 adamw --switch-step $TS "$@" $SD || stop "adamw t$TS seed $S $SUF"; }
  done
  for TS in $LV; do
    [ $TS -eq 0 ] && continue
    R=$(rsw "EXP-033_adamw_t${TS}_seed${S}$SUF")
    done_ "$(gid $R $S "$SUF")" || { $G --min-minutes 3 -- python $T --seed $S --opt1 gd --switch-r $R --gd-lr 3 --backtrack "$@" $SD || stop "gd t$TS seed $S $SUF"; }
  done
}
for S in 60 61 62 63 64 65 66 67 68 69; do trio $S ""; done            # part A (AdamW phase 2)
for L in 1 3 10; do                                                    # pilot B (split 70, three start states)
  SUF="_p2gd${L}_n10000"
  for TS in 0 10; do
    done_ "EXP-033_adamw_t${TS}_seed70$SUF" || { $G --min-minutes 8 -- python $T --seed 70 --opt1 adamw --switch-step $TS --opt2 gd --gd2-lr $L --after-steps 10000 $SD; rc=$?; [ $rc -eq 0 ] || [ $rc -eq 4 ] || stop "pilot t$TS lr2 $L rc=$rc"; }
  done
  R=$(rsw "EXP-033_adamw_t10_seed70$SUF")
  done_ "$(gid $R 70 $SUF)" || { $G --min-minutes 8 -- python $T --seed 70 --opt1 gd --switch-r $R --gd-lr 3 --backtrack --opt2 gd --gd2-lr $L --after-steps 10000 $SD; rc=$?; [ $rc -eq 0 ] || [ $rc -eq 4 ] || stop "pilot gd lr2 $L rc=$rc"; }
done
python $E/select_lr2.py
L=$(python -c "import json;v=json.load(open('$E/lr2.json'))['lr2'];print('' if v is None else f'{v:g}')")
[ -n "$L" ] || { echo "[exp034] part B not feasible (no admissible lr2), done"; exit 0; }
for S in 60 61 62 63 64 65 66 67 68 69; do trio $S "_p2gd${L}_n10000" --opt2 gd --gd2-lr $L --after-steps 10000; done   # part B
echo "[exp034] all done"
