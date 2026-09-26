#!/bin/sh
# SUPERSEDED (session 13, Astra review point 11): use `python lab/tools/night_program.py` instead. Kept as history.
echo "[gpu11] superseded by lab/tools/night_program.py (Astra 11), not run"; exit 1
# Session-11 GPU master queue (UNTESTED): GPU-001 -> EXP-043 -> EXP-046 -> EXP-047 -> EXP-048 -> EXP-049 -> EXP-044 (conditional on EXP-043) -> EXP-045.
# Runs in parallel to the CPU queue (queue_s10.sh); all GPU runs carry --device cuda. Every run through guarded_run.py.
# Resume = rerun (completed runs skip; GPU-001 reruns its checks, ~15 min, unless all three verdicts passed).
# Codex s12: fail closed. rc 3 (guard refused) anywhere stops everything; any other failure is logged, the next
# experiment still runs, and the master exits 1 at the end ("done WITH FAILURES").
R=lab/experiments
passed() { [ -f $R/GPU-001-equivalence/verdict_$1.json ] && grep -q '"pass": true' $R/GPU-001-equivalence/verdict_$1.json; }
if passed regression && passed equivalence && passed throughput; then
  echo "[gpu11] GPU-001 already passed (regression, equivalence, throughput), skipping it"
else
  sh $R/GPU-001-equivalence/queue.sh; rc=$?
  [ $rc -eq 124 ] && rc=3   # s13: a guard timeout at the session deadline is a refusal, not a failure
  [ $rc -ne 0 ] && { echo "[gpu11] GPU-001 failed or refused (rc $rc), stop: no GPU runs"; exit $rc; }
  { passed regression && passed equivalence && passed throughput; } || { echo "[gpu11] GPU-001 verdicts incomplete, stop"; exit 1; }
fi
J=$(python -c "
import json; t=json.load(open('$R/GPU-001-equivalence/verdict_throughput.json'))['levels']
ok={k: v for k, v in t.items() if v['complete']}
best=max(ok.items(), key=lambda kv:(round(kv[1]['aggregate_steps_per_s'],1), -int(kv[0][1:])))
print(int(best[0][1:]))") || { echo "[gpu11] cannot read throughput verdict, stop"; exit 1; }
echo "[gpu11] parallel GPU processes J=$J"
FAIL=0
part() {  # $1 name, rest: command
  n=$1; shift
  "$@"; rc=$?
  [ $rc -eq 3 ] && { echo "[gpu11] $n: guard refused, stop"; exit 3; }
  [ $rc -ne 0 ] && { echo "[gpu11] $n failed (rc $rc), continuing with the next experiment"; FAIL=1; }
  return 0
}
part EXP-043 sh $R/EXP-043-generalize-steering/queue.sh $J
part EXP-046 sh $R/EXP-046-dihedral-steering/queue.sh $J
part EXP-047 sh $R/EXP-047-marginal-control/queue.sh $J
part EXP-048 sh $R/EXP-048-intadd-steering/queue.sh $J
part EXP-049 sh $R/EXP-049-width-steering/queue.sh $J
part EXP-044 sh $R/EXP-044-generalize-lockin/queue.sh $J
part EXP-045 sh $R/EXP-045-mlp-steering/queue.sh $J
[ $FAIL -ne 0 ] && { echo "[gpu11] done WITH FAILURES"; exit 1; }
echo "[gpu11] all done"
