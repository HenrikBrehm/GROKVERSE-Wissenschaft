#!/bin/sh
# Session-10 master queue (written 2026-09-26, session 9): EXP-037 rest -> EXP-035 -> EXP-034 -> EXP-036 -> rest of queue_s5.
# EXP-036 moved behind EXP-034 after EXP-020 Nachtrag d failed on fresh seeds (lower prior for H36).
# One job at a time; every run through guarded_run.py; each part skips completed runs and stops on failure. Resume = rerun.
R=lab/experiments
while ps -ef | grep -v grep | grep -q "guarded_run.py"; do sleep 10; done
sh $R/EXP-037-alternation-conflict/queue.sh || { echo "[queue10] EXP-037 stop"; exit 1; }
python lab/tools/guarded_run.py -- python $R/EXP-037-alternation-conflict/analyze.py || echo "[queue10] EXP-037 analysis failed (continuing)"
python lab/tools/guarded_run.py -- python $R/EXP-037-alternation-conflict/ablate_foreign.py || echo "[queue10] EXP-037 ablation failed (continuing)"
sh $R/EXP-035-warmup-lockin/queue.sh 30 31 32 || { echo "[queue10] EXP-035 stop"; exit 1; }
python lab/tools/guarded_run.py -- python $R/EXP-035-warmup-lockin/analyze.py || echo "[queue10] EXP-035 analysis failed (continuing)"
sh $R/EXP-034-phase2-optimizer/queue.sh || { echo "[queue10] EXP-034 stop"; exit 1; }
python lab/tools/guarded_run.py -- python $R/EXP-034-phase2-optimizer/analyze.py || echo "[queue10] EXP-034 analysis failed (continuing)"
sh $R/EXP-036-init-conflict/queue.sh || { echo "[queue10] EXP-036 stop"; exit 1; }
python lab/tools/guarded_run.py -- python $R/EXP-036-init-conflict/analyze.py || echo "[queue10] EXP-036 analysis failed (continuing)"
sh $R/queue_s5.sh || { echo "[queue10] queue_s5 stop"; exit 1; }
echo "[queue10] all done"
