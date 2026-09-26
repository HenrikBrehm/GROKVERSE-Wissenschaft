#!/bin/sh
# Sequential EXP-003d baseline + EXP-010 init_swap per seed (one job at a time).
# Each run is started only if the guard grants >= 33 min (worst case 15000 steps * 0.127 s).
# Completed runs are skipped by freq_ban.py itself (exits 1 with "already completed").
# Stops on guard refusal (3) or timeout (124).
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
run() {
  python lab/tools/guarded_run.py --min-minutes 33 -- python $F "$@"
  rc=$?
  if [ $rc -eq 3 ] || [ $rc -eq 124 ]; then echo "[pairs] stop, rc=$rc"; exit $rc; fi
}
for S in ${SEEDS:-10 11 12 13 14 15 16 17 18 19}; do
  run --seed $S --condition baseline --stop-after-gen 25 --out-root lab/experiments/EXP-003-early-prediction/raw_d
  run --seed $S --condition init_swap --stop-after-gen 25 --out-root lab/experiments/EXP-010-init-swap/raw
done
echo "[pairs] all seeds done"
