' Starts the GPU job daemon (lab/tools/gpu_daemon.py) without a visible console window.
' Called every 10 minutes by the scheduled task "GROKVERSE-GPU-Daemon" (MultipleInstances IgnoreNew).
' The daemon exits at once if the inbox is empty (after its idle time), so idle triggers cost almost nothing.
' Waits for the daemon, so the task instance lives exactly as long as the daemon.
Dim fso, dir, root, sh
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
root = fso.GetParentFolderName(fso.GetParentFolderName(dir))
Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = root
sh.Run """C:\Users\henri\AppData\Local\Programs\Python\Python312\python.exe"" """ & root & "\lab\tools\gpu_daemon.py"" --idle-exit-min 5", 0, True
