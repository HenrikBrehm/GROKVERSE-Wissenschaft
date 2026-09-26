#!/bin/sh
# Session-11 GPU master queue (UNTESTED): GPU-001 -> EXP-043 -> EXP-044 (conditional on EXP-043) -> EXP-045.
# Runs in parallel to the CPU queue (queue_s10.sh); all GPU runs carry --device cuda. Every run through guarded_run.py.
# Resume = rerun (completed runs skip; GPU-001 reruns its checks, ~15 min).
R=lab/experiments
if [ -f $R/GPU-001-equivalence/verdict_equivalence.json ] && grep -q '"pass": true' $R/GPU-001-equivalence/verdict_equivalence.json \
   && [ -f $R/GPU-001-equivalence/verdict_throughput.json ]; then
  echo "[gpu11] GPU-001 already passed, skipping it"
else
  sh $R/GPU-001-equivalence/queue.sh || { echo "[gpu11] GPU-001 failed or refused (rc $?), stop: no GPU runs"; exit 1; }
fi
J=$(python -c "
import json; t=json.load(open('$R/GPU-001-equivalence/verdict_throughput.json'))
best=max(t.items(), key=lambda kv:(round(kv[1]['aggregate_steps_per_s'],1), -int(kv[0][1:])))
print(int(best[0][1:]))") || J=2
echo "[gpu11] parallel GPU processes J=$J"
sh $R/EXP-043-generalize-steering/queue.sh $J; rc=$?; [ $rc -eq 3 ] && { echo "[gpu11] guard refused, stop"; exit 3; }
sh $R/EXP-044-generalize-lockin/queue.sh $J; rc=$?; [ $rc -eq 3 ] && { echo "[gpu11] guard refused, stop"; exit 3; }
sh $R/EXP-045-mlp-steering/queue.sh $J
echo "[gpu11] all done"
