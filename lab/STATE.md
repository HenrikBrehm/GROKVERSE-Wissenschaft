# lab/STATE.md: aktueller Stand

_Zuletzt aktualisiert: 2026-09-25, ~16:55 Berlin (Sitzung 2, vom Runner gestartet 14:42Z)._

## Kurzlage

- **Repo:** lokales Git, `main` = Import-Snapshot, `lab/research` = Laborarbeit. Kein Remote, kein Push.
  In `lab/runner/SESSION_PREAMBLE.md` liegt eine uncommittete Änderung, die nicht aus einer
  Agentensitzung stammt. Sie wurde bewusst nicht committet, der Nutzer entscheidet.
- **Umgebung:** Windows 11, globales Python 3.12, torch 2.13.0, numpy 2.5.1. Die Studie lief mit
  torch 2.12.1. Bit-Gleichheit ist deshalb nicht zu erwarten, eigene Baselines sind nötig.
- **Studie (historisch, nicht umschreiben):** `RESULTS.md`. Die Interpretation liegt bei den Autoren.
- **Runner:** aktiviert (Aufgabe `GROKVERSE-Lab-Runner`, Tick alle 10 min). Sitzung 2 hat der Runner
  gestartet, der Sitzungsstart ist damit Ende-zu-Ende belegt. **Noch unbestätigt:** die
  Klassifikation des Sitzungsendes. Prüfen in `lab/runner/logs/tick.log` („session end: outcome=…“).
  Die Sitzung startete früher als der Plan von 16:04Z, vermutlich per manuellem Anstoß
  (JOURNAL Sitzung 2). Bitte prüfen, dass zwischen den Starts ≥ 5 h liegen.
- **Zeitfenster-Wächter:** `lab/tools/guarded_run.py`, weiterhin **ungetestet**, weil beide
  Sitzungen außerhalb des Fensters lagen.

## Letzter abgeschlossener Versuch

**EXP-003 / 003b / 003c** (Frühvorhersage, reine Auswertung gespeicherter Läufe):
F6 = Fourier-Konzentration des Embeddings. Ergebnis: „teilweise“ (003), „richtungsgleich, nicht
signifikant“ (003b), in der Exploration (003c) ein Fortschrittsmaß ohne feste Vorlaufzeit. Details:
`lab/experiments/EXP-003-early-prediction/SUMMARY.md`.

## Vorbereitet, noch nicht ausgeführt (Grund: außerhalb 00:00–13:00 Berlin)

1. **EXP-001 Frequenzverbot** (`lab/experiments/EXP-001-freq-ban/`), P1, Code ungetestet.
2. **EXP-002** (`lab/experiments/EXP-002-destined-ban/README.md`): 6 Läufe nach EXP-001, Auswerteskript fehlt noch.
3. **EXP-003d** (`lab/experiments/EXP-003-early-prediction/CONFIRM_d.md`): 10 Transformer-Baselines,
   Seeds 10–19, dann `confirm_d.py`. Auswerteskript ungetestet.

## Nächste konkrete Aktion (nur im Fenster 00:00–13:00 Berlin)

1. `python lab/tools/guarded_run.py --check`
2. `python lab/tools/guarded_run.py -- python lab/experiments/EXP-001-freq-ban/test_freq_ban.py`
3. Studientests als Baseline: `python lab/tools/guarded_run.py -- python training/tests/run_all.py`
4. EXP-001-Funktionstest (README Schritt 2), s/Schritt notieren und das Abbruchkriterium anwenden.
5. EXP-001-Hauptläufe, einer nach dem anderen, danach `analyze.py`.
6. EXP-002-Läufe (Befehle in dessen README), die Baselines kommen aus EXP-001. Danach das
   Auswerteskript nach dem Muster von EXP-001 `analyze.py` schreiben.
7. Bleibt Budget übrig: EXP-003d-Läufe (Befehl in `CONFIRM_d.md`), Seed für Seed. Jeder
   abgeschlossene Seed ist für sich gültig. Wenn alle 10 vorliegen: `python lab/experiments/EXP-003-early-prediction/confirm_d.py`.

## Wiederaufnahme nach Abbruch

- Läufe von EXP-001 und EXP-003d schreiben alle 500 Schritte `raw*/<run_id>/result.json` mit
  `status: running`. Ein abgebrochener Lauf wird mit `--force` **neu** gestartet, nicht
  fortgesetzt, weil der Adam-Zustand nicht gespeichert wird.
- `lab/runner/logs/guarded_runs.jsonl` protokolliert Starts und Verweigerungen.

## Blocker

- keine
