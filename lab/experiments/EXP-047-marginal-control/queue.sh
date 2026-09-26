#!/bin/sh
# EXP-047 (session 12, UNTESTED): token-count vs pair-structure control for split steering, add mod 113, seeds 150-159,
# arms eng_F, eng_G, shuf_F, shuf_G, 2000 steps, GPU only (rule 16d). Needs GPU-001 PASS. Usage: sh queue.sh [J].
# Every run through guarded_run.py; completed runs skip (freq_ban.py exit 0). Fail closed: rc 3 stops (exit 3),
# other failures are counted and the queue exits 1 at the end.
J=${1:-4}
R=lab/experiments
G=lab/tools/guarded_run.py
GPY=.venv-gpu/Scripts/python.exe
FB=$R/EXP-001-freq-ban/freq_ban.py
E=$R/EXP-047-marginal-control
grep -q '"pass": true' $R/GPU-001-equivalence/verdict_equivalence.json || { echo "[exp047] GPU-001 not passed, stop"; exit 1; }
python $G --min-minutes 2 -- python $E/analyze.py --selftest || { rc=$?; echo "[exp047] selftest failed rc $rc"; exit $rc; }
ST=$E/.status; rm -rf $ST; mkdir -p $ST
job() {  # $1 seed $2 kind $3 arm
  [ -f $ST/refused ] && return 0
  python $G --min-minutes 5 -- $GPY $FB --seed $1 --condition baseline --steps 2000 --threads 1 --device cuda \
    --split-file $E/splits/split_add113_seed$1_$2_$3.npy --out-root $E/raw
  rc=$?
  [ $rc -eq 3 ] && touch $ST/refused
  [ $rc -ne 0 ] && { echo "[exp047] seed $1 $2 $3 failed rc $rc"; touch $ST/failed; }
  return 0
}
n=0
for s in 150 151 152 153 154 155 156 157 158 159; do for k in eng shuf; do for a in F G; do
  job $s $k $a & n=$((n+1)); [ $n -ge $J ] && { wait; n=0; }
done; done; done
wait
[ -f $ST/refused ] && { echo "[exp047] guard refused, stop"; exit 3; }
python $G --min-minutes 2 -- python $E/analyze.py || { echo "[exp047] analysis failed"; touch $ST/failed; }
[ -f $ST/failed ] && { echo "[exp047] done WITH FAILURES (see above)"; exit 1; }
echo "[exp047] done"
