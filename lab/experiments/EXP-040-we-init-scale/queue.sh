#!/bin/sh
# EXP-040 queue: EXP-020 protocol with W_E multiplied by s after init (s = 0.5, 2), own only-G / only-F references.
# s = 0.5: switches t = 25, 12, 10, 50; s = 2: t = 50, 25, 100, 150. Seeds 30 32 34 (31 last). Early spectra logged.
# One job at a time via guarded_run.py; completed runs are skipped (exit 0); any other exit stops. Resume = rerun.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
S20=lab/experiments/EXP-020-data-switch/splits
O=lab/experiments/EXP-040-we-init-scale/raw
SA=5,10,12,15,20,25,30,40,50,75,100,150,200
run() { mm=$1; shift; python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@" --spectra-at $SA --out-root $O; rc=$?; [ $rc -eq 0 ] || { echo "[exp040] stop, rc=$rc"; exit $rc; }; }
python lab/tools/guarded_run.py --min-minutes 1 -- python lab/experiments/EXP-040-we-init-scale/analyze.py --selftest || { echo "[exp040] selftest failed"; exit 1; }
# smoke: scaled init + switch (60 steps); step-0 W_E power must be s^2 times the plain init of the same seed (EXP-035 run)
rm -rf lab/experiments/EXP-040-we-init-scale/raw_smoke
python lab/tools/guarded_run.py --min-minutes 2 -- python $F --seed 30 --condition baseline --steps 60 --stop-after-gen 8000 \
  --split-file $S20/seed30_train_F.npy --test-file $S20/seed30_test.npy --switch-split-file $S20/seed30_train_G.npy \
  --switch-step 30 --we-init-scale 0.5 --out-root lab/experiments/EXP-040-we-init-scale/raw_smoke || { echo "[exp040] smoke failed"; exit 1; }
SM=lab/experiments/EXP-040-we-init-scale/raw_smoke/EXP-020_baseline_seed30_thr4_seed30_train_F_to_seed30_train_G_at30_wes0.5
REF=lab/experiments/EXP-035-warmup-lockin/raw/EXP-018_baseline_seed30_thr4_seed30_train_F_wu200
python -c "import json,sys,numpy as n;r=json.load(open(sys.argv[1]+'/result.json'));a=n.load(sys.argv[1]+'/spectra.npy')[0];b=n.load(sys.argv[2]+'/spectra.npy')[0];ok=r['status']=='completed' and r['we_init_scale']==0.5 and r['events'].get('switch',{}).get('step')==30 and n.allclose(a,0.25*b,rtol=1e-5);print('smoke ratio',float(a.sum()/b.sum()));sys.exit(0 if ok else 1)" $SM $REF \
  || { echo "[exp040] smoke check failed"; exit 1; }
for S in ${*:-30 32 34 31}; do
  for C in 0.5 2; do
    run 7 --seed $S --condition baseline --steps 2000 --stop-after-gen 8000 --split-file $S20/seed${S}_train_G.npy \
      --test-file $S20/seed${S}_test.npy --we-init-scale $C
    run 19 --seed $S --condition baseline --steps 8000 --stop-after-gen 2000 --split-file $S20/seed${S}_train_F.npy \
      --test-file $S20/seed${S}_test.npy --we-init-scale $C
    if [ "$C" = "0.5" ]; then TS="25 12 10 50"; else TS="50 25 100 150"; fi
    for T in $TS; do
      run 9 --seed $S --condition baseline --steps $((T + 2000)) --stop-after-gen 8000 --split-file $S20/seed${S}_train_F.npy \
        --test-file $S20/seed${S}_test.npy --switch-split-file $S20/seed${S}_train_G.npy --switch-step $T --we-init-scale $C
    done
  done
done
echo "[exp040] all done"
