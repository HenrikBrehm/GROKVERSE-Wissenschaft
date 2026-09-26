#!/bin/sh
# Session-10 master queue (written 2026-09-26, session 9; EXP-039/040/041/042 added in session 10): EXP-035 -> EXP-038 -> EXP-036 -> EXP-039 -> EXP-040 -> EXP-034 -> EXP-042 -> EXP-041 -> rest of queue_s5.
# EXP-037 is done (session 9). EXP-036 before EXP-034: EXP-037 left the origin of the reproducible "conflict frequencies"
# (init or not) as the main open question. One job at a time; every run through guarded_run.py; each part skips completed
# runs; a failed part is logged and skipped (see part()). Resume = rerun.
R=lab/experiments
# Session 10: a failing experiment no longer blocks the rest; only a guard refusal (rc 3: window/deadline) stops the queue.
part() { d=$1; shift; sh $R/$d/queue.sh "$@"; rc=$?; [ $rc -eq 0 ] && return 0
  [ $rc -eq 3 ] && { echo "[queue10] $d refused by guard (rc 3), stop"; exit 3; }
  echo "[queue10] $d failed (rc $rc), continuing with the next experiment"; }
while ps -ef | grep -v grep | grep -q "guarded_run.py"; do sleep 10; done
part EXP-035-warmup-lockin 30 31 32
python lab/tools/guarded_run.py -- python $R/EXP-035-warmup-lockin/analyze.py || echo "[queue10] EXP-035 analysis failed (continuing)"
part EXP-038-where-lockin
python lab/tools/guarded_run.py -- python $R/EXP-038-where-lockin/analyze.py || echo "[queue10] EXP-038 analysis failed (continuing)"
part EXP-036-init-conflict
python lab/tools/guarded_run.py -- python $R/EXP-036-init-conflict/analyze.py || echo "[queue10] EXP-036 analysis failed (continuing)"
python lab/tools/guarded_run.py -- python $R/EXP-036-init-conflict/analyze_p36b.py || echo "[queue10] EXP-036 P36b analysis failed (continuing)"
part EXP-039-lr-clock
python lab/tools/guarded_run.py -- python $R/EXP-039-lr-clock/analyze.py || echo "[queue10] EXP-039 analysis failed (continuing)"
part EXP-040-we-init-scale
python lab/tools/guarded_run.py -- python $R/EXP-040-we-init-scale/analyze.py || echo "[queue10] EXP-040 analysis failed (continuing)"
part EXP-034-phase2-optimizer
python lab/tools/guarded_run.py -- python $R/EXP-034-phase2-optimizer/analyze.py || echo "[queue10] EXP-034 analysis failed (continuing)"
part EXP-042-bias-strength
python lab/tools/guarded_run.py -- python $R/EXP-042-bias-strength/analyze.py || echo "[queue10] EXP-042 analysis failed (continuing)"
part EXP-041-imprint
python lab/tools/guarded_run.py -- python $R/EXP-041-imprint/analyze.py || echo "[queue10] EXP-041 analysis failed (continuing)"
sh $R/queue_s5.sh || echo "[queue10] queue_s5 stopped (rc $?)"
echo "[queue10] all done"
