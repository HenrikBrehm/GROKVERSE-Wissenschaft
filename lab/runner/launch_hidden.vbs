' Starts one runner tick without a visible console window (called by the scheduled task).
' Waits for the tick to finish so the task's "IgnoreNew" policy also prevents overlapping ticks.
Dim fso, dir, sh
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
Set sh = CreateObject("WScript.Shell")
sh.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File """ & dir & "\tick.ps1""", 0, True
