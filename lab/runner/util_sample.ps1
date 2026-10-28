# CPU and GPU utilization for the hourly GROKVERSE update: 4 samples 1 s apart, averaged; prints one JSON line.
# GPU % = busiest engine, summed over processes and capped at 100 (as Task Manager shows it). Locale-independent (CIM).
$cpu = @(); $gpu = @(); $engine = ''; $procs = 0
for ($k = 0; $k -lt 5; $k++) {
  $c = (Get-CimInstance Win32_PerfFormattedData_PerfOS_Processor -Filter "Name='_Total'").PercentProcessorTime
  $e = @(Get-CimInstance Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine)
  if ($k -gt 0) {                                   # the first formatted sample can be stale
    $cpu += [double]$c
    $top = $e | Group-Object { $_.Name -replace '^pid_\d+_', '' } |
      ForEach-Object { [pscustomobject]@{ Key = $_.Name; Util = [math]::Min(100.0, [double](@($_.Group | Where-Object { $_.UtilizationPercentage -le 100 }) | Measure-Object UtilizationPercentage -Sum).Sum) } } |
      Sort-Object Util -Descending | Select-Object -First 1
    if ($top) { $gpu += [double]$top.Util; $engine = ($top.Key -split 'engtype_')[-1] } else { $gpu += 0 }
    $procs = @($e | Where-Object { $_.UtilizationPercentage -gt 0 } | ForEach-Object { ($_.Name -split '_')[1] } | Sort-Object -Unique).Count
  }
  Start-Sleep -Milliseconds 1000
}
$vram = (Get-CimInstance Win32_PerfFormattedData_GPUPerformanceCounters_GPUAdapterMemory | Measure-Object DedicatedUsage -Maximum).Maximum
[pscustomobject]@{
  cpu_pct = [math]::Round(($cpu | Measure-Object -Average).Average)
  gpu_pct = [math]::Round(($gpu | Measure-Object -Average).Average)
  gpu_engine = $engine; gpu_procs = $procs; vram_gb = [math]::Round($vram / 1GB, 1)
} | ConvertTo-Json -Compress
