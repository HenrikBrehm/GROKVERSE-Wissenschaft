---
tags: [lab/live]
---
# LIVE: Laborsitzung 4

- **Sitzungsstart:** 2026-09-26 02:49 Berlin (00:49Z, vom Runner)
- **Deadline:** 2026-09-26 05:49 Berlin (03:49Z)
- **Zuletzt aktualisiert:** 02:58 Berlin
- **Run-Fenster:** offen (00:00–13:00 Berlin). Erste Sitzung mit Läufen.

## Gerade

**Lauf:** EXP-003d-Baseline Seed 10 (Start 02:54, erwartet ≈ 15 min). Danach automatisch EXP-010 `init_swap` Seed 10, dann Seed 11 usw.
Nebenher: Vorbereitung EXP-011 (Betrag vs. Phase trennen).

## Als Nächstes

Fortschritt alle ~5–10 min prüfen. Nach jedem Paar ein kurzer Blick: Wandert die Frequenzwahl mit dem Tausch?

## Verlauf dieser Sitzung

- 02:54 Paar-Läufe gestartet (`run_pairs.sh`, Seeds 10→19).
- 02:53 Smoke 300 Schritte: Tausch korrekt, 0.127 s/Schritt.
- 02:52 Studientests 24/24 PASS.
- 02:50 `test_freq_ban.py` 8/8 ok. Der Wächter funktioniert im Fenster.

- 02:50 Stand gelesen, kein STOP, keine Python-Prozesse, Wächter meldet Fenster offen (180 min Sitzungsbudget).
