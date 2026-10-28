<#
  Registers (or re-registers) the per-user scheduled task "GROKVERSE-GPU-Daemon": every 10 minutes it starts
  lab/tools/gpu_daemon.py (hidden) unless an instance is already running (IgnoreNew). The daemon runs queued jobs
  from lab/queue/inbox independently of the Claude lab sessions and exits when there is no work.
  No execution time limit (a long job must not be killed by the task scheduler). Refuses if lab/STOP exists.
    powershell -NoProfile -ExecutionPolicy Bypass -File lab\runner\install_gpu_daemon_task.ps1
#>
$ErrorActionPreference = 'Stop'
$TaskName = 'GROKVERSE-GPU-Daemon'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if (Test-Path (Join-Path $Root 'lab\STOP')) { throw 'lab/STOP exists - not registering the GPU daemon.' }
$vbs = Join-Path $PSScriptRoot 'launch_daemon_hidden.vbs'
$action = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument ('"' + $vbs + '"') -WorkingDirectory $Root
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 10)
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -StartWhenAvailable `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings `
    -Principal $principal -Description 'GROKVERSE GPU job daemon (lab/tools/gpu_daemon.py; lab/runner/README.md)' -Force | Out-Null
Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo | Select-Object TaskName, NextRunTime, LastRunTime
