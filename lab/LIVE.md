---
tags: [lab/live]
---
# LIVE: Laborsitzung 4

- **Sitzungsstart:** 2026-09-26 02:49 Berlin (00:49Z, vom Runner)
- **Deadline:** 2026-09-26 05:49 Berlin (03:49Z)
- **Zuletzt aktualisiert:** 03:48 Berlin
- **Run-Fenster:** offen (00:00–13:00 Berlin). Erste Sitzung mit Läufen.

## Gerade

**Lauf:** Baseline Seed 14 (seit 03:47), ≈ 12 min pro Lauf; Baseline 17 voraussichtlich ≈ 04:35 fertig, danach EXP-016. Warteschlange `queue_s4b.sh`: Baselines 12–17 → [[experiments/EXP-016-engineered-split/README|EXP-016]] (je Seed 2 konstruierte Splits, 2000 Schritte) → Rest.
Codex-Review der Split-Linie ist eingearbeitet (Nachträge vor jedem Lauf).

## Als Nächstes

Sobald 8 Baselines fertig sind (10–17): Bestätigung EXP-015 und EXP-012 Phase 2 an frischen Seeds.

## Verlauf dieser Sitzung

- 03:47 Baseline Seed 13 fertig: gen 5275 (4 von 10).
- 03:40 [[experiments/EXP-017-rfm-split/README|EXP-017]] (RFM, keine Zufalls-Init) vorbereitet und getestet, nicht gelaufen.
- 03:35 Baseline Seed 12 fertig: gen 3525. Neuer Stand: 3 von 10 frischen Baselines.
- 03:28 Warteschlange umgestellt: Baselines 12–17, dann EXP-016 (nur Reihenfolge).
- 03:27 Baseline Seed 11 fertig: gen 5975.
- 03:26 Codex-Review Split-Linie: 4 Befunde übernommen. Test „fremde Masken“ an den Explorationsdaten: passend 0.31, fremd 0.51, p ≤ 5.5e-4. Der Effekt ist split-spezifisch.
- 03:19 Post hoc: Das Masken-Spektrum sagt die Frequenzen in allen 4 Architekturen voraus, auch bei der Two-hot-MLP, wo die Init nichts vorhersagt.
- 03:16 [[experiments/EXP-016-engineered-split/README|EXP-016]] vorab festgelegt: Splits konstruiert, die Zielfrequenzen im Masken-Spektrum hervorheben (offline 10/10 erfolgreich).
- 03:15 Post hoc: Token-Häufigkeiten erklären nichts (r̄ 0.50). Es zählt die Paarstruktur.
- 03:14 [[experiments/EXP-015-mask-spectrum/README|EXP-015]] Phase 1: Masken-Spektrum sagt K voraus (r̄ 0.307, p < 1e-5). Mechanismus-Check: M0 ~ echter Gradient (ρ 0.57).
- 03:14 EXP-010 Tausch Seed 10 fertig: gen 5175, d = +1 (1 S-Frequenz gewonnen).
- 03:12 Gradient-Vorschau: Das Spektrum des ersten Gradienten folgt dem Split (ρ 0.34), nicht der Init (−0.01). Warteschlange umgestellt (Baselines zuerst).
- 03:10 [[experiments/EXP-014-split-vs-init/README|EXP-014]] (Split vs. Init) vorab festgelegt.
- 03:07 [[experiments/EXP-013-lockin-curve/README|EXP-013]] vorbereitet und nach die Paar-Serie eingereiht.
- 03:06 [[experiments/EXP-012-init-gradient/README|EXP-012]] Phase 1: Der erste Gradient sagt die Frequenzen besser voraus als die Init (r̄ 0.30 vs. 0.375). Bestätigung an Seeds 10–19 steht aus.
- 03:05 Codex-Review EXP-010/011: 6 Befunde, 4 übernommen, 2 teilweise (Nachtrag a, vor jedem Ergebnis).
- 03:02 Baseline Seed 10 fertig: gen 3925. Die finalen Frequenzen stehen schon bei Schritt 250 fest, kaum nach Init-Leistung.
- 02:59 Literatur zu EXP-010/011 nachgesucht: kein kausaler Init-Tausch im Transformer-Embedding gefunden (vorläufig).
- 02:57 [[experiments/EXP-011-init-magswap/README|EXP-011]] (nur Normen tauschen) vorab festgelegt, Code und Test 9/9.
- 02:54 Paar-Läufe gestartet (`run_pairs.sh`, Seeds 10→19).
- 02:53 Smoke 300 Schritte: Tausch korrekt, 0.127 s/Schritt.
- 02:52 Studientests 24/24 PASS.
- 02:50 `test_freq_ban.py` 8/8 ok. Der Wächter funktioniert im Fenster.

- 02:50 Stand gelesen, kein STOP, keine Python-Prozesse, Wächter meldet Fenster offen (180 min Sitzungsbudget).
