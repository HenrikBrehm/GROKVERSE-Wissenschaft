# Guard acceptance (Astra point 1, rule 18b1). Run ONLY inside the run window (checks it first).
#   powershell -ExecutionPolicy Bypass -File lab/tools/accept_guard.ps1
# Probes (each uses lab/tools/probe_sleep.py, which writes the PID of the real interpreter):
#   A  STOP during a run: guard must exit 3 and the child must die. lab/STOP is removed again in all cases.
#   B  guard killed alone (no /T), system python: the job object must take the child down.
#   C  guard killed alone, .venv-gpu python (launcher + real interpreter): the child must die as well.
# Output: one line per probe (PASS/FAIL) and lab/runner/logs/accept_guard.json. Exit 0 only if all pass.
$ErrorActionPreference = 'Stop'
$root = Resolve-Path (Join-Path $PSScriptRoot '..\..')
Set-Location $root
$logs = Join-Path $root 'lab\runner\logs'
$stop = Join-Path $root 'lab\STOP'

& python lab/tools/guarded_run.py --check | Out-Null   # --check itself is no run
if ($LASTEXITCODE -ne 0) { Write-Output 'window closed or guard refuses: no probes'; exit 3 }
if (Test-Path $stop) { Write-Output 'lab/STOP exists already: no probes'; exit 3 }

# the guard must be the real interpreter, not a shim (App alias), otherwise probes B/C would kill the wrong process
$sysPy = (Get-Command python).Source
if ($sysPy -like '*WindowsApps*') { Write-Output "python resolves to an App alias ($sysPy): no probes"; exit 2 }

function Start-Guarded([string]$py, [string]$pidFile, [int]$seconds) {
    Remove-Item $pidFile -ErrorAction SilentlyContinue
    $p = Start-Process -FilePath $sysPy -NoNewWindow -PassThru -ArgumentList @(
        'lab/tools/guarded_run.py', '--', $py, 'lab/tools/probe_sleep.py', $pidFile, "$seconds")
    $null = $p.Handle   # keep the handle so ExitCode is available later
    for ($i = 0; $i -lt 40 -and -not (Test-Path $pidFile); $i++) { Start-Sleep -Milliseconds 250 }
    if (-not (Test-Path $pidFile)) { throw "probe child did not start ($pidFile)" }
    return @{ guard = $p; child = [int](Get-Content $pidFile) }
}

function Test-Alive([int]$procId) { return [bool](Get-Process -Id $procId -ErrorAction SilentlyContinue) }

$results = [ordered]@{}
$venvPy = Join-Path $root '.venv-gpu\Scripts\python.exe'

# A: STOP file
$r = Start-Guarded $sysPy (Join-Path $logs 'probeA.pid') 60
try {
    Start-Sleep -Seconds 3
    New-Item -ItemType File -Path $stop | Out-Null
    $exited = $r.guard.WaitForExit(20000)
} finally {
    Remove-Item $stop -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 1
$code = if ($exited) { $r.guard.ExitCode } else { $null }
$childAlive = Test-Alive $r.child
if ($childAlive) { Stop-Process -Id $r.child -Force -ErrorAction SilentlyContinue }
if (-not $exited) { Stop-Process -Id $r.guard.Id -Force -ErrorAction SilentlyContinue }
$results['A_stop'] = [ordered]@{ pass = ($exited -and $code -eq 3 -and -not $childAlive); guard_exit = $code;
                                  child_alive_after = $childAlive; stop_removed = -not (Test-Path $stop) }

# B and C: kill only the guard process (no tree kill), the job object must take the child down
foreach ($case in @(@('B_kill_guard_system_python', $sysPy), @('C_kill_guard_venv_python', $venvPy))) {
    $r = Start-Guarded $case[1] (Join-Path $logs "probe_$($case[0]).pid") 120
    Start-Sleep -Seconds 3
    Stop-Process -Id $r.guard.Id -Force
    Start-Sleep -Seconds 3
    $childAlive = Test-Alive $r.child
    if ($childAlive) { Stop-Process -Id $r.child -Force -ErrorAction SilentlyContinue }
    $results[$case[0]] = [ordered]@{ pass = -not $childAlive; child_alive_after = $childAlive }
}

$all = -not ($results.Values | Where-Object { -not $_.pass })
$results['all_pass'] = $all
$results | ConvertTo-Json | Set-Content -Encoding utf8 (Join-Path $logs 'accept_guard.json')
foreach ($k in $results.Keys) { if ($k -ne 'all_pass') { Write-Output ("{0}: {1}" -f $k, $(if ($results[$k].pass) { 'PASS' } else { 'FAIL' })) } }
if (Test-Path $stop) { Write-Output 'WARNING: lab/STOP still exists'; exit 2 }
if ($all) { exit 0 } else { exit 1 }
