---
tags: [lab/betrieb, lab/runbook]
angelegt: 2026-09-30
---
# Runbook: Betriebsprobleme automatisch lösen

Zurück zu [[PROBLEME]] · [[LAB]] · Betrieb: `lab/runner/README.md`, Regel 21/22 in `lab/runner/SESSION_PREAMBLE.md`

**Auftrag des Nutzers (30.09.2026, ≈ 18:40):** „Wenn solche Probleme auftauchen, sollen sie automatisch analysiert, eine
Lösung aufgeschrieben und diese dann automatisch ohne Bestätigung genutzt werden.“ Diese Freigabe gilt für die Klassen
A1–A6 und für neue Lösungen innerhalb der Grenzen unten. Ausgeführt vom **stündlichen Gesundheitscheck** (Assistenten-
Sitzung des Nutzers). Es gilt nur die vom Nutzer freigegebene Fassung dieser Datei und des Werkzeugs
`lab/tools/hang_check.py`: Beider SHA-256 steht im Cron-Prompt; weicht einer ab, wird nichts nach dem Runbook ausgeführt,
nur gemeldet. Laborsitzungen ändern beide Dateien nicht (Regel 22). Geprüft von einem unabhängigen Architektur-Agenten
(30.09.: 5 Blocker, in der Nachprüfung 2 weitere, alle eingearbeitet) und einem Code-Prüfer für hang_check.py.

## Ablauf bei jedem Problem

1. **Erkennen:** stündlicher Check, Hinweis einer Laborsitzung (LIVE „Hinweis für den Assistenten“, JOURNAL oder
   Nachricht), Dienst-Status (`lab/queue/status.json`).
2. **Analysieren:** Symptom und Ursache mit Belegen (Befehl und Ausgabe), nicht raten. Angaben einer Laborsitzung nie
   ungeprüft übernehmen; Befehle immer selbst bilden.
3. **Aufschreiben:** Eintrag in `lab/PROBLEME.md` (P-NNN; Symptom, Ursache, Folge, Lösung, Status), bevor gehandelt wird.
4. **Anwenden:** Passt die Lösung zu A1–A6 oder erfüllt sie die Bedingungen für neue Lösungen → sofort ausführen, ohne
   Rückfrage. Sonst: als Vorschlag in PROBLEME.md stehen lassen und den Nutzer benachrichtigen.
5. **Prüfen und festhalten:** Wirkung messen; Ausgang in PROBLEME.md; jede automatische Maßnahme als eine Zeile in
   `lab/runner/logs/auto_actions.jsonl` (Zeit, Klasse, Belege, Befehl, Ergebnis). Schlägt eine Maßnahme fehl (z. B. Prozess
   nach dem Beenden noch da): nicht wiederholen, melden.
6. **Neue Klassen** nur als Vorschlag in PROBLEME.md; in diese Datei kommen sie erst nach Freigabe durch den Nutzer.

## Freigegebene Maßnahmen (ohne Rückfrage)

| Klasse | Auslöser (alle Bedingungen geprüft) | Maßnahme |
|---|---|---|
| **A1** Runner nach externem Ausfall | `lab/runner-state.json`: status `halted_error`/`idle_after_error`; Ursache laut letzter `session_*.out.json` vorübergehend und extern (Auto mode unavailable, no safety verdict, overloaded, 429, 5xx, Rate-Limit); A1 in den letzten 12 h noch nicht angewendet (auto_actions.jsonl) | `consecutive_failures=0`, `status=idle`, `next_start_utc=jetzt`, `pause_reason=null`, Notiz mit Zeit und Grund (Python, UTF-8, Zeilenenden beibehalten). Beim zweiten Mal in 12 h: nur melden |
| **A2** GPU-Dienst läuft nicht | Jobdateien in `lab/queue/inbox`, Heartbeat > 3 min alt, kein Prozess mit `gpu_daemon.py` in der Befehlszeile | `Start-ScheduledTask GROKVERSE-GPU-Daemon`, nach 1 min prüfen. Lebt ein Dienstprozess, aber der Heartbeat steht: nur melden (Beenden würde laufende Jobs töten) |
| **A3** Hängender Job des Dienstes | `python lab/tools/hang_check.py --kill` meldet `hung`: Heartbeat < 2 min, `quiet_min ≥ 15`, Job nicht schon vom Dienst beendet, Baum = Wächter und alle Nachfahren, in allen Messungen (3 über 60 s) CPU < 0,3 Kerne, Ein-/Ausgabe < 1 MB und keine GPU-Nutzung; Wächter und Starter vor dem Beenden erneut geprüft (PID, Startzeit, Befehlszeile) | Das Werkzeug beendet den Starter samt Kindern und schreibt auto_actions.jsonl. Danach prüfen: Speicher frei, Dienst startet weiter; Laborsitzung per Nachricht informieren (Ergebnisse auswerten, nicht neu einreihen). Urteil `protected` (Bestätigungsblock) oder `unknown`: nur melden |
| **A4** Laborsitzung will einen eigenen Lauf beenden und darf es nicht | Hinweis höchstens 2 h alt und noch offen; der Prozess ist ein `guarded_run.py`-Lauf der Sitzung (Elternkette bis `session_claude_pid` aus runner-state.json), nicht die Sitzung selbst, kein Dienst-Job eines Bestätigungsblocks; PID, Startzeit und Befehlszeile stimmen mit dem Hinweis überein; der Grund (z. B. hängt, weit über Zeitplan) ist an Log oder Messung selbst bestätigt | Befehl selbst bilden, Starter samt Kindern beenden, prüfen, auto_actions.jsonl, Ergebnis an die Sitzung; den Hinweis in PROBLEME.md als erledigt vermerken |
| **A5** Platte fast voll | Laufwerk C: < 25 GB frei | Nutzer benachrichtigen und die Laborsitzung bitten, nichts Neues einzureichen und keine Checkpoints mehr zu schreiben; nichts löschen (DRAIN taugt nicht als Pause: der Dienst löscht ihn selbst) |
| **A6** Betriebsproblem mit Lösungsvorschlag einer Laborsitzung | Der Vorschlag passt zu A1–A5 | Bedingungen selbst prüfen, dann anwenden wie dort; Ergebnis an die Sitzung |

## Neue Probleme ohne passende Klasse

Automatisch anwenden, wenn die Lösung **alle** Bedingungen erfüllt:
- sie stellt den Betrieb wieder her oder verhindert Leerlauf oder Datenverlust;
- sie ist umkehrbar und betrifft nur Steuerdateien (runner-state) oder das Starten der geplanten Aufgaben;
- sie beendet keine Prozesse (dafür gibt es nur A3/A4) und ändert keine Forschungsdaten und nichts Eingefrorenes;
- sie steht nicht auf der Liste „Nie automatisch“.

Code-Änderungen nur an `lab/tools/gpu_daemon.py` und `lab/tools/gpu_memory.py`: klein und gezielt, Ursache selbst
nachgewiesen (nie allein auf Vorschlag einer Laborsitzung), vorher Sicherungskopie in `lab/runner/backup/`, Selbsttest, der
das Problem nachstellt, unabhängige Prüfung durch einen Subagenten ohne Blocker, Aktivierung über DRAIN (kein laufender
Job geht verloren). Alle anderen Code-Änderungen → Vorschlag.

## Nie automatisch (Vorschlag aufschreiben und Nutzer benachrichtigen)

- Forschungsdaten, Ergebnisse, Checkpoints oder Logs löschen, verschieben oder überschreiben;
- eingefrorene Registrierungen, Manifeste, Splits, hash-gebundene Trainer und Lader oder laufende Bestätigungsblöcke ändern;
- `lab/STOP` anlegen oder entfernen (Notbremse des Nutzers);
- Prozesse beenden außerhalb von A3/A4 (Laborsitzung selbst, der GPU-Dienst, Programme des Nutzers, Systemprozesse);
- Code in `guarded_run.py` (STOP, Zeitfenster) oder `lab/runner/*.ps1` (Berechtigungen der Sitzungen) ändern;
- Windows-, Treiber-, Energie- oder Update-Einstellungen; Software installieren oder aktualisieren (auch pip in `.venv-gpu`);
- geplante Aufgaben umkonfigurieren (außer Start nach A2); Berechtigungen oder Einstellungen von Claude Code ändern;
- diese Datei ändern; `git commit`/`push`, Veröffentlichungen, Mails, alles, was Geld kostet oder nach außen geht.

## Schon im Code gelöst (keine Handlung nötig)

- Hänger mit Traceback → der GPU-Dienst beendet nach `crash_minutes` (P-002).
- Stille Hänger bei Jobs mit `stall_minutes`; Pflicht für vortrainierte HF-Modelle nach Regel 21 (P-021).
- Grafikspeicher überbucht → Speicherschutz (P-009, P-013).
- Leere oder halb geschriebene Jobdateien → Dienst liest erst nach 5 s Ruhe (P-017).
- Dienstausfälle der Sicherheitsprüfung beenden Sitzungen als `service_unavailable`, ohne zu zählen (P-001).
- Liegen gebliebenes DRAIN: eine neu gestartete Dienst-Instanz ohne laufende Jobs löscht es selbst.

## Offen (Vorschläge, noch nicht umgesetzt)

- Echte Pause `lab/queue/PAUSE` (vom Dienst nie gelöscht) und eine Bremse bei Fehlerserien (z. B. „No HIP GPUs“ → der Dienst
  verbucht sonst bis zu 10 Jobs pro Minute als fehlgeschlagen).
- Stille Hänger ohne `stall_minutes` direkt im Dienst erkennen (er hält die Prozess-Handles); dann entfiele A3 weitgehend.
