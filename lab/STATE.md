---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand

_Zuletzt aktualisiert: 2026-09-26, ~02:57 Berlin (Sitzung 4, vom Runner gestartet 00:49Z, Deadline 03:49Z)._

> **LÄUFT (Sitzung 4, ab 03:28): `sh lab/experiments/queue_s4b.sh`** (Log `lab/runner/logs/queue_s4b.log`): Baselines 12–17,
> dann EXP-016 (Smoke, dann Arme F/G je Seed, 2000 Schritte), dann Baselines 18/19, EXP-014-Kreuzpaare, EXP-010-Tausch 11–19,
> EXP-013 am Ende. **Wiederaufnahme: `sh lab/experiments/queue_s4b.sh` erneut starten** (fertige Läufe werden übersprungen).
> Ältere Warteschlange (ersetzt, 03:28): `sh lab/experiments/queue_s4.sh` (Log `lab/runner/logs/queue_s4.log`): Baselines 11–19,
> dann EXP-014-Kreuzläufe, dann EXP-010-Tausch 11–19, am Ende EXP-013. **Wiederaufnahme: dasselbe Skript erneut starten.**
> Vorher (bis 03:12): `sh lab/experiments/EXP-010-init-swap/run_pairs.sh` im Hintergrund, Log
> `lab/runner/logs/pairs_s4.log`. Abwechselnd EXP-003d-Baseline (`raw_d`) und EXP-010 `init_swap`
> (`EXP-010-init-swap/raw`), Seeds 10→19, je Lauf nur bei ≥ 33 min Restzeit. **Wiederaufnahme:** dasselbe
> Skript erneut starten. Fertige Läufe überspringt `freq_ban.py`. Ein Lauf mit `status: running` war
> abgebrochen und muss mit `--force` neu (oder Verzeichnis löschen, nachdem es geprüft wurde).
> Geprüft in Sitzung 4: `test_freq_ban.py` 8/8, Studientests 24/24, Smoke 300 Schritte (Tausch korrekt,
> gleicher `split_hash`, `power_before` = Baseline-Spektrum bei 0), 0.127 s/Schritt, `guarded_run.py`
> funktioniert im Fenster.
> Danach wartet ein Hintergrund-Job auf `[pairs]` im Log und startet EXP-013 (`lockin.py`, Log `lockin_s4.log`).
> Neu in Sitzung 4: EXP-011 (Normtausch) und EXP-012 (Init-Gradient) vorab festgelegt; EXP-012 Phase 1 fertig
> (G0 gewählt); EXP-010/011 Nachtrag a nach Codex-Review; EXP-013 vorbereitet.
> **Plan (03:17):** Wenn die Baselines 11–19 fertig sind, `queue_s4.sh` zwischen zwei Läufen beenden und EXP-016
> starten (Smoke `--steps 50`, dann 10 Läufe), vor EXP-014 und den restlichen EXP-010-Tauschläufen.
> Neu: EXP-015 (Masken-Spektrum, Phase 1 r̄ 0.307) und EXP-016 (konstruierter Split) vorab festgelegt, Kandidat N3.
> **Offen nach der Sitzung:** restliche Paare (Seeds, die in `raw_d`/`raw` fehlen), dann `EXP-010-init-swap/analyze.py`,
> `EXP-012 predict.py --phase 2 --predictor G0` (≥ 8 Baselines), `confirm_d.py`, danach EXP-011 (10 Läufe).

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
