---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand (höchstens ~80 Zeilen; Historie im [[JOURNAL]], Abschnitt „STATE-Archiv“)

_Zuletzt aktualisiert: 2026-09-27, 00:31 Berlin (Sitzung 17, läuft bis 03:19; macht um 03:00 die Schritte 1–3, das Nachtprogramm startet die Folgesitzung). Nächste Sitzung: direkt nach dem Ende (nächster Tick)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[FINDINGS]] · [[BACKLOG]] · [[reviews/ASTRA_2026-09-26|Astra-Review]] · [[LESART-nacht-2026-09-27]]

## Verbindlich jetzt: Regel 18 (Astra-Review umsetzen), Nacht 26./27.09.

- **Keine Läufe (Training oder Tests) vor 03:00 Berlin** (Wächter: `WINDOW_START_OVERRIDES`). Davor nur Code/Doku/Rechnung auf Dateien.
- 18a vollständig (Punkte 3, 10, 16, 11, 17, 5; 18c Programm A/B/C), alles **ungetestet** bis 03:00. Offen: EXP-034-Port (nach P3-Design).
- **Nächste Sitzung ab 03:14 (Sitzung 16 hat den Kreuzblock ergänzt, sonst nichts offen):** bis 03:00 nichts Pflichtiges offen (Sitzung 15: N30-Fenstermodell, EXP-054 und Lesarten für EXP-041/042 vor den Läufen eingefroren). Ab 03:00 Schritte unten.
- Stand je Punkt: Tabelle „Umsetzung“ am Ende von [[reviews/ASTRA_2026-09-26]].

## Wiederaufnahme ab 03:00 (18b), genau in dieser Reihenfolge

1. `python lab/tools/guarded_run.py --check` → `allowed: true`. Keine andere Queue aktiv (`ps -ef | grep -E "night_program|queue|guarded_run" | grep -v grep`).
2. Wächter-Abnahme **(Sitzung 18: als Skript)**: `powershell -ExecutionPolicy Bypass -File lab/tools/accept_guard.ps1` (≈ 1 min; Proben A STOP, B/C Wächter hart beendet mit System- bzw. venv-Python; Ergebnis `lab/runner/logs/accept_guard.json`; löscht STOP selbst). Von Hand wie bisher: `python lab/tools/guarded_run.py -- python -c "import time; time.sleep(60)"` im Hintergrund, währenddessen
   `lab/STOP` anlegen → Exit 3 und Kind beendet? **STOP sofort wieder löschen**, im JOURNAL vermerken. Scheitert es: Blocker in LIVE.
3. Tests, je `python lab/tools/guarded_run.py [--min-minutes 5] -- python <datei> [arg]`: `lab/experiments/EXP-001-freq-ban/test_freq_ban.py` (Sitzung 18 ergänzt); `lab/tools/result_loader.py`;
   `lab/tests/test_freq_ban_fingerprint.py` (--min-minutes 5; kleine CPU-Läufe im Temp-Ordner); `lab/tests/test_night_program.py`;
   **neu (Sitzung 14):** `lab/experiments/EXP-052-oos-mask-prediction/exp052.py --selftest`, `lab/tools/pilot_power.py --selftest`,
   `lab/tools/confirm_splits.py --selftest`, `lab/tools/confirm_p1.py --selftest`. Scheitert etwas: beheben, bevor Queues starten
   (die vier neuen blockieren die Nachtqueues nicht, nur ihre eigene spätere Auswertung).
4. GPU: `python lab/tools/night_program.py > lab/runner/logs/night.log 2>&1` im Hintergrund (Plan: `--dry-run`). Beginnt mit GPU-001
   (**Sitzung 18: Stufe 0 `components`, Astra 9** → Regression → Gleichwertigkeit → Durchsatz); ohne PASS keine GPU-Läufe. Danach EXP-043 → 046 → 047 (+ EXP-051) → 048 → 049 → 044 → 045.
   Wiederaufnahme = derselbe Befehl (Fertiges wird per Fingerprint übersprungen). Status: `lab/runner/logs/night_*/night_status.json`.
   Ist das GPU-Programm vor ≈ 11:00 fertig (GPU-001 bestanden): EXP-050 nachschieben (`--experiments GPU-001,EXP-050`, Paket C, 60 Läufe).
5. CPU **erst nach GPU-001**: `python lab/tools/night_program.py --cpu > lab/runner/logs/night_cpu.log 2>&1` (EXP-014 → 035 → 038 → 041 → 036 →
   039 → 040 → 042). Nicht portiert: 034 (nach P3-Design); 018/022/023/010 zurückgestellt ([[BACKLOG]] „Sichtung nach Regel 18c“).
   **Wenn GPU-001 scheitert:** kein GPU-Lauf; sofort `--cpu --cpu-workers 3` (Zahl **explizit** angeben: ohne Throughput-PASS nimmt der Code sonst 1 Worker, Sitzung 17). Paket A danach auf der CPU (Sitzung 15, geprüft, ungetestet):
   `python lab/tools/night_program.py --paket-a-cpu --experiments EXP-043,... [--cpu-workers N]` (≈ 300 Läufe, mehrere Fenster;
   neben `--cpu` Threadsumme ≤ 12). Auswertungen von Hand dann mit `LAB_PAKET_A_DEVICE=cpu`.
6. Beobachten (Regel 14). GPU-001-Verdikte ins JOURNAL (Gleichwertigkeit, s/Schritt, J). Punkt 9: GPU bleibt experimentell.
7. Auswerten: `python lab/tools/night_report.py`; **vor jeder Deutung** [[LESART-nacht-2026-09-27]] lesen.
8. **Eingefrorene Vorhersagen (Sitzung 14), nach den jeweiligen Läufen, alle über den Wächter:**
   - EXP-052 (Paket C): `lab/experiments/EXP-052-oos-mask-prediction/exp052.py`, sobald die R-Arme von EXP-043, 046, 048 fertig sind (Holm fest über vier).
   - EXP-039 (CPU): `lab/experiments/EXP-039-lr-clock/eval_pi.py` (π gegen drei Uhren, `predictions_pi.json`, nur beschreibend).
   - EXP-044 (GPU): `lab/experiments/EXP-044-generalize-lockin/pi_persistence.py` (π gegen EXP-020, Lesarten (i)/(ii) in der README).
   - **Neu (Sitzung 15):** EXP-054 nach EXP-036: `lab/experiments/EXP-054-window-oos/n30_window.py` (erst `--selftest`); EXP-042 nach dessen
     Hauptauswertung: `lab/experiments/EXP-042-bias-strength/pi_window.py` (erst `--selftest`, EXP-020-Regression). Beide nur beschreibend.
9. **Vor dem Einfrieren von P1:** `lab/tools/pilot_power.py` (Δ_pow-Pilotstreuung, n für Power 80 %; vorher prüfen, dass die summary.json von
   EXP-048/049 aus dieser Nacht stammt). Bestätigungsblock dann mit `confirm_splits.py --manifest …` und `confirm_p1.py --jobs/--analyze …`
   (nur mit committetem Manifest; Seeds 1000–1099). P3 vorher schärfen: primär Wechsel bei t = 25 (Decke bei 150), Maß π, Überlappung nach EXP-053.
   Gekreuzter Split×Init-Block (Astra 5) ist entschieden (Sitzung 16): ins Manifest `"cross": {"task": "add", "p": 113, "seeds": [erste 5], "inits_per_seed": 2}`
   (20 Zusatzläufe, sekundär; Lesart in `confirm_p1.py`). EXP-014 bleibt Exploration.

## Aktive Queue / laufende Jobs

- Keine (Stand 22:05, Sitzung 14). Vorbereitet, ungetestet: GPU-001, EXP-043–049 (in `night_program.py`), EXP-050 (optional), CPU: `night_program.py --cpu`.

## Drei Prioritäten (Regel 18c: Programm A/B/C)

1. **A – Split-Steuerung verallgemeinern und replizieren:** EXP-043 (Modulus), 046 (D₅₉), 048 (nicht-modular), 049 (Breite), 045 (MLP);
   Mechanismus-Kontrolle EXP-047 (Häufigkeiten); funktional (P2) EXP-051. Idee N29 (Steuerung über Loss-Gewichte) erst nach EXP-047.
2. **B – Persistenz nach Datenwechsel:** EXP-044, CPU EXP-035–042; P3-Entwurf im [[BACKLOG]] (π als Maß, t = 25 primär, Überlappung EXP-053, ELR-Arm).
3. **C – mechanistische Vorhersage an unberührten Fällen:** EXP-052 (eingefroren), EXP-050, Theorie erster Ordnung ([[BEFUND-split-mechanismus]]).

## Blocker / Hinweise

- **Codex ohne Guthaben** („out of credits“, 20:04): Zweitprüfung durch Claude-Subagenten (frischer Kontext, nur lesend).
- Uncommittete Nutzeränderungen (`guarded_run.py`, `install_task.ps1`, `tick.ps1`, `runner/README.md`, `SESSION_PREAMBLE.md`,
  `runner-state.json`, `parallel_queue.py`) **nicht committen**; nur gezielt `git add <pfad>`, nie `commit -a`.
- Zeitstempel nur aus `guarded_run.py --check` (`now_berlin`); `--check` liefert Exit 3, wenn nicht erlaubt.
- Shell-Skripte mit LF; Heredocs mit Backticks nur mit `<<'EOF'`; lange Patches als Datei (Python-Skript im Temp-Ordner) statt Heredoc.
- `Path.with_suffix` nicht für Namen mit „eps2.0“ benutzen.
- Neue `freq_ban.py`-Argumente nur **bei Abweichung vom Standard** in den Fingerprint aufnehmen, sonst brechen alle Wiederaufnahmen ab (Sitzung 16, [[BACKLOG]] ELR-Arm).
- **Sitzungsgrenze (Sitzung 17):** Jeder Job hat als harte Grenze die Sitzungsdeadline. `night_program.py` wertet einen dabei abgebrochenen Job (Exit 124)
  jetzt wie eine Ablehnung (Programm stoppt mit Exit 3, Status „refused by guard“) statt als Fehlschlag; GPU-001 überspringt bestandene Stufen.
  Also: ein „refused“/Exit 3 am Sitzungsende ist **kein** Fehler, einfach denselben Befehl neu starten. Nachtprogramm früh in einer frischen Sitzung starten.
  Die STOP-Probe ist während einer Sitzung sicher (Aufgabe `IgnoreNew`, kein Tick), STOP aber vor Sitzungsende löschen.
- Für den Nutzer (nicht von mir zu ändern): `guarded_run.py` bindet `.venv-gpu`-Prozesse evtl. zu spät ans Job-Objekt;
  `parallel_queue.py` ist unversioniert, `night_program.py` hängt davon ab.

## Letzte abgeschlossene Versuche (Details [[LAB]], [[FINDINGS]])

- Letzte Urteile aus Sitzung 9/10 (EXP-020, EXP-028, EXP-037); seither nur vorbereitet. Kernaussagen K1–K6 in [[FINDINGS]].
- Sitzung 14 (post hoc, gespeicherte Läufe): kontinuierliche Persistenz π an EXP-020 (0.15/0.38/0.72/≈1 bei t = 10/25/50/150); nach
  Gegenprüfung korrigiert: Warmup verzögert, aber weder Schritt- noch Λ-Uhr passen ([[BEFUND-festlegung]]).
