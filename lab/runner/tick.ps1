<#
.SYNOPSIS
  GROKVERSE lab outer runner - one "tick". Called every 10 minutes by the Windows
  scheduled task "GROKVERSE-Lab-Runner". Makes NO model request unless a session is due.

.DESCRIPTION
  1. lab/STOP present          -> status 'stopped', disables its own scheduled task, exits.
  2. status 'halted_error'     -> exits (3 consecutive unknown failures; needs a human).
  3. lock held by live process -> exits (no parallel sessions).
  4. now < next_start_utc      -> exits.
  5. otherwise starts ONE `claude -p` session (prompt = SESSION_PREAMBLE.md + PROMPT.md),
     session deadline = start + 180 min (only a context chunk, not a work limit),
     hard timeout 200 min, then classifies the outcome:
       completed      -> next session at the next tick (continuous work, user wish 2026-09-25)
       usage_limit    -> reset + 60 s, or +5 h if no reliable reset time
       rate_limited   -> retry after 15 min (short API rate limit / overload, no reset time)
       timeout_killed | error -> retry after 30 min (3 in a row -> halted_error).
  A session whose runner died (task limit, reboot) is found via lock + recorded claude PID/start time:
  status 'running' without a live runner -> outcome 'interrupted' and resume at the next tick.
  Missed slots are never replayed: a due tick runs exactly one session.

  Windows PowerShell 5.1 compatible. Manual dry check: tick.ps1 -WhatIf
#>
[CmdletBinding()]
param([switch]$WhatIf)

$ErrorActionPreference = 'Stop'
$Root      = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$LabDir    = Join-Path $Root 'lab'
$StateFile = Join-Path $LabDir 'runner-state.json'
$StopFile  = Join-Path $LabDir 'STOP'
$LockFile  = Join-Path $PSScriptRoot 'session.lock'
$LogDir    = Join-Path $PSScriptRoot 'logs'
$TaskName  = 'GROKVERSE-Lab-Runner'

$IntervalHours       = 5     # only the retry delay after a usage limit without a parsable reset time
$SessionBudgetMin    = 180   # context chunk; the next session follows right after (continuous mode)
$HardTimeoutMin      = 200   # hang protection only
$ErrorBackoffMin     = 30
$RateLimitBackoffMin = 15    # short API rate limit / overload (no quota reset time): retry soon, not after 5 h
$MaxResetAheadDays   = 8     # a parsed reset time further ahead than this is treated as implausible
$ResetBufferSec      = 60
$MaxConsecutiveFails = 3

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$TickLog = Join-Path $LogDir 'tick.log'

function Write-Log([string]$msg) {
    $line = '{0}  {1}' -f ([DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')), $msg
    Add-Content -Path $TickLog -Value $line -Encoding UTF8
}

function Read-State {
    if (-not (Test-Path $StateFile)) { throw "runner state missing: $StateFile" }
    return (Get-Content -Raw -Encoding UTF8 $StateFile | ConvertFrom-Json)
}

function Set-Field($obj, [string]$name, $value) {
    $obj | Add-Member -NotePropertyName $name -NotePropertyValue $value -Force
}

function Save-State($state) {
    Set-Field $state 'updated_utc' ([DateTime]::UtcNow.ToString('o'))
    $tmp = "$StateFile.tmp"
    $json = $state | ConvertTo-Json -Depth 6
    [IO.File]::WriteAllText($tmp, $json, (New-Object Text.UTF8Encoding $false))   # no BOM: Python-readable
    Move-Item -Force -Path $tmp -Destination $StateFile
}

function ConvertTo-Utc([string]$iso) {
    if ([string]::IsNullOrWhiteSpace($iso)) { return $null }
    return [DateTime]::Parse($iso, [Globalization.CultureInfo]::InvariantCulture,
        [Globalization.DateTimeStyles]::AdjustToUniversal -bor [Globalization.DateTimeStyles]::AssumeUniversal)
}

# IANA -> Windows time zone ids for the reset-time parser (unknown zone => not reliable)
$TzMap = @{
    'Europe/Berlin' = 'W. Europe Standard Time'; 'Europe/Vienna' = 'W. Europe Standard Time'
    'Europe/Zurich' = 'W. Europe Standard Time'; 'Europe/Amsterdam' = 'W. Europe Standard Time'
    'Europe/Paris' = 'Romance Standard Time'; 'Europe/London' = 'GMT Standard Time'
    'UTC' = 'UTC'; 'Etc/UTC' = 'UTC'
    'America/New_York' = 'Eastern Standard Time'; 'America/Los_Angeles' = 'Pacific Standard Time'
}

function Get-ResetTimeUtc([string]$text, [DateTime]$nowUtc) {
    # Form 1: "...limit reached|1758812400" (epoch seconds, UTC by definition)
    $m = [regex]::Match($text, '(?i)limit reached\|(\d{10})')
    if ($m.Success) {
        $t = [DateTimeOffset]::FromUnixTimeSeconds([int64]$m.Groups[1].Value).UtcDateTime
        return @{ utc = $t; how = 'epoch' }
    }
    # Form 2: "resets 4pm (Europe/Berlin)" / "resets Oct 2, 4:30pm (Europe/Berlin)"
    $m = [regex]::Match($text, '(?i)resets\s+(?:at\s+)?(?<when>[A-Za-z0-9 ,:.]+?)\s*\((?<tz>[A-Za-z_]+(?:/[A-Za-z_]+)?)\)')
    if (-not $m.Success) { return $null }
    $tzId = $TzMap[$m.Groups['tz'].Value]
    if (-not $tzId) { return $null }
    $tz = [TimeZoneInfo]::FindSystemTimeZoneById($tzId)
    $when = ($m.Groups['when'].Value -replace '\s+', ' ').Trim().ToUpperInvariant()
    $inv = [Globalization.CultureInfo]::InvariantCulture
    $nowLocal = [TimeZoneInfo]::ConvertTimeFromUtc($nowUtc, $tz)
    $parsed = [DateTime]::MinValue
    $withDate = @('MMM d, htt', 'MMM d, h:mmtt', 'MMM d htt', 'MMM d h:mmtt', 'MMM d, h tt', 'MMM d, h:mm tt')
    $timeOnly = @('htt', 'h:mmtt', 'h tt', 'h:mm tt', 'HH:mm')
    foreach ($f in $withDate) {
        if ([DateTime]::TryParseExact($when, $f, $inv, 0, [ref]$parsed)) {
            $local = New-Object DateTime ($nowLocal.Year, $parsed.Month, $parsed.Day, $parsed.Hour, $parsed.Minute, 0)
            if ($local -lt $nowLocal.AddDays(-1)) { $local = $local.AddYears(1) }
            return @{ utc = [TimeZoneInfo]::ConvertTimeToUtc($local, $tz); how = 'date_time_tz' }
        }
    }
    foreach ($f in $timeOnly) {
        if ([DateTime]::TryParseExact($when, $f, $inv, 0, [ref]$parsed)) {
            $local = $nowLocal.Date.AddHours($parsed.Hour).AddMinutes($parsed.Minute)
            if ($local -le $nowLocal) { $local = $local.AddDays(1) }
            return @{ utc = [TimeZoneInfo]::ConvertTimeToUtc($local, $tz); how = 'time_tz_next_occurrence' }
        }
    }
    return $null
}

# true if a process with this PID is alive AND started at the recorded time (guards against PID reuse)
function Test-LiveProcess([int]$procId, [string]$startIso) {
    if ($procId -le 0) { return $false }
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if (-not $proc) { return $false }
    if ([string]::IsNullOrWhiteSpace($startIso)) { return $true }
    try { return ([math]::Abs(($proc.StartTime.ToUniversalTime() - (ConvertTo-Utc $startIso)).TotalSeconds) -lt 2) }
    catch { return $true }
}

function Test-LockHeld {
    if (-not (Test-Path $LockFile)) { return $false }
    $held = Get-Content -Raw $LockFile -ErrorAction SilentlyContinue
    $lockPid = 0; $lockStart = $null
    if ($held -match 'pid=(\d+)') { $lockPid = [int]$Matches[1] }
    if ($held -match 'pstart=(\S+)') { $lockStart = $Matches[1] }
    return (Test-LiveProcess $lockPid $lockStart)
}

function Enter-Lock {
    if (Test-Path $LockFile) {
        $held = Get-Content -Raw $LockFile -ErrorAction SilentlyContinue
        if (Test-LockHeld) { return $false }
        Write-Log "stale lock removed ($held)"
        Remove-Item -Force $LockFile
    }
    try {
        $fs = [System.IO.File]::Open($LockFile, 'CreateNew', 'Write', 'None')
        $pstart = (Get-Process -Id $PID).StartTime.ToUniversalTime().ToString('o')
        $bytes = [Text.Encoding]::UTF8.GetBytes("pid=$PID pstart=$pstart started=$([DateTime]::UtcNow.ToString('o'))")
        $fs.Write($bytes, 0, $bytes.Length); $fs.Close()
        return $true
    } catch { return $false }
}

function Exit-Lock { Remove-Item -Force -ErrorAction SilentlyContinue $LockFile }

# ------------------------------------------------------------------ main ---
$state = Read-State
$nowUtc = [DateTime]::UtcNow

if (Test-Path $StopFile) {
    if ($state.status -ne 'stopped') {
        Set-Field $state 'status' 'stopped'
        Set-Field $state 'pause_reason' 'lab/STOP present - no automatic resumption'
        Set-Field $state 'next_start_utc' $null
        Save-State $state
        Write-Log 'STOP file found: status=stopped, disabling scheduled task'
        if (-not $WhatIf) { Disable-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue | Out-Null }
    }
    exit 0
}
if ($state.status -in @('halted_error', 'stopped', 'prepared_not_activated')) { exit 0 }

# Reconcile a session whose runner died (task limit, reboot, crash): status still 'running' but no live runner.
if ($state.status -eq 'running' -and -not (Test-LockHeld)) {
    if (Test-LiveProcess ([int]$state.session_claude_pid) $state.session_claude_start) {
        Write-Log "runner gone but its claude process $($state.session_claude_pid) is still alive - not starting a parallel session"
        exit 0
    }
    if ($WhatIf) { Write-Host '[WhatIf] previous session would be marked interrupted and resumed now'; exit 0 }
    Set-Field $state 'status' 'idle'
    Set-Field $state 'last_outcome' 'interrupted'
    Set-Field $state 'last_end_utc' $nowUtc.ToString('o')
    Set-Field $state 'next_start_utc' $nowUtc.ToString('o')      # resume now instead of waiting on the provisional time
    Save-State $state
    Write-Log 'previous session was interrupted (runner gone, no claude process): outcome=interrupted, resuming now'
}

$next = ConvertTo-Utc $state.next_start_utc
if ($next -and $nowUtc -lt $next) { exit 0 }          # not due: no model request
if ($WhatIf) { Write-Host "[WhatIf] session would start now ($nowUtc UTC; next was $next)"; exit 0 }

if (-not (Enter-Lock)) { Write-Log 'due, but a session holds the lock - skipping'; exit 0 }
try {
    $claude = (Get-Command claude -ErrorAction Stop).Source
    $stamp = $nowUtc.ToString('yyyyMMddTHHmmssZ')
    $promptFile = Join-Path $LogDir "prompt_$stamp.txt"
    $outFile = Join-Path $LogDir "session_$stamp.out.json"
    $errFile = Join-Path $LogDir "session_$stamp.err.txt"
    $preamble = Get-Content -Raw -Encoding UTF8 (Join-Path $PSScriptRoot 'SESSION_PREAMBLE.md')
    $mission = Get-Content -Raw -Encoding UTF8 (Join-Path $PSScriptRoot 'PROMPT.md')
    [IO.File]::WriteAllText($promptFile, $preamble + "`n" + $mission, (New-Object Text.UTF8Encoding $false))

    $deadline = $nowUtc.AddMinutes($SessionBudgetMin)
    Set-Field $state 'status' 'running'
    Set-Field $state 'last_start_utc' $nowUtc.ToString('o')
    # provisional only (overwritten at session end); a dead runner is reconciled above, not by this time
    Set-Field $state 'next_start_utc' $nowUtc.AddMinutes($HardTimeoutMin + 15).ToString('o')
    Set-Field $state 'session_deadline_utc' $deadline.ToString('o')
    Set-Field $state 'pause_reason' $null
    Set-Field $state 'sessions_started' ([int]$state.sessions_started + 1)
    Save-State $state
    Write-Log "session start (deadline $($deadline.ToString('o')), log $outFile)"

    $env:LAB_SESSION_DEADLINE_UTC = $deadline.ToString('o')
    $cliArgs = @('-p', '--output-format', 'json', '--permission-mode', 'auto',
                 '--permission-prompts', 'none', '--name', "GROKVERSE-lab-$stamp")
    $p = Start-Process -FilePath $claude -ArgumentList $cliArgs -WorkingDirectory $Root `
        -RedirectStandardInput $promptFile -RedirectStandardOutput $outFile `
        -RedirectStandardError $errFile -NoNewWindow -PassThru
    $null = $p.Handle   # keep the handle so ExitCode is available after exit (PS 5.1 quirk)
    $s2 = Read-State
    Set-Field $s2 'session_claude_pid' $p.Id
    Set-Field $s2 'session_claude_start' $p.StartTime.ToUniversalTime().ToString('o')
    Save-State $s2
    $finished = $p.WaitForExit($HardTimeoutMin * 60 * 1000)
    $endUtc = [DateTime]::UtcNow

    $outcome = 'error'; $exitCode = $null
    if (-not $finished) {
        & taskkill.exe /PID $p.Id /T /F | Out-Null
        $null = $p.WaitForExit(60000)
        $outcome = 'timeout_killed'
    } else {
        $exitCode = $p.ExitCode
    }
    $text = ''
    if (Test-Path $outFile) { $text += (Get-Content -Raw $outFile -ErrorAction SilentlyContinue) }
    if (Test-Path $errFile) { $text += "`n" + (Get-Content -Raw $errFile -ErrorAction SilentlyContinue) }
    $isError = $true      # unparsable output or a missing is_error field count as an error
    $j = $null
    try {
        $j = (Get-Content -Raw $outFile) | ConvertFrom-Json
        if ($null -ne $j.is_error) { $isError = [bool]$j.is_error }
    } catch { }

    # only a FAILED session is inspected for limit messages, and only its final result text plus the
    # end of stderr - not the whole transcript, where a quoted limit message could appear
    $failed = $isError -or ($finished -and $exitCode -ne 0)
    $limitText = ''
    if ($j -and $j.result) { $limitText += [string]$j.result }
    if (Test-Path $errFile) {
        $errText = '' + (Get-Content -Raw $errFile -ErrorAction SilentlyContinue)   # empty file -> '' (not $null)
        $limitText += "`n" + $errText.Substring([math]::Max(0, $errText.Length - 4000))
    }
    if (-not $j) { $limitText += "`n" + $text.Substring([math]::Max(0, $text.Length - 4000)) }
    if ($j -and $j.errors) { $limitText += "`n" + (($j.errors | ForEach-Object { [string]$_ }) -join "`n") }
    $limitHit = $failed -and ($limitText -match '(?i)(usage limit|limit reached|hit your (usage )?limit|out of (extra )?usage)')
    $rateHit = $failed -and -not $limitHit -and ($limitText -match '(?i)(rate[_ ]limit|\b429\b|overloaded)')
    # service-side outage (e.g. the auto-mode safety check returned no verdict, 2026-09-29): transient, not our fault
    $serviceHit = $failed -and -not $limitHit -and -not $rateHit -and
        ($limitText -match '(?i)(no safety verdict|auto mode is unavailable|internal server error|\b50[234]\b|service unavailable)')
    $state = Read-State
    Set-Field $state 'session_claude_pid' $null
    Set-Field $state 'session_claude_start' $null
    if ($serviceHit) {
        $outcome = 'service_unavailable'
        Set-Field $state 'next_start_utc' $endUtc.AddMinutes($RateLimitBackoffMin).ToString('o')
        Set-Field $state 'status' 'idle'
        Set-Field $state 'pause_reason' 'transient service outage (not counted as a failure)'
    } elseif ($rateHit) {
        $outcome = 'rate_limited'
        Set-Field $state 'next_start_utc' $endUtc.AddMinutes($RateLimitBackoffMin).ToString('o')
        Set-Field $state 'status' 'idle'
        Set-Field $state 'pause_reason' 'short API rate limit / overload'
    } elseif ($limitHit) {
        $outcome = 'usage_limit'
        $reset = Get-ResetTimeUtc $limitText $endUtc
        if ($reset -and ($reset.utc -le $endUtc -or $reset.utc -gt $endUtc.AddDays($MaxResetAheadDays))) {
            Write-Log "implausible reset time $($reset.utc.ToString('o')) ignored"
            $reset = $null
        }
        if ($reset) {
            $nextStart = $reset.utc.AddSeconds($ResetBufferSec)
            Set-Field $state 'known_reset_utc' $reset.utc.ToString('o')
            Set-Field $state 'reset_parse' $reset.how
        } else {
            $nextStart = $endUtc.AddHours($IntervalHours)
            Set-Field $state 'known_reset_utc' $null
            Set-Field $state 'reset_parse' 'none - retry after 5 h (not a claim that the limit resets then)'
        }
        Set-Field $state 'next_start_utc' $nextStart.ToString('o')
        Set-Field $state 'status' 'paused_usage_limit'
        Set-Field $state 'pause_reason' 'usage limit reported by the CLI'
        Set-Field $state 'consecutive_failures' 0
    } elseif ($outcome -ne 'timeout_killed' -and $exitCode -eq 0 -and -not $isError) {
        $outcome = 'completed'
        Set-Field $state 'next_start_utc' $endUtc.ToString('o')      # continue at the next tick
        Set-Field $state 'status' 'idle'
        Set-Field $state 'consecutive_failures' 0
    } else {
        Set-Field $state 'next_start_utc' $endUtc.AddMinutes($ErrorBackoffMin).ToString('o')
        $fails = [int]$state.consecutive_failures + 1
        Set-Field $state 'consecutive_failures' $fails
        if ($fails -ge $MaxConsecutiveFails) {
            Set-Field $state 'status' 'halted_error'
            Set-Field $state 'pause_reason' "$fails consecutive failed sessions - human check required (see $errFile)"
        } else {
            Set-Field $state 'status' 'idle_after_error'
        }
    }
    Set-Field $state 'last_end_utc' $endUtc.ToString('o')
    Set-Field $state 'last_outcome' $outcome
    Set-Field $state 'last_exit_code' $exitCode
    Set-Field $state 'last_session_minutes' ([math]::Round(($endUtc - $nowUtc).TotalMinutes, 1))
    Set-Field $state 'total_session_minutes' ([math]::Round([double]$state.total_session_minutes + ($endUtc - $nowUtc).TotalMinutes, 1))
    Save-State $state
    Write-Log "session end: outcome=$outcome exit=$exitCode next=$($state.next_start_utc)"
} catch {
    Write-Log "tick error: $($_.Exception.Message) (line $($_.InvocationInfo.ScriptLineNumber))"
    try {
        $s = Read-State
        Set-Field $s 'consecutive_failures' ([int]$s.consecutive_failures + 1)
        if ([int]$s.consecutive_failures -ge $MaxConsecutiveFails) { Set-Field $s 'status' 'halted_error' }
        elseif ($s.status -eq 'running') { Set-Field $s 'status' 'idle_after_error' }
        Set-Field $s 'next_start_utc' ([DateTime]::UtcNow.AddMinutes($ErrorBackoffMin).ToString('o'))
        Set-Field $s 'pause_reason' "tick error: $($_.Exception.Message)"
        Save-State $s
    } catch { }
} finally {
    Remove-Item Env:\LAB_SESSION_DEADLINE_UTC -ErrorAction SilentlyContinue
    Exit-Lock
}
