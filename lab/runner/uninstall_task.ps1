# Removes the scheduled task "GROKVERSE-Lab-Runner" (does not touch lab/ state or logs).
Unregister-ScheduledTask -TaskName 'GROKVERSE-Lab-Runner' -Confirm:$false
