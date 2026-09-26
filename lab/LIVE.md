---
tags: [lab/live]
---
# LIVE: Laborsitzung 4

- **Sitzungsstart:** 2026-09-26 02:49 Berlin (00:49Z, vom Runner)
- **Deadline:** 2026-09-26 05:49 Berlin (03:49Z)
- **Zuletzt aktualisiert:** 05:16 Berlin
- **Run-Fenster:** offen (00:00–13:00 Berlin). Erste Sitzung mit Läufen.

## Gerade

**Lauf:** [[experiments/EXP-016-engineered-split/README|EXP-016]] (konstruierte Splits, je ≈ 4.5 min), Seed 10 Arm F seit 04:53. Diese Sitzung schafft voraussichtlich Seeds 10–14 (beide Arme); der Rest folgt in der nächsten Sitzung.
**Wichtigster Befund heute:** Das Masken-Spektrum des **Trainingssplits** sagt voraus, welche Frequenzen das Netz lernt (an frischen Seeds bestätigt, EXP-015). Ob der Split sie auch *verursacht*, prüft EXP-016 gerade; Seed 10 spricht dafür.

## Als Nächstes

Laufende EXP-016-Läufe beobachten. Ab ≈ 05:39 Stand sichern und Abschlussbericht schreiben (Deadline 05:49).

## Verlauf dieser Sitzung

- 05:15 EXP-016 Seed 12 Arm F: 4 von 5 aus der Zielmenge, gen 625 (Zufallssplit 3525).
- 05:11 EXP-016 Seed 11 Arm G: 3 von 5 aus G, 2 weitere direkt daneben (38/55 statt 39/56). Δ = +7.
- 05:06 EXP-016 Seed 11 Arm F: wieder 4 von 5 aus der Zielmenge, gen 775 (Zufallssplit 5975).
- 05:08 Codex-Angriff auf EXP-015: Wortlaut auf „sagt voraus“ korrigiert; exakter Test p = 2.5e-5; auch gegen die funktionalen Schlüsselfrequenzen der Studie hält der Befund (p = 3.6e-6).
- 05:02 EXP-016 Seed 10 Arm G: 4 von 5 Frequenzen aus **seiner** Zielmenge G, keine aus F. Δ = +8 von max. 10. Die Frequenzen folgen der Datenauswahl (1 Seed).
- 04:58 EXP-016 Seed 10 Arm F: generalisiert schon bei Schritt 525 (Zufallssplit: 3925); 4 von 5 Frequenzen aus der Zielmenge. Einzelwert, Kontrolle (Arm G) folgt.
- 04:53 **Bestätigt an frischen Seeds:** [[experiments/EXP-015-mask-spectrum/README|EXP-015]] (Split-Masken-Spektrum sagt Frequenzen voraus, r̄ 0.277, p < 1e-5; fremde Masken 0.499) und [[experiments/EXP-012-init-gradient/README|EXP-012]] (erster Gradient > Init, p = 0.031).
- 04:53 Baseline Seed 17 fertig (8 von 10). EXP-016-Smoke ok.
- 04:41 Baseline Seed 16 fertig: gen 7425 (7 von 10).
- 04:24 Baseline Seed 15 fertig: gen 5975 (6 von 10).
- 04:11 Baseline Seed 14 fertig: gen 11200, langsamer Seed (5 von 10).
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
