#!/bin/sh
# SUPERSEDED (session 13, Astra 11): run via `python lab/tools/night_program.py` (fingerprints/flags may differ here). History only.
echo "superseded by lab/tools/night_program.py, not run"; exit 1
# EXP-043 (session 11, UNTESTED): split steering on add mod 97 and mul mod 113, seeds 70-79, arms F/G (+ secondary R).
# GPU only (rule 16d: every arm and seed on the same device). Needs GPU-001 PASS first. Usage: sh queue.sh [J]
# J = parallel GPU processes (from GPU-001 verdict_throughput.json; default 4). Every run through guarded_run.py.
# Completed runs are skipped by freq_ban.py (exit 0). Resume = rerun.
J=${1:-4}
R=lab/experiments
G=lab/tools/guarded_run.py
GPY=.venv-gpu/Scripts/python.exe
FB=$R/EXP-001-freq-ban/freq_ban.py
E=$R/EXP-043-generalize-steering
grep -q '"pass": true' $R/GPU-001-equivalence/verdict_equivalence.json || { echo "[exp043] GPU-001 not passed, stop"; exit 1; }
set -e
python $G --min-minutes 2 -- python $E/analyze.py --selftest
# smoke: 50 steps, mul 113 (the new code path), then check the run record
python $G --min-minutes 3 -- $GPY $FB --seed 70 --condition baseline --steps 50 --threads 1 --device cuda --p 113 --task mul --split-file $E/splits/split_mul113_seed70_eps2.0_F.npy --spectra-at 50 --out-root $E/raw_smoke --force
python $G --min-minutes 2 -- python -c "
import json,glob; r=json.load(open(glob.glob('$E/raw_smoke/*/result.json')[0]))
assert r['status']=='completed' and r['config']['task']=='mul' and r['config']['p']==113 and r['device']=='cuda', r['status']
assert r['run_id'].startswith('EXP-043_') and r['run_id'].endswith('_mul113_devcuda'), r['run_id']
print('[exp043] smoke ok', r['run_id'], r['sec_per_step'], 's/step', r.get('cuda_max_mem_mb'), 'MB')"
set +e
ST=$E/.status; rm -rf $ST; mkdir -p $ST   # Codex s12: failures/refusals recorded, not swallowed
job() {  # $1 task $2 p $3 seed $4 eps $5 arm
  python $G --min-minutes 10 -- $GPY $FB --seed $3 --condition baseline --steps 2000 --threads 1 --device cuda --p $2 --task $1 \
    --split-file $E/splits/split_$1$2_seed$3_eps$4_$5.npy --spectra-at 50,250,500,1000,2000 --out-root $E/raw
  rc=$?; [ $rc -eq 3 ] && touch $ST/refused
  [ $rc -ne 0 ] && { echo "[exp043] $1$2 seed $3 $5 failed rc $rc"; touch $ST/failed; }; return 0
}
batch() {  # run the lines of stdin as jobs, J at a time
  n=0
  while read t p s e a; do
    [ -f $ST/refused ] && continue
    job $t $p $s $e $a &
    n=$((n+1)); [ $n -ge $J ] && { wait; n=0; }
  done
  wait
}
for s in 70 71 72 73 74 75 76 77 78 79; do for a in F G; do echo "mul 113 $s 2.0 $a"; echo "add 97 $s 2.0 $a"; done; done | batch
[ -f $ST/refused ] && { echo "[exp043] guard refused, stop"; exit 3; }
python $G --min-minutes 2 -- python $E/analyze.py || { echo "[exp043] analysis failed"; touch $ST/failed; }
# secondary: random reference splits (eps 0), not needed for the verdict
for s in 70 71 72 73 74 75 76 77 78 79; do echo "mul 113 $s 0.0 R"; echo "add 97 $s 0.0 R"; done | batch
[ -f $ST/refused ] && { echo "[exp043] guard refused, stop"; exit 3; }
python $G --min-minutes 2 -- python $E/analyze.py || { echo "[exp043] analysis failed"; touch $ST/failed; }
[ -f $ST/failed ] && { echo "[exp043] done WITH FAILURES (see above)"; exit 1; }
echo "[exp043] done"
