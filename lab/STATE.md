---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand

_Zuletzt aktualisiert: 2026-09-25, ~22:05 Berlin (Sitzung 3, vom Runner gestartet 19:49Z)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[JOURNAL]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]]

## Kurzlage

- **Repo:** lokales Git, `main` = Import-Snapshot, `lab/research` = Laborarbeit. Kein Remote, kein Push.
  In `lab/runner/SESSION_PREAMBLE.md` liegt eine uncommittete Änderung, die nicht aus einer
  Agentensitzung stammt. Sie wurde bewusst nicht committet, der Nutzer entscheidet.
- **Umgebung:** Windows 11, globales Python 3.12, torch 2.13.0, numpy 2.5.1. Die Studie lief mit
  torch 2.12.1. Bit-Gleichheit ist deshalb nicht zu erwarten, eigene Baselines sind nötig.
- **Studie (historisch, nicht umschreiben):** `RESULTS.md`. Die Interpretation liegt bei den Autoren.
- **Runner:** aktiviert (Aufgabe `GROKVERSE-Lab-Runner`, Tick alle 10 min). Sitzung 2 hat der Runner
  gestartet, der Sitzungsstart ist damit Ende-zu-Ende belegt. Auch die
  Klassifikation des Sitzungsendes ist **in Sitzung 3 bestätigt:** Das Ende von Sitzung 2 wurde als `completed`
  erkannt, der Abstand zwischen den Starts betrug 5 h 07 min.
- **Zeitfenster-Wächter:** `lab/tools/guarded_run.py`, weiterhin **ungetestet**, weil beide
  Sitzungen außerhalb des Fensters lagen.

## Letzter abgeschlossener Versuch

**EXP-009** (Frequenz-Lotterie, reine Auswertung): Das Init-Spektrum von W_E sagt die finalen
Top-5-Frequenzen mit voraus (r̄ = 0.386 gegenüber 0.5, p < 1e-5, seed-spezifisch). Bei der
Two-hot-MLP gilt das nur pro Neuron. → [[experiments/EXP-009-freq-commitment/SUMMARY|EXP-009]].
Davor: EXP-003/b/c (F6-Frühvorhersage, teilweise).

## Vorbereitet, noch nicht ausgeführt (Grund: außerhalb 00:00–13:00 Berlin)

1. **EXP-001 Frequenzverbot**, jetzt mit *Nachtrag b* (Codex-Review): Intervall-Zensur,
   Validierung, projizierter Gradient und Adam, Energiekontrolle `shrink_matched`. Code ungetestet.
2. **EXP-002** mit Auswertung `analyze.py` (ungetestet).
3. **EXP-003d**: 10 Transformer-Baselines, Seeds 10–19.
4. **EXP-010 Init-Tausch**: 10 Läufe `init_swap`, Seeds 10–19. Braucht die Baselines aus EXP-003d.

## Nächste konkrete Aktion (nur im Fenster 00:00–13:00 Berlin; nächster Start ≈ 02:49 Berlin)

1. `python lab/tools/guarded_run.py --check`
2. `python lab/tools/guarded_run.py -- python lab/experiments/EXP-001-freq-ban/test_freq_ban.py`.
   Dazu gehören die neuen Tests für init_swap, shrink und Zensur-Intervalle.
3. Studientests als Baseline: `python lab/tools/guarded_run.py -- python training/tests/run_all.py`
4. Funktionstest EXP-001 (README Schritt 2): s/Schritt notieren und das Abbruchkriterium anwenden.
   Zusätzlich ein Kurz-Smoke für `init_swap` (`--steps 300 --out-root …/raw_smoke`), der prüft,
   dass `events.init_swap` und `split_hash` gleich der Baseline sind.
5. **Prioritätsentscheidung (Sitzung 3):** Zuerst die EXP-003d-Baseline und EXP-010 `init_swap`
   im Wechsel pro Seed (10–19). Das ist die stärkste neue Spur: Sie repliziert EXP-009 an frischen
   Seeds und prüft sie kausal. Danach die 12 EXP-001-Läufe, dann EXP-002.
   Auswertung: `confirm_d.py`, `EXP-010-init-swap/analyze.py`.
6. Jede Sitzung hat nur 90 min. Pro Sitzung sind also etwa 3–4 Läufe à ≤ 20 min möglich.

## Wiederaufnahme nach Abbruch

- Läufe von EXP-001 und EXP-003d schreiben alle 500 Schritte `raw*/<run_id>/result.json` mit
  `status: running`. Ein abgebrochener Lauf wird mit `--force` **neu** gestartet, nicht
  fortgesetzt, weil der Adam-Zustand nicht gespeichert wird.
- `lab/runner/logs/guarded_runs.jsonl` protokolliert Starts und Verweigerungen.

## Blocker

- keine
