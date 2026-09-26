---
tags: [lab/live]
---
# LIVE: Laborsitzung 4

- **Sitzungsstart:** 2026-09-26 02:49 Berlin (00:49Z, vom Runner)
- **Deadline:** 2026-09-26 05:49 Berlin (03:49Z)
- **Zuletzt aktualisiert:** 03:08 Berlin
- **Run-Fenster:** offen (00:00–13:00 Berlin). Erste Sitzung mit Läufen.

## Gerade

**Lauf:** EXP-010 `init_swap` Seed 10, Schritt 2000, Test-Acc 0.18. Die frühen Top-5 (Schritt 250) sind fast dieselben wie in der Baseline: {7, 14, 20, 39, 41} gegen {7, 14, 19, 39, 41}. Der Tausch lenkt hier kaum um.

## Als Nächstes

Automatisch weiter mit Seed 11 (Baseline, dann Tausch) usw. Nach der Paar-Serie startet [[experiments/EXP-013-lockin-curve/README|EXP-013]] (Lock-in-Kurve, ≈ 7 min) automatisch.

## Verlauf dieser Sitzung

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
