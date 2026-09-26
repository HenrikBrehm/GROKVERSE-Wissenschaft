#!/bin/sh
# EXP-037 queue: EXP-020 splits/inits of seeds 30-32; F/G alternate in blocks of A steps (A = 5, 25) for steps 1..200,
# then G only for 2000 steps (freq_ban.py --alternate-every A --switch-step 200). Smoke first (fail-closed).
# One job at a time via guarded_run.py; completed runs are skipped (exit 0); any other exit stops. Resume = rerun.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
S20=lab/experiments/EXP-020-data-switch/splits
O=lab/experiments/EXP-037-alternation-conflict/raw
SM=lab/experiments/EXP-037-alternation-conflict/raw_smoke
run() { mm=$1; shift; python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@" --out-root $O; rc=$?; [ $rc -eq 0 ] || { echo "[exp037] stop, rc=$rc"; exit $rc; }; }
# smoke: 30 steps, A = 5, switch at 20 -> toggles at steps 5, 10, 15 (3), switch event at 20
python lab/tools/guarded_run.py --min-minutes 2 -- python $F --seed 30 --condition baseline --steps 30 --stop-after-gen 8000 \
  --split-file $S20/seed30_train_F.npy --test-file $S20/seed30_test.npy --switch-split-file $S20/seed30_train_G.npy \
  --switch-step 20 --alternate-every 5 --out-root $SM || { echo "[exp037] smoke failed"; exit 1; }
python -c "import json,glob,sys;r=json.load(open(glob.glob('$SM/*_alt5/result.json')[0]));e=r['events'];sys.exit(0 if r['alternate_every']==5 and e.get('alternations')==3 and e.get('switch',{}).get('step')==20 and r['steps_completed']==30 else 1)" \
  || { echo "[exp037] smoke check failed"; exit 1; }
for A in 5 25; do
  for S in 30 31 32; do
    run 7 --seed $S --condition baseline --steps 2200 --stop-after-gen 8000 --split-file $S20/seed${S}_train_F.npy \
      --test-file $S20/seed${S}_test.npy --switch-split-file $S20/seed${S}_train_G.npy --switch-step 200 --alternate-every $A
  done
done
echo "[exp037] all done"
