#!/bin/sh
# EXP-049 (session 13, UNTESTED): split steering at d_model 128 vs 512, add mod 113, seeds 170-179, arms F/G, 2000 steps.
# GPU only (rule 16d). Needs GPU-001 PASS first. Usage: sh queue.sh [J]. Every run through guarded_run.py.
# Completed runs are skipped by width_train.py (exit 0). Resume = rerun. Exit 3 = guard refused (propagated),
# other failures are counted and the queue exits 1 at the end.
J=${1:-4}
R=lab/experiments
G=lab/tools/guarded_run.py
GPY=.venv-gpu/Scripts/python.exe
E=$R/EXP-049-width-steering
grep -q '"pass": true' $R/GPU-001-equivalence/verdict_equivalence.json || { echo "[exp049] GPU-001 not passed, stop"; exit 1; }
python $G --min-minutes 2 -- python $E/analyze.py --selftest || { rc=$?; echo "[exp049] selftest failed rc $rc"; exit $rc; }
# smoke: 50 steps per width on the GPU into raw_smoke, then check the run records
rm -rf $E/raw_smoke
for d in 128 512; do
  python $G --min-minutes 3 -- $GPY $E/width_train.py --seed 170 --d-model $d --steps 50 --device cuda \
    --split-file $E/splits/split_add113_seed170_eps2.0_F.npy --out-root $E/raw_smoke --force || { rc=$?; echo "[exp049] smoke d$d failed rc $rc"; exit $rc; }
done
python $G --min-minutes 2 -- python -c "
import json,glob; rs=[json.load(open(f)) for f in sorted(glob.glob('$E/raw_smoke/*/result.json'))]
assert sorted(r['d_model'] for r in rs)==[128,512], [r['d_model'] for r in rs]
for r in rs:
    assert r['status']=='completed' and r['device']=='cuda' and r['steps_completed']==50 and r['config']['d_model']==r['d_model'], r['run_id']
    assert r['run_id'].endswith('_devcuda') and len(r['final_top_m_freqs'])==5, r['run_id']
    print('[exp049] smoke ok', r['run_id'], r['n_params'], 'params', r['sec_per_step'], 's/step', r.get('cuda_max_mem_mb'), 'MB')" || { echo "[exp049] smoke check failed"; exit 1; }
ST=$E/.status; rm -rf $ST; mkdir -p $ST
job() {  # $1 seed $2 width $3 arm
  [ -f $ST/refused ] && return 0
  python $G --min-minutes 5 -- $GPY $E/width_train.py --seed $1 --d-model $2 --steps 2000 --device cuda \
    --split-file $E/splits/split_add113_seed$1_eps2.0_$3.npy --out-root $E/raw
  rc=$?
  [ $rc -eq 3 ] && touch $ST/refused
  [ $rc -ne 0 ] && { echo "[exp049] seed $1 d$2 $3 failed rc $rc"; touch $ST/failed; }
  return 0
}
batch() {  # run the lines of stdin as jobs, J at a time
  n=0
  while read s d a; do
    job $s $d $a &
    n=$((n+1)); [ $n -ge $J ] && { wait; n=0; }
  done
  wait
}
for s in 170 171 172 173 174 175 176 177 178 179; do for d in 128 512; do echo "$s $d F"; echo "$s $d G"; done; done | batch
[ -f $ST/refused ] && { echo "[exp049] guard refused, stop"; exit 3; }
python $G --min-minutes 2 -- python $E/analyze.py || { echo "[exp049] analysis failed"; touch $ST/failed; }
[ -f $ST/failed ] && { echo "[exp049] done WITH FAILURES (see above)"; exit 1; }
echo "[exp049] done"
