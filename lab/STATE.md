---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]], Abschnitt „STATE-Archiv“)

_Zuletzt aktualisiert: 2026-09-26, 21:27 Berlin (Sitzung 14, läuft bis 00:19). Nächster Runner-Start laut runner-state.json: 00:54 Berlin._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] · [[BACKLOG]] · [[reviews/ASTRA_2026-09-26|Astra-Review]] · [[LESART-nacht-2026-09-27]]

## Verbindlich jetzt: Regel 18 (Astra-Review umsetzen), Nacht 26./27.09.

- **Keine Läufe (Training oder Tests) vor 03:00 Berlin** (Wächter: `WINDOW_START_OVERRIDES`). Davor nur Code/Doku.
- Reihenfolge 18a (Code, vor 03:00): Punkt 3 ✅ ungetestet · Punkt 10 ✅ ungetestet · Punkt 16 ✅ für alle Nachtauswertungen (EXP-043–050, ungetestet) · Punkt 11 ✅ ungetestet (GPU und `--cpu`; offen: EXP-034-Port) · Punkt 17 ✅ (diese Datei) · Punkt 5 ✅ (neue Versuche mit `SeedSequence`, Vermerk in FINDINGS) · 18c ✅ (FINDINGS = Programm A/B/C,
  P1–P3, Bestätigungsblock Seeds 1000–1099, Nullkalibrierung). Zweitprüfung der gemeinsamen Technik erledigt (JOURNAL Zyklus 14).
- **Sitzung ab 00:59 bis 03:00:** nichts Pflichtiges offen. Optional: P3-Entwurf schärfen (ELR als drittes Konkurrenzmodell), Volltext arXiv 2507.20057 lesen. Nichts starten, was trainiert oder testet.
- Stand je Punkt: Tabelle „Umsetzung“ am Ende von [[reviews/ASTRA_2026-09-26]].

## Wiederaufnahme ab 03:00 (18b), genau in dieser Reihenfolge

1. `python lab/tools/guarded_run.py --check` → `allowed: true`. Keine andere Queue aktiv (`ps -ef | grep -E "night_program|queue|guarded_run" | grep -v grep`).
2. Wächter-Abnahme: `python lab/tools/guarded_run.py -- python -c "import time; time.sleep(60)"` im Hintergrund, währenddessen
   `lab/STOP` anlegen → Exit 3 und Kind beendet? **STOP sofort wieder löschen**, im JOURNAL vermerken. Scheitert es: Blocker in LIVE.
3. Tests: `python lab/tools/guarded_run.py -- python lab/tools/result_loader.py` (Selbsttest) und
   `python lab/tools/guarded_run.py --min-minutes 5 -- python lab/tests/test_freq_ban_fingerprint.py` (Fingerprint, Legacy-Prüfung,
   Sperre, atomare Arrays, Artefaktprüfung; kleine CPU-Läufe im Temp-Ordner) und
   `python lab/tools/guarded_run.py -- python lab/tests/test_night_program.py` (Ablaufsteuerung, simulierte Jobs). Scheitert etwas: beheben, bevor Queues starten.
4. GPU: `python lab/tools/night_program.py > lab/runner/logs/night.log 2>&1` im Hintergrund (Plan: `--dry-run`). Beginnt mit GPU-001
   (Regression → Gleichwertigkeit → Durchsatz); ohne PASS keine GPU-Läufe. Danach EXP-043 → 046 → 047 (+ EXP-051, Ablation an den EXP-047-Modellen) → 048 → 049 → 044 → 045.
   Wiederaufnahme = derselbe Befehl (Fertiges wird per Fingerprint übersprungen). Status: `lab/runner/logs/night_*/night_status.json`.
5. CPU **erst nach GPU-001** (sonst verfälscht CPU-Last die J-Messung): `python lab/tools/night_program.py --cpu > lab/runner/logs/night_cpu.log 2>&1` (**EXP-014** → 035 → 038 → 041 → 036 →
   039 → 040 → 042). Nicht portiert, gesichtet ([[BACKLOG]] „Sichtung nach Regel 18c“): 034 nach P3-Design; 018/022/023/010 zurückgestellt.
6. Beobachten (Regel 14). GPU-001-Verdikte ins JOURNAL (Gleichwertigkeit, s/Schritt, J). Punkt 9: GPU bleibt experimentell.
7. Auswerten: `python lab/tools/night_report.py`; **vor jeder Deutung** [[LESART-nacht-2026-09-27]] lesen.
8. **EXP-052** (eingefrorene Vorhersage, Sitzung 14): Selbsttest `guarded_run.py -- python lab/experiments/EXP-052-oos-mask-prediction/exp052.py --selftest`
   (ab 03:00, vor den Läufen); Auswertung von Hand, sobald die R-Arme von EXP-043, EXP-046 und EXP-048 („random“) erfolgreich sind (Holm fest über vier Fälle; ein fehlender Fall zählt p = 1): `guarded_run.py -- python .../exp052.py`.

## Aktive Queue / laufende Jobs

- Keine (Stand 21:02). Vorbereitet, ungetestet: GPU-001, EXP-043–049 (in `night_program.py`), EXP-050 (optional:
  `--experiments GPU-001,EXP-050`), CPU: `night_program.py --cpu`.

## Drei Prioritäten (Regel 18c: Programm A/B/C)

1. **A – Split-Steuerung verallgemeinern und replizieren:** EXP-043 (Modulus), 046 (D₅₉), 048 (nicht-modular), 049 (Breite),
   045 (MLP); Mechanismus-Kontrolle EXP-047 (Häufigkeiten). Funktionale Wirkung (P2): EXP-051 (Pilot, nach EXP-047).
2. **B – Persistenz nach Datenwechsel:** EXP-044 (bedingt auf EXP-043), CPU EXP-035–042 (`night_program.py --cpu`); P3-Entwurf im [[BACKLOG]] mit Überlappungskonstruktion EXP-053 (Entwurf) und ELR-Arm.
3. **C – mechanistische Vorhersage an unberührten Fällen:** EXP-052 (eingefroren, Sitzung 14; läuft ohne eigene Läufe mit), EXP-050 (M0c gegen M0, Kontrolle quadlm), Theorie erster Ordnung
   ([[BEFUND-split-mechanismus]] Herleitung; EXP-047 Nachtrag a).

## Blocker / Hinweise

- **Codex ohne Guthaben** („out of credits“, 20:04): Zweitprüfung durch Claude-Subagenten (frischer Kontext, nur lesend).
- Uncommittete Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `tick.ps1`, `runner/README.md`, `SESSION_PREAMBLE.md`,
  `runner-state.json`, `parallel_queue.py`) **nicht committen** (der Astra-Review liegt seit s13 mit der Umsetzungstabelle im Git); nur gezielt `git add <pfad>`, nie `commit -a`.
- Zeitstempel nur aus `guarded_run.py --check` (`now_berlin`); `--check` liefert jetzt Exit 3, wenn nicht erlaubt.
- Shell-Skripte mit LF; Heredocs mit Backticks nur mit `<<'EOF'`; lange Patches als Datei statt Heredoc.
- `Path.with_suffix` nicht für Namen mit „eps2.0“ benutzen.
- Für den Nutzer (nicht von mir zu ändern): `guarded_run.py` bindet `.venv-gpu`-Prozesse evtl. zu spät ans Job-Objekt (venv-Starter startet
  den echten Interpreter als Kind); `parallel_queue.py` ist unversioniert, `night_program.py` hängt davon ab.

## Letzte abgeschlossene Versuche (Details [[LAB]], [[FINDINGS]])

- Letzte Urteile stammen aus Sitzung 9/10 (EXP-020, EXP-028, EXP-037); seither nur vorbereitet. Kernaussagen K1–K6 in [[FINDINGS]].
