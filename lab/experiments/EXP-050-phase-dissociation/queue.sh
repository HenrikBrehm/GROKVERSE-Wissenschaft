#!/bin/sh
# SUPERSEDED (session 13, Astra 11): run via `python lab/tools/night_program.py` (fingerprints/flags may differ here). History only.
echo "superseded by lab/tools/night_program.py, not run"; exit 1
# EXP-050 (session 13, UNTESTED, NOT in queue_gpu_s11.sh): M0c vs M0 dissociation, add mod 113, seeds 180-189,
# modes quadlm/anti/sym x arms F/G, 2000 steps, transformer, GPU only (rule 16d). Needs GPU-001 PASS. Usage: sh queue.sh [J].
# Every run through guarded_run.py; completed runs skip (freq_ban.py exit 0). rc 3 stops (exit 3), other failures are
# counted and the queue exits 1 at the end.
J=${1:-4}
R=lab/experiments
G=lab/tools/guarded_run.py
GPY=.venv-gpu/Scripts/python.exe
FB=$R/EXP-001-freq-ban/freq_ban.py
E=$R/EXP-050-phase-dissociation
grep -q '"pass": true' $R/GPU-001-equivalence/verdict_equivalence.json || { echo "[exp050] GPU-001 not passed, stop"; exit 1; }
python $G --min-minutes 2 -- python $E/analyze.py --selftest || { rc=$?; echo "[exp050] selftest failed rc $rc"; exit $rc; }
ST=$E/.status; rm -rf $ST; mkdir -p $ST
job() {  # $1 seed $2 mode $3 arm
  [ -f $ST/refused ] && return 0
  python $G --min-minutes 5 -- $GPY $FB --seed $1 --condition baseline --steps 2000 --threads 1 --device cuda \
    --split-file $E/splits/split_add113_seed$1_$2_$3.npy --out-root $E/raw
  rc=$?
  [ $rc -eq 3 ] || [ $rc -eq 124 ] && touch $ST/refused
  [ $rc -ne 0 ] && { echo "[exp050] seed $1 $2 $3 failed rc $rc"; touch $ST/failed; }
  return 0
}
n=0
for s in 180 181 182 183 184 185 186 187 188 189; do for m in quadlm anti sym; do for a in F G; do
  job $s $m $a & n=$((n+1)); [ $n -ge $J ] && { wait; n=0; }
done; done; done
wait
[ -f $ST/refused ] && { echo "[exp050] guard refused/timed out, stop"; exit 3; }
python $G --min-minutes 2 -- python $E/analyze.py || { echo "[exp050] analysis failed"; touch $ST/failed; }
[ -f $ST/failed ] && { echo "[exp050] done WITH FAILURES (see above)"; exit 1; }
echo "[exp050] done"
