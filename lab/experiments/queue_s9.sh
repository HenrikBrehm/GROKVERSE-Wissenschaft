#!/bin/sh
# Session-9 master queue (2026-09-26): queue_s8 order with EXP-036 inserted after EXP-035:
# EXP-020 remainder -> analyses (EXP-020, EXP-028, Nachtrag d) -> EXP-035 -> EXP-036 -> EXP-034 -> rest of queue_s5.
# One job at a time; every run through guarded_run.py; each part skips completed runs and stops on failure. Resume = rerun.
R=lab/experiments
while ps -ef | grep -v grep | grep -q "guarded_run.py"; do sleep 10; done
# EXP-020 part of queue_s8 (identical arguments; completed runs are skipped)
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
S20=$R/EXP-020-data-switch/splits
run() { mm=$1; shift; python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@"; rc=$?; [ $rc -eq 0 ] || { echo "[queue9] stop, rc=$rc"; exit $rc; }; }
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
python lab/tools/guarded_run.py -- python $R/EXP-020-data-switch/analyze.py || echo "[queue9] EXP-020 analysis failed (continuing)"
python lab/tools/guarded_run.py -- python $R/EXP-028-memo-imprint/analyze.py || echo "[queue9] EXP-028 analysis failed (continuing)"
python lab/tools/guarded_run.py -- python $R/EXP-020-data-switch/conflict_freqs.py || echo "[queue9] Nachtrag d failed (continuing)"
sh $R/EXP-035-warmup-lockin/queue.sh 30 31 32 || { echo "[queue9] EXP-035 stop"; exit 1; }
python lab/tools/guarded_run.py -- python $R/EXP-035-warmup-lockin/analyze.py || echo "[queue9] EXP-035 analysis failed (continuing)"
sh $R/EXP-036-init-conflict/queue.sh || { echo "[queue9] EXP-036 stop"; exit 1; }
python lab/tools/guarded_run.py -- python $R/EXP-036-init-conflict/analyze.py || echo "[queue9] EXP-036 analysis failed (continuing)"
sh $R/EXP-034-phase2-optimizer/queue.sh || { echo "[queue9] EXP-034 stop"; exit 1; }
python lab/tools/guarded_run.py -- python $R/EXP-034-phase2-optimizer/analyze.py || echo "[queue9] EXP-034 analysis failed (continuing)"
sh $R/queue_s5.sh || { echo "[queue9] queue_s5 stop"; exit 1; }
echo "[queue9] all done"
