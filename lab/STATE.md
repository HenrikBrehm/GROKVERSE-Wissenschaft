---
tags: [lab/state]
---
# lab/STATE.md: aktueller Stand

_Zuletzt aktualisiert: 2026-09-26, ~05:10 Berlin (Sitzung 4, vom Runner gestartet 00:49Z, Deadline 03:49Z = 05:49 Berlin)._

Einstieg: [[LAB]] · Live: [[LIVE]] · [[JOURNAL]] · [[BACKLOG]] · [[NOVEL_DIRECTIONS]]

## Wiederaufnahme (zuerst lesen)

- **Warteschlange:** `sh lab/experiments/queue_s4b.sh` (Log `lab/runner/logs/queue_s4b.log`). Sie überspringt fertige
  Läufe (`freq_ban.py` endet dann mit „already completed“, das ist gewollt). Reihenfolge: Baselines 12–17 (fertig) →
  EXP-016 Smoke (fertig) → EXP-016 Arme F/G Seeds 10–19 (2000 Schritte, je ≈ 4.5 min) → Baselines 18/19 → EXP-014
  Kreuzpaare (10↔11, 12↔13, 14↔15, 16↔17, 18↔19) → EXP-010-Tausch 11–19 → EXP-013 (Lock-in).
  **Nächste Sitzung im Fenster: dasselbe Skript erneut starten.** Danach EXP-017 (RFM) und EXP-011 (Normtausch).
- **Abgebrochene Läufe** stehen mit `status: running` in `result.json`. Sie werden **nicht** übersprungen, sondern von
  `freq_ban.py` automatisch neu gestartet (nur `completed` wird übersprungen). Kein Resume des Adam-Zustands.
- Vor jedem Start: `python lab/tools/guarded_run.py --check`. Der Wächter ist seit Sitzung 4 im Fenster **getestet**.

## Kurzlage

- **Repo:** lokales Git, `main` = Import-Snapshot, `lab/research` = Laborarbeit. Kein Remote, kein Push.
  Uncommittete Änderungen an `lab/runner/*`, `lab/runner-state.json` und `lab/tools/guarded_run.py` stammen vom
  Nutzer (Regeln 13/14, keine feste Jobgrenze). Sie sind bewusst nicht committet; der Nutzer entscheidet.
- **Umgebung:** Windows 11, Python 3.12, torch 2.13.0, numpy 2.5.1 (Studie: torch 2.12.1). Die rekonstruierten Inits
  stimmen trotzdem bitgenau mit den gespeicherten Schritt-0-Checkpoints überein. 0.13 s/Schritt (Transformer, 4 Threads).
- **Studie (historisch, nicht umschreiben):** `RESULTS.md`. Interpretation bei den Autoren.
- **Runner:** aktiviert (Aufgabe `GROKVERSE-Lab-Runner`), Sitzungsstart und -ende-Klassifikation belegt.

## Stand der Versuche (Sitzung 4)

**Bestätigt an frischen Seeds 10–17 (vorab festgelegt):**
- [[experiments/EXP-015-mask-spectrum/README|EXP-015]]: Das **Masken-Spektrum M0 des Trainingssplits** (ohne Gewichte)
  sagt die Rangfolge der gelernten Frequenzen voraus: r̄ 0.277, fremde Masken 0.499, exaktes p 2.5e-5. Hält auch gegen
  die funktionalen Schlüsselfrequenzen der Studie (p 3.6e-6). **Nur Assoziation:** Split und Init desselben Seeds sind
  gleich geseedet. Post hoc auch in MLP-512/572 und Two-hot-MLP.
- [[experiments/EXP-012-init-gradient/README|EXP-012]]: Der erste Gradient an W_E sagt K besser voraus als das
  Init-Spektrum (0.254 vs. 0.369, p 0.031). EXP-009 an frischen Seeds repliziert (E0 p 0.0015).

**Läuft:** [[experiments/EXP-016-engineered-split/README|EXP-016]] (kausal: konstruierter Split soll Frequenzen vorgeben).
Seeds 10–13: Δ = +8, +7, +7, +7 (von max. 10); jeder Arm 3–4/5 aus der eigenen Zielmenge, 0 aus der anderen.
Grokking früh (500–1050 vs. 3525–5975, nicht vorab festgelegt). Entscheidung erst ab 8 Seeds.

**Vorbereitet, nicht ausgeführt:** EXP-014 (Split × Init gekreuzt, Nachtrag a), EXP-017 (RFM, keine Zufalls-Init),
EXP-013 (Lock-in-Kurve), EXP-011 (Normtausch), EXP-001/002 (Frequenzverbote).
**Teilweise:** EXP-010 (Init-Tausch): 1 von 10 Paaren (Seed 10, d = +1). EXP-003d: 8 von 10 Baselines.

## Nächste konkrete Aktionen (nur im Fenster 00:00–13:00 Berlin)

1. `python lab/tools/guarded_run.py --check`, dann `sh lab/experiments/queue_s4b.sh` im Hintergrund, beobachten.
2. Sobald EXP-016 ≥ 8 Seeds hat: `python lab/experiments/EXP-016-engineered-split/analyze.py`.
3. Nach Baselines 18/19: EXP-015/012 Phase 2 mit n = 10 nur **berichten** (die Entscheidung fiel vorab bei n = 8).
4. Nach den Kreuzpaaren: `EXP-014-split-vs-init/analyze.py`. Nach den Tauschläufen: `EXP-010-init-swap/analyze.py`.
5. EXP-017: `python lab/tools/guarded_run.py -- python lab/experiments/EXP-017-rfm-split/rfm.py --seeds 0-9 --iters 15`.
6. Außerhalb des Fensters: Literatur zu N3 vertiefen (Google Scholar), EXP-016-Folgefragen (Dosis ε, Beschleunigung
   des Grokkings durch konstruierte Splits als eigene Frage mit eigener Kontrolle) vorab festlegen.

## Blocker

- keine
