#!/bin/sh
# GPU-001 (rule 16b/c, written 2026-09-26 session 11, UNTESTED): CPU regression of the --device edit, CPU-vs-GPU
# equivalence on stored EXP-016 runs, GPU speed and parallel throughput. Every run through guarded_run.py.
# GPU runs carry "--device cuda" so the CPU queues (queue_s10 etc.) do not wait for them.
# Stops on the first failure of steps 1-2 (the verdict script decides whether the GPU may be used).
R=lab/experiments
G=lab/tools/guarded_run.py
GPY=.venv-gpu/Scripts/python.exe
FB=$R/EXP-001-freq-ban/freq_ban.py
OUT=$R/GPU-001-equivalence
S16=$R/EXP-016-engineered-split/splits
set -e
# 0. environment (no training)
python $G --min-minutes 2 -- $GPY -c "import torch; print('[gpu001] torch', torch.__version__, 'hip', torch.version.hip, 'avail', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '-')"
# 1. CPU regression: the stored 50-step EXP-016 smoke must be reproduced exactly by the edited freq_ban.py (global python, CPU)
python $G --min-minutes 3 -- python $FB --seed 10 --condition baseline --steps 50 --split-file $S16/split_seed10_eps2.0.npy --out-root $OUT/raw_cpu_regression --force
python $G --min-minutes 2 -- python $OUT/compare.py regression
# 2. equivalence: GPU reruns of stored CPU runs EXP-016 seeds 10, 11, 12 (arm F, 2000 steps)
for s in 10 11 12; do
  python $G --min-minutes 10 -- $GPY $FB --seed $s --condition baseline --steps 2000 --threads 1 --device cuda --split-file $S16/split_seed${s}_eps2.0.npy --out-root $OUT/raw_equiv
done
python $G --min-minutes 2 -- python $OUT/compare.py equivalence
# 3. throughput: J parallel GPU processes, 500 steps each (seed 10, arm F); separate out-roots per level
# s13 review: stale raw_par results from an earlier (refused) attempt must not mix into this measurement, and a refusal (rc 3)
# or guard timeout (rc 124) of any throughput run must not produce a verdict (else J could be capped for good): exit 3.
set +e
rm -rf $OUT/raw_par $OUT/.tp_rc
mkdir -p $OUT/.tp_rc
for J in 1 2 4 8; do
  i=1
  while [ $i -le $J ]; do
    ( python $G --min-minutes 5 -- $GPY $FB --seed 10 --condition baseline --steps 500 --threads 1 --device cuda --split-file $S16/split_seed10_eps2.0.npy --out-root $OUT/raw_par/J${J}_$i --force
      rc=$?; [ $rc -ne 0 ] && echo $rc > $OUT/.tp_rc/J${J}_$i ) &
    i=$((i+1))
  done
  wait
done
if grep -qxE '3|124' $OUT/.tp_rc/* 2>/dev/null; then echo "[gpu001] throughput run refused/timed out, no verdict, stop (rc 3)"; exit 3; fi
python $G --min-minutes 2 -- python $OUT/compare.py throughput || { rc=$?; echo "[gpu001] throughput FAIL/refused rc $rc"; exit $rc; }
echo "[gpu001] done"
