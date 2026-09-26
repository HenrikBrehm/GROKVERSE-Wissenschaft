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
gilt `next_start = Reset + 60 s`. Sonst gilt `Meldung + 5 h`, und zwar nur als Wiederholungszeit.
Das Parse-Verfahren steht in `reset_parse`. Das Format der Limit-Meldung der CLI ist **nicht
verifiziert**; ein unbekanntes Format fällt auf +5 h zurück.

**Fehler:** Wenn eine Sitzung nach 110 Minuten noch läuft, wird der ganze Prozessbaum beendet
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
