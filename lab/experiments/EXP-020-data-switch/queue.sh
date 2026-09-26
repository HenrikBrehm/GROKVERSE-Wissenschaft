#!/bin/sh
# EXP-020 queue (design after Nachtrag a, Codex review 2026-09-26; NOT yet run). One job at a time, every run
# through guarded_run.py. freq_ban.py exits 0 when a run is already completed, so the queue stops on EVERY
# nonzero exit. Resume: start again. After the smoke, check_smoke.py must pass before any main run.
F=lab/experiments/EXP-001-freq-ban/freq_ban.py
X=lab/experiments/EXP-020-data-switch
SP=$X/splits
run() {
  mm=$1; shift
  python lab/tools/guarded_run.py --min-minutes $mm -- python $F "$@"
  rc=$?
  if [ $rc -ne 0 ]; then echo "[queue20] stop, rc=$rc"; exit $rc; fi
}
while ps -ef | grep -v grep | grep -q "guarded_run.py"; do sleep 10; done
run 3 --seed 30 --condition baseline --steps 60 --stop-after-gen 8000 --split-file $SP/seed30_train_F.npy \
  --test-file $SP/seed30_test.npy --switch-split-file $SP/seed30_train_G.npy --switch-step 30 --out-root $X/raw_smoke
python $X/check_smoke.py || { echo "[queue20] smoke check failed"; exit 1; }
for S in 30 31 32 33 34; do
  # t = inf: only F, up to 8000 steps so that gen_F is observed; K is read at step 2000
  run 19 --seed $S --condition baseline --steps 8000 --stop-after-gen 2000 --split-file $SP/seed${S}_train_F.npy \
    --test-file $SP/seed${S}_test.npy --out-root $X/raw
  # t = 0: only G, 2000 steps (= the common post-switch G budget)
  run 7 --seed $S --condition baseline --steps 2000 --stop-after-gen 8000 --split-file $SP/seed${S}_train_G.npy \
    --test-file $SP/seed${S}_test.npy --out-root $X/raw
  for T in 150 50 25 10 400 1000; do   # 10, 25: EXP-020 Nachtrag b   # F for T steps, then exactly 2000 steps on G
    run 9 --seed $S --condition baseline --steps $((T + 2000)) --stop-after-gen 8000 \
      --split-file $SP/seed${S}_train_F.npy --test-file $SP/seed${S}_test.npy \
      --switch-split-file $SP/seed${S}_train_G.npy --switch-step $T --out-root $X/raw
  done
done
echo "[queue20] all done"
