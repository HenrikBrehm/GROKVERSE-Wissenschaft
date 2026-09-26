#!/bin/sh
# EXP-044 (session 11, UNTESTED): early lock-in (K4) on the EXP-043 tasks that were judged "steuerbar". GPU only.
# Usage: sh queue.sh [J]. Needs GPU-001 PASS and EXP-043 summary.json. Every run through guarded_run.py; completed runs skip.
J=${1:-4}
R=lab/experiments
G=lab/tools/guarded_run.py
GPY=.venv-gpu/Scripts/python.exe
FB=$R/EXP-001-freq-ban/freq_ban.py
E=$R/EXP-044-generalize-lockin
S=$E/splits
grep -q '"pass": true' $R/GPU-001-equivalence/verdict_equivalence.json || { echo "[exp044] GPU-001 not passed, stop"; exit 1; }
TASKS=$(python -c "
import json; t=json.load(open('$R/EXP-043-generalize-steering/summary.json'))['tasks']
print(' '.join(k for k, v in t.items() if v.get('verdict') == 'steuerbar'))") || { echo "[exp044] no EXP-043 summary, stop"; exit 1; }
[ -n "$TASKS" ] || { echo "[exp044] no task steuerbar in EXP-043: EXP-044 not run (by design)"; exit 0; }
echo "[exp044] tasks: $TASKS"
set -e
# smoke: switch path with --p/--task on the GPU (60 steps, switch at 30), then check the record
python $G --min-minutes 3 -- $GPY $FB --seed 80 --condition baseline --steps 60 --threads 1 --device cuda --p 113 --task mul \
  --split-file $S/mul113_seed80_train_F.npy --test-file $S/mul113_seed80_test.npy --switch-split-file $S/mul113_seed80_train_G.npy \
  --switch-step 30 --spectra-at 30,60 --out-root $E/raw_smoke --force
python $G --min-minutes 2 -- python -c "
import json,glob; r=json.load(open(glob.glob('$E/raw_smoke/*/result.json')[0]))
sw=r['events']['switch']; assert r['status']=='completed' and sw['step']==30 and r['device']=='cuda' and r['run_id'].startswith('EXP-044_'), r['run_id']
assert sw['n_G_minus_F'] > 2000, sw
print('[exp044] smoke ok', r['run_id'], sw)"
set +e
ST=$E/.status; rm -rf $ST; mkdir -p $ST   # Codex s12: failures/refusals recorded, not swallowed
job() {  # $1 task$p (e.g. mul113) $2 seed $3 kind (F | G | switch step)
  t=${1%%[0-9]*}; p=${1#$t}; st=$S/$1_seed$2
  if [ "$3" = F ] || [ "$3" = G ]; then
    python $G --min-minutes 10 -- $GPY $FB --seed $2 --condition baseline --steps 2000 --threads 1 --device cuda --p $p --task $t \
      --split-file ${st}_train_$3.npy --test-file ${st}_test.npy --spectra-at 50,250,2000 --out-root $E/raw
  else
    python $G --min-minutes 10 -- $GPY $FB --seed $2 --condition baseline --steps $(($3 + 2000)) --threads 1 --device cuda --p $p --task $t \
      --split-file ${st}_train_F.npy --test-file ${st}_test.npy --switch-split-file ${st}_train_G.npy --switch-step $3 \
      --spectra-at $3,$(($3 + 250)),$(($3 + 2000)) --out-root $E/raw
  fi
  rc=$?; [ $rc -eq 3 ] && touch $ST/refused
  [ $rc -ne 0 ] && { echo "[exp044] $1 seed $2 $3 failed rc $rc"; touch $ST/failed; }; return 0
}
batch() { n=0; while read a b c; do [ -f $ST/refused ] && continue; job $a $b $c & n=$((n+1)); [ $n -ge $J ] && { wait; n=0; }; done; wait; }
for task in $TASKS; do for s in 80 81 82 83 84 85 86 87 88 89; do for k in F G 25 50 150; do echo "$task $s $k"; done; done; done | batch
[ -f $ST/refused ] && { echo "[exp044] guard refused, stop"; exit 3; }
python $G --min-minutes 2 -- python $E/analyze.py || { echo "[exp044] analysis failed"; touch $ST/failed; }
[ -f $ST/failed ] && { echo "[exp044] done WITH FAILURES (see above)"; exit 1; }
echo "[exp044] done"
