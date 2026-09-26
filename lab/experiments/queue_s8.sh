#!/bin/sh
# Session-8 master queue (2026-09-26): EXP-020 remainder -> EXP-035 (warmup, seeds 30-32) -> EXP-034 -> rest of queue_s5.
# One job at a time; every run through guarded_run.py; each part skips completed runs and stops on failure. Resume = rerun.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
R=lab/experiments
S20=$R/EXP-020-data-switch/splits
run() { mm=$1; shift; python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@"; rc=$?; [ $rc -eq 0 ] || { echo "[queue8] stop, rc=$rc"; exit $rc; }; }
while ps -ef | grep -v grep | grep -q "guarded_run.py"; do sleep 10; done
for S in 30 31 32 33 34; do      # identical arguments to queue_s5.sh (EXP-020), so completed runs are skipped
  run 19 --seed $S --condition baseline --steps 8000 --stop-after-gen 2000 --split-file $S20/seed${S}_train_F.npy \
    --test-file $S20/seed${S}_test.npy --out-root $R/EXP-020-data-switch/raw
  run 7 --seed $S --condition baseline --steps 2000 --stop-after-gen 8000 --split-file $S20/seed${S}_train_G.npy \
    --test-file $S20/seed${S}_test.npy --out-root $R/EXP-020-data-switch/raw
  for T in 150 50 25 10 400 1000; do
    run 9 --seed $S --condition baseline --steps $((T + 2000)) --stop-after-gen 8000 \
      --split-file $S20/seed${S}_train_F.npy --test-file $S20/seed${S}_test.npy \
      --switch-split-file $S20/seed${S}_train_G.npy --switch-step $T --out-root $R/EXP-020-data-switch/raw
  done
done
python lab/tools/guarded_run.py -- python $R/EXP-020-data-switch/analyze.py || echo "[queue8] EXP-020 analysis failed (continuing)"
python lab/tools/guarded_run.py -- python $R/EXP-028-memo-imprint/analyze.py || echo "[queue8] EXP-028 analysis failed (continuing)"
sh $R/EXP-035-warmup-lockin/queue.sh 30 31 32 || { echo "[queue8] EXP-035 stop"; exit 1; }
python lab/tools/guarded_run.py -- python $R/EXP-035-warmup-lockin/analyze.py || echo "[queue8] EXP-035 analysis failed (continuing)"
sh $R/EXP-034-phase2-optimizer/queue.sh || { echo "[queue8] EXP-034 stop"; exit 1; }
python lab/tools/guarded_run.py -- python $R/EXP-034-phase2-optimizer/analyze.py || echo "[queue8] EXP-034 analysis failed (continuing)"
sh $R/queue_s5.sh || { echo "[queue8] queue_s5 stop"; exit 1; }
echo "[queue8] all done"
