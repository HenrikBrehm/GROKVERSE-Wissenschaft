---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]], Abschnitt „STATE-Archiv“)

_Zuletzt aktualisiert: 2026-09-26, 20:44 Berlin (Sitzung 13). Nächster Runner-Start laut runner-state.json: 00:59 Berlin._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] · [[BACKLOG]] · [[reviews/ASTRA_2026-09-26|Astra-Review]] · [[LESART-nacht-2026-09-27]]

## Verbindlich jetzt: Regel 18 (Astra-Review umsetzen), Nacht 26./27.09.

- **Keine Läufe (Training oder Tests) vor 03:00 Berlin** (Wächter: `WINDOW_START_OVERRIDES`). Davor nur Code/Doku.
- Reihenfolge 18a (Code, vor 03:00): Punkt 3 ✅ ungetestet · Punkt 10 ✅ ungetestet · Punkt 16 ✅ für alle Nachtauswertungen (EXP-043–050, ungetestet) · Punkt 11 GPU ✅ ungetestet (`night_program.py`;
  **offen: CPU-Queue `queue_s10.sh`**) · Punkt 17 ✅ (diese Datei) · Punkt 5 **offen** (neue Versuche nutzen `SeedSequence`;
  FINDINGS-Vermerk „EXP-016 stark, Seed-Abhängigkeit eingeschränkt“ fehlt). Dazu 18c: FINDINGS zum Programm A/B/C umbauen.
- Stand je Punkt: Tabelle „Umsetzung“ am Ende von [[reviews/ASTRA_2026-09-26]].

## Wiederaufnahme ab 03:00 (18b), genau in dieser Reihenfolge

1. `python lab/tools/guarded_run.py --check` → `allowed: true`. Keine andere Queue aktiv (`ps -ef | grep -E "night_program|queue|guarded_run" | grep -v grep`).
2. Wächter-Abnahme: `python lab/tools/guarded_run.py -- python -c "import time; time.sleep(60)"` im Hintergrund, währenddessen
   `lab/STOP` anlegen → Exit 3 und Kind beendet? **STOP sofort wieder löschen**, im JOURNAL vermerken. Scheitert es: Blocker in LIVE.
3. Tests: `python lab/tools/guarded_run.py -- python lab/tools/result_loader.py` (Selbsttest) und
   `python lab/tools/guarded_run.py --min-minutes 5 -- python lab/tests/test_freq_ban_fingerprint.py` (Fingerprint, Legacy-Prüfung,
   Sperre, atomare Arrays, Artefaktprüfung; kleine CPU-Läufe im Temp-Ordner). Scheitert etwas: beheben, bevor Queues starten.
4. GPU: `python lab/tools/night_program.py > lab/runner/logs/night.log 2>&1` im Hintergrund (Plan: `--dry-run`). Beginnt mit GPU-001
   (Regression → Gleichwertigkeit → Durchsatz); ohne PASS keine GPU-Läufe. Danach EXP-043 → 046 → 047 → 048 → 049 → 044 → 045.
   Wiederaufnahme = derselbe Befehl (Fertiges wird per Fingerprint übersprungen). Status: `lab/runner/logs/night_*/night_status.json`.
5. CPU parallel: `sh lab/experiments/queue_s10.sh > lab/runner/logs/queue_s10.log 2>&1` (bis zur Umstellung auf parallel_queue).
6. Beobachten (Regel 14). GPU-001-Verdikte ins JOURNAL (Gleichwertigkeit, s/Schritt, J). Punkt 9: GPU bleibt experimentell.
7. Auswerten: `python lab/tools/night_report.py`; **vor jeder Deutung** [[LESART-nacht-2026-09-27]] lesen.

## Aktive Queue / laufende Jobs

- Keine (Stand 20:44). Vorbereitet, ungetestet: GPU-001, EXP-043–049 (in `night_program.py`), EXP-050 (optional:
  `--experiments GPU-001,EXP-050`), CPU: `queue_s10.sh` (EXP-035 → 038 → 041 → 036 → 039 → 040 → 034 → 042 → queue_s5).

## Drei Prioritäten (Regel 18c: Programm A/B/C)

1. **A – Split-Steuerung verallgemeinern und replizieren:** EXP-043 (Modulus), 046 (D₅₉), 048 (nicht-modular), 049 (Breite),
   045 (MLP); Mechanismus-Kontrolle EXP-047 (Häufigkeiten). Funktionale Wirkung (Ablation) fehlt noch → planen.
2. **B – Persistenz nach Datenwechsel:** EXP-044 (bedingt auf EXP-043), CPU-Versuche EXP-035–042 (laufen in queue_s10).
3. **C – mechanistische Vorhersage an unberührten Fällen:** EXP-050 (M0c gegen M0, Kontrolle quadlm), Theorie erster Ordnung
   ([[BEFUND-split-mechanismus]] Herleitung; EXP-047 Nachtrag a).

## Blocker / Hinweise

- **Codex ohne Guthaben** („out of credits“, 20:04): Zweitprüfung durch Claude-Subagenten (frischer Kontext, nur lesend).
- Uncommittete Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `tick.ps1`, `runner/README.md`, `SESSION_PREAMBLE.md`,
  `runner-state.json`, `parallel_queue.py`) **nicht committen** (der Astra-Review liegt seit s13 mit der Umsetzungstabelle im Git); nur gezielt `git add <pfad>`, nie `commit -a`.
- Zeitstempel nur aus `guarded_run.py --check` (`now_berlin`); `--check` liefert jetzt Exit 3, wenn nicht erlaubt.
- Shell-Skripte mit LF; Heredocs mit Backticks nur mit `<<'EOF'`; lange Patches als Datei statt Heredoc.
- `Path.with_suffix` nicht für Namen mit „eps2.0“ benutzen.

## Letzte abgeschlossene Versuche (Details [[LAB]], [[FINDINGS]])

- Letzte Urteile stammen aus Sitzung 9/10 (EXP-020, EXP-028, EXP-037); seither nur vorbereitet. Kernaussagen K1–K6 in [[FINDINGS]].
