#!/bin/sh
# Session-10 master queue (written 2026-09-26, session 9; EXP-039 added in session 10): EXP-035 -> EXP-038 -> EXP-036 -> EXP-039 -> EXP-040 -> EXP-034 -> rest of queue_s5.
# EXP-037 is done (session 9). EXP-036 before EXP-034: EXP-037 left the origin of the reproducible "conflict frequencies"
# (init or not) as the main open question. One job at a time; every run through guarded_run.py; each part skips completed
# runs and stops on failure. Resume = rerun.
R=lab/experiments
while ps -ef | grep -v grep | grep -q "guarded_run.py"; do sleep 10; done
sh $R/EXP-035-warmup-lockin/queue.sh 30 31 32 || { echo "[queue10] EXP-035 stop"; exit 1; }
python lab/tools/guarded_run.py -- python $R/EXP-035-warmup-lockin/analyze.py || echo "[queue10] EXP-035 analysis failed (continuing)"
sh $R/EXP-038-where-lockin/queue.sh || { echo "[queue10] EXP-038 stop"; exit 1; }
python lab/tools/guarded_run.py -- python $R/EXP-038-where-lockin/analyze.py || echo "[queue10] EXP-038 analysis failed (continuing)"
sh $R/EXP-036-init-conflict/queue.sh || { echo "[queue10] EXP-036 stop"; exit 1; }
python lab/tools/guarded_run.py -- python $R/EXP-036-init-conflict/analyze.py || echo "[queue10] EXP-036 analysis failed (continuing)"
python lab/tools/guarded_run.py -- python $R/EXP-036-init-conflict/analyze_p36b.py || echo "[queue10] EXP-036 P36b analysis failed (continuing)"
sh $R/EXP-039-lr-clock/queue.sh || { echo "[queue10] EXP-039 stop"; exit 1; }
python lab/tools/guarded_run.py -- python $R/EXP-039-lr-clock/analyze.py || echo "[queue10] EXP-039 analysis failed (continuing)"
sh $R/EXP-040-we-init-scale/queue.sh || { echo "[queue10] EXP-040 stop"; exit 1; }
python lab/tools/guarded_run.py -- python $R/EXP-040-we-init-scale/analyze.py || echo "[queue10] EXP-040 analysis failed (continuing)"
sh $R/EXP-034-phase2-optimizer/queue.sh || { echo "[queue10] EXP-034 stop"; exit 1; }
python lab/tools/guarded_run.py -- python $R/EXP-034-phase2-optimizer/analyze.py || echo "[queue10] EXP-034 analysis failed (continuing)"
sh $R/queue_s5.sh || { echo "[queue10] queue_s5 stop"; exit 1; }
echo "[queue10] all done"
