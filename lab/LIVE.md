---
tags: [lab/live]
---
# LIVE: Laborsitzung 38

- **Sitzungsstart:** 2026-09-28 05:19 Berlin (03:19Z, vom Runner)
- **Deadline:** 2026-09-28 08:19 Berlin (06:19Z)
- **Zuletzt aktualisiert:** 06:23 Berlin
- **Run-Fenster:** heute bis 18:00.

## Gerade

- GPU: **R2-Block** (13/300 fertig, 6 Worker) und **R7-Block** (14/36, 2 Worker).
- CPU: EXP-014 (4 Threads).
- Paper: P4/C3 als §3.11 geschrieben, unabhängige Prüfung läuft.

## Als Nächstes

R7 → `--analyze`; R2 → `--analyze`, C2, `R2_time.py`; dann R4 (≈ 1.6 h, evtl. nächste Sitzung).

## Verlauf dieser Sitzung

- 06:23 **P4 bestätigt** in allen drei Bedingungen (MLP, 4× Breite, Integer-Addition; je 15/15); **C3 bestätigt** (S = 0.30).
- 06:08 R3-Paperabschnitt geprüft (Zahlen richtig, Formulierungen vorsichtiger).
- 05:57 **R3 fertig:** Schrittuhr widerlegt (beide Zellen 0/20); Λ-Uhr registriert *nicht bestätigt* (doppelte Lernrate bestätigt, halbe nur in der Richtung).
- 05:43 **EXP-078:** Steuerung überträgt sich auf 2 Schichten (Δ_pow 5.84, 10/10); **R7 eingefroren** (n = 10), Block läuft.
- 05:28 **EXP-040 fertig:** *unklar* (registriert); die W_E-Init-Skala verschiebt das Festlegungsfenster nicht (3/4 Seeds) → gegen die Amplitudenschwelle.
- 05:26 Neue Idee N47 (Mediation der R5-Beschleunigung über frühes W_E-Signal); verwandte Arbeit Howe 2026 eingeordnet.
- 05:23 R5 §3.9 unabhängig geprüft: Zahlen richtig, 7 Formulierungen korrigiert. Post hoc: früher Zielanteil sagt Tempo innerhalb der E-Arme vorher (ρ ≈ −0.7).
- 05:21 R5 als §3.9 ins Paper (Prüfung läuft).
- 05:20 EXP-078 (GPU) und EXP-040/014 (CPU) gestartet.
