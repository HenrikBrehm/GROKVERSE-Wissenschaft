#!/bin/sh
# EXP-045 (session 11, UNTESTED): split steering in the shared-embedding MLP, add mod 113, seeds 90-99, arms F/G, 10 000 steps, GPU.
# Usage: sh queue.sh [J]. Needs GPU-001 PASS. Every run through guarded_run.py; completed runs skip.
J=${1:-4}
R=lab/experiments
G=lab/tools/guarded_run.py
GPY=.venv-gpu/Scripts/python.exe
FB=$R/EXP-001-freq-ban/freq_ban.py
E=$R/EXP-045-mlp-steering
grep -q '"pass": true' $R/GPU-001-equivalence/verdict_equivalence.json || { echo "[exp045] GPU-001 not passed, stop"; exit 1; }
set -e
python $G --min-minutes 3 -- $GPY $FB --seed 90 --condition baseline --steps 50 --threads 1 --device cuda --arch mlp \
  --split-file $E/splits/split_add113_seed90_eps2.0_F.npy --spectra-at 50 --out-root $E/raw_smoke --force
python $G --min-minutes 2 -- python -c "
import json,glob; r=json.load(open(glob.glob('$E/raw_smoke/*/result.json')[0]))
assert r['status']=='completed' and r['config']['arch']=='mlp' and r['device']=='cuda' and r['run_id'].startswith('EXP-045_'), r['run_id']
print('[exp045] smoke ok', r['run_id'], r['sec_per_step'], 's/step')"
set +e
ST=$E/.status; rm -rf $ST; mkdir -p $ST   # Codex s12: failures/refusals recorded, not swallowed
job() {  # $1 seed $2 arm
  python $G --min-minutes 10 -- $GPY $FB --seed $1 --condition baseline --steps 10000 --stop-after-gen 100000 --threads 1 \
    --device cuda --arch mlp --split-file $E/splits/split_add113_seed$1_eps2.0_$2.npy --spectra-at 250,2000,5000,10000 --out-root $E/raw
  rc=$?; [ $rc -eq 3 ] && touch $ST/refused
  [ $rc -ne 0 ] && { echo "[exp045] seed $1 $2 failed rc $rc"; touch $ST/failed; }; return 0
}
n=0
for s in 90 91 92 93 94 95 96 97 98 99; do for a in F G; do
  [ -f $ST/refused ] && continue
  job $s $a & n=$((n+1)); [ $n -ge $J ] && { wait; n=0; }
done; done
wait
[ -f $ST/refused ] && { echo "[exp045] guard refused, stop"; exit 3; }
python $G --min-minutes 2 -- python $E/analyze.py || { echo "[exp045] analysis failed"; touch $ST/failed; }
[ -f $ST/failed ] && { echo "[exp045] done WITH FAILURES (see above)"; exit 1; }
echo "[exp045] done"
