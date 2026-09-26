#!/bin/sh
# EXP-035 queue: EXP-020 protocol with linear lr warmup over 200 steps (freq_ban.py --warmup 200), seeds from $@
# (default 30 31 32). Nachtrag a: warmup only while training on F; full lr after the switch. One job at a time via guarded_run.py; completed runs are skipped (exit 0); any other exit stops.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
S20=lab/experiments/EXP-020-data-switch/splits
O=lab/experiments/EXP-035-warmup-lockin/raw
W=200
SEEDS=${*:-30 31 32}
run() { mm=$1; shift; python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@" --warmup $W --out-root $O; rc=$?; [ $rc -eq 0 ] || { echo "[exp035] stop, rc=$rc"; exit $rc; }; }
# smoke (warmup + switch code path, 60 steps), fail-closed check of the switch and displacement events
python lab/tools/guarded_run.py --min-minutes 2 -- python $F --seed 30 --condition baseline --steps 60 --stop-after-gen 8000   --split-file $S20/seed30_train_F.npy --test-file $S20/seed30_test.npy --switch-split-file $S20/seed30_train_G.npy   --switch-step 30 --warmup $W --out-root lab/experiments/EXP-035-warmup-lockin/raw_smoke || { echo "[exp035] smoke failed"; exit 1; }
python -c "import json,glob,sys;r=json.load(open(glob.glob('lab/experiments/EXP-035-warmup-lockin/raw_smoke/*_wu200/result.json')[0]));e=r['events'];sys.exit(0 if r['warmup']==200 and e.get('switch',{}).get('step')==30 and e.get('displacement_at_switch',{}).get('W_E',0)>0 else 1)"   || { echo "[exp035] smoke check failed"; exit 1; }
for S in $SEEDS; do
  run 19 --seed $S --condition baseline --steps 8000 --stop-after-gen 2000 --split-file $S20/seed${S}_train_F.npy --test-file $S20/seed${S}_test.npy
  # Nachtrag a: t = 0 reference is the EXP-020 "only G" run (constant lr, identical to the post-switch G phase here)
  for T in 50 150 100 25 10 250; do
    run 9 --seed $S --condition baseline --steps $((T + 2000)) --stop-after-gen 8000 --split-file $S20/seed${S}_train_F.npy \
      --test-file $S20/seed${S}_test.npy --switch-split-file $S20/seed${S}_train_G.npy --switch-step $T
  done
done
echo "[exp035] all done"
