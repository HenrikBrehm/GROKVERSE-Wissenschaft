#!/bin/sh
# EXP-039 queue: EXP-020 protocol with constant lr scale c on the F phase (steps <= 250), full lr after the switch.
# c = 2: only F + switches t = 25, 10, 50; c = 0.5: only F + t = 50, 100, 150. Seeds 30 32 34 (31 last). One job at a time
# via guarded_run.py; completed runs are skipped (exit 0); any other exit stops. Resume = rerun.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
S20=lab/experiments/EXP-020-data-switch/splits
O=lab/experiments/EXP-039-lr-clock/raw
run() { mm=$1; shift; python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@" --out-root $O; rc=$?; [ $rc -eq 0 ] || { echo "[exp039] stop, rc=$rc"; exit $rc; }; }
# smoke: lr-scale + switch code path (60 steps), fail-closed check on the exact run directory
rm -rf lab/experiments/EXP-039-lr-clock/raw_smoke
python lab/tools/guarded_run.py --min-minutes 2 -- python $F --seed 30 --condition baseline --steps 60 --stop-after-gen 8000 \
  --split-file $S20/seed30_train_F.npy --test-file $S20/seed30_test.npy --switch-split-file $S20/seed30_train_G.npy \
  --switch-step 30 --lr-scale 2 --out-root lab/experiments/EXP-039-lr-clock/raw_smoke || { echo "[exp039] smoke failed"; exit 1; }
SM=lab/experiments/EXP-039-lr-clock/raw_smoke/EXP-020_baseline_seed30_thr4_seed30_train_F_to_seed30_train_G_at30_lrs2
python -c "import json,sys;r=json.load(open(sys.argv[1]+'/result.json'));e=r['events'];sys.exit(0 if r['status']=='completed' and r['lr_scale']==2.0 and r['lr_scale_until']==250 and e.get('switch',{}).get('step')==30 and e.get('displacement_at_switch',{}).get('W_E',0)>0 else 1)" $SM \
  || { echo "[exp039] smoke check failed"; exit 1; }
for S in ${*:-30 32 34 31}; do
  for C in 2 0.5; do
    run 19 --seed $S --condition baseline --steps 8000 --stop-after-gen 2000 --split-file $S20/seed${S}_train_F.npy \
      --test-file $S20/seed${S}_test.npy --lr-scale $C
    if [ "$C" = "2" ]; then TS="25 10 50"; else TS="50 100 150"; fi
    for T in $TS; do
      run 9 --seed $S --condition baseline --steps $((T + 2000)) --stop-after-gen 8000 --split-file $S20/seed${S}_train_F.npy \
        --test-file $S20/seed${S}_test.npy --switch-split-file $S20/seed${S}_train_G.npy --switch-step $T --lr-scale $C
    done
  done
done
echo "[exp039] all done"
