---
tags: [lab/live]
---
# LIVE: Laborsitzung 4

- **Sitzungsstart:** 2026-09-26 02:49 Berlin (00:49Z, vom Runner)
- **Deadline:** 2026-09-26 05:49 Berlin (03:49Z)
- **Zuletzt aktualisiert:** 03:00 Berlin
- **Run-Fenster:** offen (00:00–13:00 Berlin). Erste Sitzung mit Läufen.

## Gerade

**Lauf:** EXP-003d-Baseline Seed 10, Schritt ~2000, Test-Acc 0.12 (noch Plateau), 0.127 s/Schritt.
**Codex** prüft EXP-010/011 (Design und Auswertung) im Hintergrund.

## Als Nächstes

Nach Seed 10: automatisch `init_swap` Seed 10. Codex-Befunde prüfen und protokollieren.

## Verlauf dieser Sitzung

- 02:59 Literatur zu EXP-010/011 nachgesucht: kein kausaler Init-Tausch im Transformer-Embedding gefunden (vorläufig).
- 02:57 [[experiments/EXP-011-init-magswap/README|EXP-011]] (nur Normen tauschen) vorab festgelegt, Code und Test 9/9.
- 02:54 Paar-Läufe gestartet (`run_pairs.sh`, Seeds 10→19).
- 02:53 Smoke 300 Schritte: Tausch korrekt, 0.127 s/Schritt.
- 02:52 Studientests 24/24 PASS.
- 02:50 `test_freq_ban.py` 8/8 ok. Der Wächter funktioniert im Fenster.

- 02:50 Stand gelesen, kein STOP, keine Python-Prozesse, Wächter meldet Fenster offen (180 min Sitzungsbudget).
