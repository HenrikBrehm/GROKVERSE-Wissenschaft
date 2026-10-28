<#
  Registers (or re-registers) the per-user scheduled task "GROKVERSE-Lab-Runner":
  a tick every 10 minutes, indefinitely. The tick itself decides whether a session is due
  (5 h after the last actual session start, or reset + 60 s after a usage limit).
  Runs only while this user is logged on (no stored password). Refuses if lab/STOP exists.
    powershell -NoProfile -ExecutionPolicy Bypass -File lab\runner\install_task.ps1
#>
$ErrorActionPreference = 'Stop'
$TaskName = 'GROKVERSE-Lab-Runner'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if (Test-Path (Join-Path $Root 'lab\STOP')) { throw 'lab/STOP exists - not (re)activating the runner.' }
$vbs = Join-Path $PSScriptRoot 'launch_hidden.vbs'
$action = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument ('"' + $vbs + '"') -WorkingDirectory $Root
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 10)
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 4)   # > tick hard timeout 200 min + cleanup
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings `
    -Principal $principal -Description 'GROKVERSE research lab outer runner (lab/runner/README.md)' -Force | Out-Null
Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo | Select-Object TaskName, NextRunTime, LastRunTime
