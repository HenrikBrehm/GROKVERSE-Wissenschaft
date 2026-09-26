#!/bin/sh
# EXP-048 (session 13, UNTESTED): split steering on NON-modular integer addition, seeds 160-169, arms F/G (+ secondary R).
# GPU only (rule 16d). Needs GPU-001 PASS first. Usage: sh queue.sh [J]. Every run through guarded_run.py.
# Completed runs are skipped by intadd_train.py (exit 0). Resume = rerun. Exit 3 = guard refused (propagated),
# other failures are counted and the queue exits 1 at the end.
J=${1:-4}
R=lab/experiments
G=lab/tools/guarded_run.py
GPY=.venv-gpu/Scripts/python.exe
E=$R/EXP-048-intadd-steering
grep -q '"pass": true' $R/GPU-001-equivalence/verdict_equivalence.json || { echo "[exp048] GPU-001 not passed, stop"; exit 1; }
python $G --min-minutes 2 -- python $E/analyze.py --selftest || { rc=$?; echo "[exp048] selftest failed rc $rc"; exit $rc; }
# smoke: 50 steps on the GPU into raw_smoke, then check the run record
rm -rf $E/raw_smoke
python $G --min-minutes 3 -- $GPY $E/intadd_train.py --seed 160 --steps 50 --device cuda \
  --split-file $E/splits/split_intadd113_seed160_eps2.0_F.npy --out-root $E/raw_smoke --force || { rc=$?; echo "[exp048] smoke failed rc $rc"; exit $rc; }
python $G --min-minutes 2 -- python -c "
import json,glob; r=json.load(open(glob.glob('$E/raw_smoke/*/result.json')[0]))
assert r['status']=='completed' and r['device']=='cuda' and r['n_out']==225 and r['config']['p']==225, r['status']
assert r['run_id'].endswith('_devcuda') and len(r['final_top_m_freqs'])==5 and r['steps_completed']==50, r['run_id']
print('[exp048] smoke ok', r['run_id'], r['sec_per_step'], 's/step', r.get('cuda_max_mem_mb'), 'MB')" || { echo "[exp048] smoke check failed"; exit 1; }
ST=$E/.status; rm -rf $ST; mkdir -p $ST
job() {  # $1 seed $2 eps $3 arm
  [ -f $ST/refused ] && return 0
  python $G --min-minutes 5 -- $GPY $E/intadd_train.py --seed $1 --steps 2000 --device cuda \
    --split-file $E/splits/split_intadd113_seed$1_eps$2_$3.npy --out-root $E/raw
  rc=$?
  [ $rc -eq 3 ] && touch $ST/refused
  [ $rc -ne 0 ] && { echo "[exp048] seed $1 $3 failed rc $rc"; touch $ST/failed; }
  return 0
}
batch() {  # run the lines of stdin as jobs, J at a time
  n=0
  while read s e a; do
    job $s $e $a &
    n=$((n+1)); [ $n -ge $J ] && { wait; n=0; }
  done
  wait
}
for s in 160 161 162 163 164 165 166 167 168 169; do echo "$s 2.0 F"; echo "$s 2.0 G"; done | batch
[ -f $ST/refused ] && { echo "[exp048] guard refused, stop"; exit 3; }
python $G --min-minutes 2 -- python $E/analyze.py || { echo "[exp048] analysis failed"; touch $ST/failed; }
for s in 160 161 162 163 164 165 166 167 168 169; do echo "$s 0.0 R"; done | batch
[ -f $ST/refused ] && { echo "[exp048] guard refused, stop"; exit 3; }
python $G --min-minutes 2 -- python $E/analyze.py || { echo "[exp048] analysis failed"; touch $ST/failed; }
[ -f $ST/failed ] && { echo "[exp048] done WITH FAILURES (see above)"; exit 1; }
echo "[exp048] done"
