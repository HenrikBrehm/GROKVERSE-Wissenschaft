#!/bin/sh
# EXP-046 (session 12, UNTESTED): split steering in the non-abelian group D_59, seeds 140-149, arms F/G (+ secondary R).
# GPU only (rule 16d). Needs GPU-001 PASS first. Usage: sh queue.sh [J]. Every run through guarded_run.py.
# Completed runs are skipped by group_train.py (exit 0). Resume = rerun. Exit 3 = guard refused (propagated).
J=${1:-4}
R=lab/experiments
G=lab/tools/guarded_run.py
GPY=.venv-gpu/Scripts/python.exe
E=$R/EXP-046-dihedral-steering
grep -q '"pass": true' $R/GPU-001-equivalence/verdict_equivalence.json || { echo "[exp046] GPU-001 not passed, stop"; exit 1; }
python $G --min-minutes 2 -- python $E/analyze.py --selftest || { rc=$?; echo "[exp046] selftest failed rc $rc"; exit $rc; }
# smoke: 50 steps on the GPU, then check the run record
python $G --min-minutes 3 -- $GPY $E/group_train.py --seed 140 --steps 50 --device cuda \
  --split-file $E/splits/split_D59_seed140_eps2.0_F.npy --out-root $E/raw_smoke --force || { rc=$?; echo "[exp046] smoke failed rc $rc"; exit $rc; }
python $G --min-minutes 2 -- python -c "
import json,glob; r=json.load(open(glob.glob('$E/raw_smoke/*/result.json')[0]))
assert r['status']=='completed' and r['device']=='cuda' and r['order']==118 and r['config']['p']==118, r['status']
assert r['run_id'].endswith('_devcuda') and len(r['final_top_m_irreps'])==5, r['run_id']
print('[exp046] smoke ok', r['run_id'], r['sec_per_step'], 's/step', r.get('cuda_max_mem_mb'), 'MB')" || { echo "[exp046] smoke check failed"; exit 1; }
REFUSED=$E/.refused; rm -f $REFUSED
job() {  # $1 seed $2 eps $3 arm
  [ -f $REFUSED ] && return 0
  python $G --min-minutes 5 -- $GPY $E/group_train.py --seed $1 --steps 2000 --device cuda \
    --split-file $E/splits/split_D59_seed$1_eps$2_$3.npy --out-root $E/raw
  rc=$?
  [ $rc -eq 3 ] && touch $REFUSED
  [ $rc -ne 0 ] && echo "[exp046] seed $1 $3 failed rc $rc"
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
for s in 140 141 142 143 144 145 146 147 148 149; do echo "$s 2.0 F"; echo "$s 2.0 G"; done | batch
[ -f $REFUSED ] && { echo "[exp046] guard refused, stop"; exit 3; }
python $G --min-minutes 2 -- python $E/analyze.py || echo "[exp046] analysis failed"
for s in 140 141 142 143 144 145 146 147 148 149; do echo "$s 0.0 R"; done | batch
[ -f $REFUSED ] && { echo "[exp046] guard refused, stop"; exit 3; }
python $G --min-minutes 2 -- python $E/analyze.py || echo "[exp046] analysis failed"
echo "[exp046] done"
