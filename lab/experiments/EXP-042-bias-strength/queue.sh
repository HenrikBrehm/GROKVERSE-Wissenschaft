#!/bin/sh
# EXP-042 queue: EXP-020 protocol with a G split of concentration eps_G (8 primary, 1 secondary); F/test = EXP-020.
# Per seed and eps: only G_eps (2000) + switches F -> G_eps (+2000). Only-F reference = EXP-020 run (not rerun).
# One job at a time via guarded_run.py; completed runs are skipped (exit 0); any other exit stops. Resume = rerun.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
X=lab/experiments/EXP-042-bias-strength
run() { mm=$1; shift; python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@"; rc=$?; [ $rc -eq 0 ] || { echo "[exp042] stop, rc=$rc"; exit $rc; }; }
python lab/tools/guarded_run.py --min-minutes 1 -- python $X/analyze.py --selftest || { echo "[exp042] selftest failed"; exit 1; }
for E in 8 1; do
  SP=$X/eps$E/splits; O=$X/eps$E/raw
  if [ "$E" = "8" ]; then TS="50 100 25 150"; else TS="25 10 50"; fi
  for S in ${*:-30 31 32 34}; do
    run 7 --seed $S --condition baseline --steps 2000 --stop-after-gen 8000 --split-file $SP/seed${S}_train_G.npy \
      --test-file $SP/seed${S}_test.npy --out-root $O
    for T in $TS; do
      run 7 --seed $S --condition baseline --steps $((T + 2000)) --stop-after-gen 8000 --split-file $SP/seed${S}_train_F.npy \
        --test-file $SP/seed${S}_test.npy --switch-split-file $SP/seed${S}_train_G.npy --switch-step $T --out-root $O
    done
  done
done
echo "[exp042] all done"
