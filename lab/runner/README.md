# Äußerer Runner — Status: **aktiviert** (2026-09-25 16:39 Berlin, vom Nutzer selbst)

Der Nutzer hat die Aufgabe `GROKVERSE-Lab-Runner` selbst registriert, nachdem der Klassifikator sie dem Agenten zweimal verweigert hatte. Geprüft sind der Tick alle 10 min (unbegrenzt), IgnoreNew und die Anmeldeart Interactive. Die Trockenprüfung um 16:38 hat sich korrekt still beendet, weil noch keine Sitzung fällig war. **Ende-zu-Ende noch unbestätigt**: Die erste echte Runner-Sitzung ist fällig ab 16:04Z (18:04 Berlin).

## Ursprünglicher Stand (Sitzung 1)

Stand 2026-09-25 (Sitzung 1). Die Dateien sind geschrieben und statisch geparst (PowerShell-Parser:
keine Fehler). **Nichts davon wurde ausgeführt.** Das Aktivieren (Aufgabe registrieren, Probelauf)
hat der Auto-Mode-Klassifikator von Claude Code in Sitzung 1 als „Create Unsafe Agents“ blockiert.
Der Agent hat das nicht umgangen. Ob der Runner aktiviert wird, entscheidest du.

## Was es ist

| Datei | Zweck |
|---|---|
| `PROMPT.md` | der Arbeitsauftrag, wörtlich gespeichert |
| `SESSION_PREAMBLE.md` | Betriebsregeln, die jeder Runner-Sitzung vorangestellt werden (zuerst `lab/STATE.md` lesen, Runs nur über `guarded_run.py` …) |
| `tick.ps1` | ein „Tick“: prüft STOP, Sperre und Fälligkeit; startet höchstens **eine** `claude -p`-Sitzung; wertet Ende, Usage-Limit und Fehler aus; schreibt `lab/runner-state.json` |
| `launch_hidden.vbs` | startet `tick.ps1` ohne sichtbares Konsolenfenster |
| `install_task.ps1` / `uninstall_task.ps1` | registriert bzw. entfernt die Benutzer-Aufgabe `GROKVERSE-Lab-Runner` (Tick alle 10 min) |
| `logs/` (gitignored) | `tick.log`, Prompt, stdout/stderr jeder Sitzung, `guarded_runs.jsonl` |

**Warteschleife ohne Modellanfragen:** Ein Tick liest nur `runner-state.json` und beendet sich,
solange `now < next_start_utc`. Nur ein fälliger Tick ruft `claude` auf.

**Takt (Dauerbetrieb seit 2026-09-25, Wunsch des Nutzers):** Eine Sitzung dauert höchstens 180 min
(Deadline, harter Timeout 200 min). Endet sie normal, startet der nächste Tick sofort die nächste
Sitzung. Der Agent arbeitet also durchgehend, bis das Usage-Limit erreicht ist, und nach dem Reset
geht es automatisch weiter (siehe unten). Nach einem Fehler oder Timeout wird nach 30 min wiederholt,
nach 3 Fehlern in Folge wird angehalten. Verpasste Termine (Rechner aus) werden nicht nachgeholt:
Der erste fällige Tick startet genau eine Sitzung.

**Keine Parallelität:** Sperrdatei `session.lock` (mit PID, atomar per `CreateNew`; verwaiste Sperren
werden erkannt) und zusätzlich `MultipleInstances IgnoreNew` in der Aufgabe.

**Usage-Limit:** Nur eine *fehlgeschlagene* Sitzung wird auf Limit-Meldungen untersucht. Ist eine
Reset-Zeit lesbar (`…limit reached|<epoch>` oder `resets <Zeit> (<IANA-Zone>)`, optional mit Datum),
gilt `next_start = Reset + 60 s` (nur wenn der Reset plausibel in der Zukunft liegt, höchstens 8 Tage). Sonst gilt `Meldung + 5 h`, und zwar nur als Wiederholungszeit. Kurze API-Ratenlimits/Überlastung (ohne Reset-Zeit) werden nach 15 min wiederholt. Gesucht wird nur im Ergebnistext und am Ende von stderr.
Das Parse-Verfahren steht in `reset_parse`. Das Format der Limit-Meldung der CLI ist **nicht
verifiziert**; ein unbekanntes Format fällt auf +5 h zurück.

**Wiederanlauf:** Stirbt der Runner (Task-Limit 4 h, Neustart), erkennt der nächste Tick das an Sperre und gespeicherter Claude-PID: Läuft Claude noch, wird keine zweite Sitzung gestartet; sonst `outcome=interrupted` und sofortiger Neustart.

**Fehler:** Wenn eine Sitzung nach 200 Minuten noch läuft, wird der ganze Prozessbaum beendet
(`timeout_killed`). Unbekannte Fehler zählen `consecutive_failures` hoch; nach 3 Fehlern in Folge
wird `status = halted_error` gesetzt und nichts mehr gestartet, bis ein Mensch es prüft. Die
Wiederholung kommt frühestens nach 5 Stunden, es gibt also keine schnelle Schleife.

**STOP:** Existiert `lab/STOP`, setzt der Tick `status = stopped`, deaktiviert seine eigene Aufgabe
und startet nichts mehr. Die STOP-Datei entfernt er nie selbst.

**Zeitfenster:** Der Runner darf Sitzungen jederzeit starten. Test- und Trainingsläufe erlaubt
innerhalb einer Sitzung nur `lab/tools/guarded_run.py`. Es erzwingt 00:00–13:00 Europe/Berlin, die
die Sitzungsdeadline (eine feste Jobgrenze gibt es seit 2026-09-25 nicht mehr, der Agent beobachtet seine Läufe selbst) (`LAB_SESSION_DEADLINE_UTC` = Start + 180 min) und
verweigert den Start, wenn die Uhrzeit nicht bestimmbar ist.

## Sicherheitsrelevante Entscheidung, die bei dir liegt

Jede Runner-Sitzung läuft mit `claude -p --permission-mode auto --permission-prompts none`, also
unbeaufsichtigt: Alles, was der Auto-Modus nicht selbst freigibt, wird verweigert, und es wird
nicht nachgefragt. Globale Einstellungen ändert das nicht. Die Sitzungen können aber ohne dich
Dateien im Projekt ändern und Befehle ausführen. Genau das hat der Klassifikator markiert.
Mögliche Alternativen, falls du den Auto-Modus nicht unbeaufsichtigt laufen lassen willst: in
`tick.ps1` `--permission-mode acceptEdits` plus eine enge `--allowedTools`-Liste verwenden, oder die
Sitzungen weiter von Hand starten (`claude` im Projekt öffnen und
„Setze die Laborarbeit laut lab/runner/PROMPT.md fort“).

Nicht steuerbar per CLI-Flag: ob dein Konto bei erreichtem Limit auf kostenpflichtige
Zusatznutzung umschaltet. Das ist eine Kontoeinstellung auf claude.ai. Bitte prüfe sie, falls
das unerwünscht ist.

## Aktivieren (von dir auszuführen)

```powershell
# im Projektroot, als dein normaler Benutzer (keine Admin-Rechte nötig)
powershell -NoProfile -ExecutionPolicy Bypass -File lab\runner\tick.ps1 -WhatIf   # Trockenprüfung, startet nichts
powershell -NoProfile -ExecutionPolicy Bypass -File lab\runner\install_task.ps1   # registriert den 10-min-Tick
```

Vorher in `lab/runner-state.json` `"status"` von `"prepared_not_activated"` auf `"idle"` setzen.
Der erste fällige Start ist `next_start_utc` (2026-09-25T16:04:31Z = 18:04 Berlin). Liegt dieser
Termin schon in der Vergangenheit, startet der erste Tick sofort eine Sitzung.

**Voraussetzungen:** Der Rechner ist eingeschaltet, du bist angemeldet (die Aufgabe läuft nur bei
angemeldetem Benutzer, ohne gespeichertes Passwort), und `claude` ist im PATH und angemeldet.

## Pausieren / Beenden

| Ziel | Befehl |
|---|---|
| Stopp mit Wirkung auf die Planung | `New-Item lab\STOP` (der nächste Tick deaktiviert die Aufgabe) |
| Pause ohne STOP | `Disable-ScheduledTask -TaskName GROKVERSE-Lab-Runner` · fortsetzen: `Enable-ScheduledTask …` |
| Entfernen | `powershell -File lab\runner\uninstall_task.ps1` |
| Status | `Get-Content lab\runner-state.json` · `Get-ScheduledTaskInfo -TaskName GROKVERSE-Lab-Runner` · `lab\runner\logs\tick.log` |

## GPU-Dienst (seit 2026-09-29)

Lange Läufe laufen unabhängig von den Claude-Sitzungen über `lab/tools/gpu_daemon.py`, gestartet von der Aufgabe
`GROKVERSE-GPU-Daemon` (alle 10 min, IgnoreNew, kein Zeitlimit; Installation `install_gpu_daemon_task.ps1`, Start
versteckt über `launch_daemon_hidden.vbs`). Sitzungen legen Jobdateien in `lab/queue/inbox/` ab; Status in
`lab/queue/status.json`, Logs in `lab/queue/logs/`, Erledigtes in `lab/queue/done/`. Jeder Job läuft über den Wächter
(STOP, Fenster, Job-Objekt), ohne Sitzungsdeadline, mit `job_minutes` als harter Grenze. Stirbt der Dienst, sterben seine
Jobs mit (Job-Objekt) und laufen beim Neustart erneut. Anlass: Sitzungsabsturz am 29.09. 08:24 (Auto-Mode-Ausfall),
bei dem die Jobs mitstarben. Solche Dienstausfälle wertet `tick.ps1` jetzt als `service_unavailable` (Neustart nach
15 min, zählt nicht als Fehler).

Jobdateien laufen in Namensreihenfolge (Zahl vorne = Priorität, auch für später eingereichte Dateien). Hänger-Erkennung
(seit 29.09., nachdem zwei EXP-105-Läufe nach einem Traceback 90 min lang mit 100 % CPU hingen und zwei GPU-Plätze
blockierten): Endet ein Job-Log in einem Python-Traceback und wächst `crash_minutes` lang (Standard 10) nicht mehr, beendet
der Dienst den Job (`failed:hung`); optional beendet `stall_minutes` (Standard aus) Jobs ohne jede neue Ausgabe
(`failed:stalled`). Jobs laufen mit `PYTHONUNBUFFERED=1`; jede Beendigung steht im Job-Log und in `guarded_runs.jsonl`.
Sanfter Neustart nach Code-Änderungen: `lab/queue/DRAIN` anlegen – der Dienst startet nichts Neues, lässt Laufendes
fertig werden, löscht DRAIN und beendet sich; die Aufgabe startet dann den neuen Code. `status.json` → `features` zeigt,
was die laufende Instanz kann (eine Instanz mit altem Code ignoriert DRAIN).

Speicherschutz (seit 29.09., `lab/tools/gpu_memory.py`; Anlass: 10 Sprachmodell-Läufe à 3,4 GB überbuchten die 20-GB-Karte,
Windows lagerte 15 GB in den RAM aus, alles lief 8× langsamer, RAM und Speicherzusage liefen voll, die Auslagerungsdatei
wuchs um ≈ 25 GB – `lab/PROBLEME.md` P-009): Jede Jobdatei meldet mit `gpu_gb` den Grafikspeicher eines Laufs an (Standard
3,5). Ein Job startet nur, wenn max(Messung, 2,5 GB Reserve + angemeldete Größen) + seine Größe ≤ `--gpu-budget-gb` (Standard
16) bleibt, nicht ausgelagert wird (geteilter Speicher ≤ 3 GB) und RAM (≥ 3 GB) und der Spielraum der Speicherzusage (≥ 8 GB, einschließlich möglichem Wachstum der Auslagerungsdatei) reichen; höchstens
ein Start alle 6 s. Unterbrochene Läufe starten nach einem Neustart zuerst; geänderte Kopfzeilen werden neu eingelesen.
`status.json` → `memory` (Messwerte) und `admission` (warum gerade nichts startet, seit wann).
Entfernen: `Unregister-ScheduledTask -TaskName GROKVERSE-GPU-Daemon -Confirm:$false`.
